import numpy as np


class WCorrelation:
    """
    Weighted correlation matrix for SSA components.

    This measures similarity between reconstructed components
    using SSA weighting scheme.

    Reference concept:
    https://jds-online.org/journal/JDS/article/1027/file/pdf
    (W-correlation section)
    """

    def __init__(self, window: int):
        self.window = window

    # --------------------------------------------------------

    def _weights(self, L: int, K: int) -> np.ndarray:
        """
        SSA diagonal averaging weights.
        """

        return np.array(
            list(range(1, L + 1))
            + [L] * (K - L - 1)
            + list(range(1, L + 1))[::-1]
        )

    # --------------------------------------------------------

    def _w_inner(
        self,
        w: np.ndarray,
        x: np.ndarray,
        y: np.ndarray
    ) -> float:

        return float(np.sum(w * x * y))

    # --------------------------------------------------------

    def compute(
        self,
        components: np.ndarray
    ) -> np.ndarray:
        """
        Compute W-correlation matrix.

        Parameters
        ----------
        components : np.ndarray
            Shape (N, d)
            SSA reconstructed components

        Returns
        -------
        W_corr : np.ndarray
            Shape (d, d)
        """

        N, d = components.shape

        L = self.window
        K = N - L + 1

        w = self._weights(L, K)

        W = np.zeros((d, d))

        norms = np.zeros(d)

        # compute self-norms
        for i in range(d):

            norms[i] = self._w_inner(
                w,
                components[:, i],
                components[:, i]
            )

        norms = np.sqrt(norms)

        # W-correlation matrix
        for i in range(d):

            for j in range(i, d):

                num = self._w_inner(
                    w,
                    components[:, i],
                    components[:, j]
                )

                denom = norms[i] * norms[j] + 1e-12

                W[i, j] = abs(num / denom)
                W[j, i] = W[i, j]

        return W
