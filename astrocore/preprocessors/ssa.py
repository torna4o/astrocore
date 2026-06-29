from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from astrocore.preprocessing import Preprocessor
from astrocore.preprocessors.fft import FFT
from astrocore.utils.performance import measure_performance


# ============================================================
# DATA CLASSES
# ============================================================

@dataclass(slots=True)
class SSAComponent:
    """
    Represents a single reconstructed SSA component.
    """

    component_id: int

    time: np.ndarray
    flux: np.ndarray

    energy: float
    energy_fraction: float

    analyses: dict = field(default_factory=dict)


@dataclass(slots=True)
class SSAResult:
    """
    Complete Singular Spectrum Analysis result.
    """

    components: list[SSAComponent]

    eigenvalues: np.ndarray

    window: int

    rank: int

    metadata: dict = field(default_factory=dict)


# ============================================================
# SSA
# ============================================================

class SSA(Preprocessor):
    """
    Singular Spectrum Analysis.

    Parameters
    ----------
    window : int
        Embedding window length.

    analyses : list[str] or None
        Optional analyses to perform for every reconstructed
        component.

        Currently supported

        - "fft"
    """

    def __init__(
        self,
        window: int,
        analyses: list[str] | None = None
    ):

        self.window = window
        self.analyses = analyses or []

    # --------------------------------------------------------

    @staticmethod
    def _trajectory_matrix(
        y: np.ndarray,
        L: int
    ) -> np.ndarray:

        N = len(y)
        K = N - L + 1

        return np.array(
            [
                y[i:i + L]
                for i in range(K)
            ]
        ).T

    # --------------------------------------------------------

    @staticmethod
    def _reconstruct(
        U,
        S,
        VT,
        N
    ):

        rank = len(S)

        components = np.zeros((N, rank))

        for i in range(rank):

            elementary = S[i] * np.outer(
                U[:, i],
                VT[i]
            )

            rev = elementary[::-1]

            components[:, i] = [

                rev.diagonal(k).mean()

                for k in range(
                    -rev.shape[0] + 1,
                    rev.shape[1]
                )

            ]

        return components

    # --------------------------------------------------------

    def _analyze_component(
        self,
        component: SSAComponent
    ) -> None:
        """
        Run requested analyses on a single component.
        """

        if "fft" in self.analyses:

            fft = FFT()

            component.analyses["fft"] = fft.run(
                {
                    "t": component.time,
                    "y": component.flux
                }
            )

        #
        # Future
        #

        # if "wavelet" in self.analyses:
        #     ...

        # if "lomb_scargle" in self.analyses:
        #     ...

    # --------------------------------------------------------

    @measure_performance
    def run(
        self,
        lightcurve: dict
    ) -> SSAResult:

        t = np.asarray(lightcurve["t"])
        y = np.asarray(lightcurve["y"])

        L = self.window

        if L >= len(y):

            raise ValueError(
                "Window length must be smaller "
                "than light curve length."
            )

        X = self._trajectory_matrix(
            y,
            L
        )

        #
        # SVD
        #

        U, S, VT = np.linalg.svd(
            X,
            full_matrices=False
        )

        eigenvalues = S ** 2

        total_energy = eigenvalues.sum()

        reconstructed = self._reconstruct(
            U,
            S,
            VT,
            len(y)
        )

        components = []

        for i in range(len(S)):

            component = SSAComponent(

                component_id=i,

                time=t,

                flux=reconstructed[:, i],

                energy=float(eigenvalues[i]),

                energy_fraction=float(
                    eigenvalues[i] / total_energy
                )

            )

            self._analyze_component(component)

            components.append(component)

        return SSAResult(

            components=components,

            eigenvalues=eigenvalues,

            window=L,

            rank=len(S),

            metadata={

                "method": "SSA",

                "window": L,

                "total_energy": float(
                    total_energy
                )

            }

        )
