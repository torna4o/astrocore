from .base import DataSource

import numpy as np
from astropy.io import fits


class LocalCSV(DataSource):

    def __init__(self, path):
        self.path = path

    def load(self):

        data = np.loadtxt(
            self.path,
            delimiter=","
        )

        return {
            "t": data[:, 0],
            "y": data[:, 1],
            "meta": {
                "source": "local_csv",
                "path": self.path
            }
        }

class LocalFITS(DataSource):
    # Class to load lightcurve FITS files downloaded from MAST
    def __init__(self, path):
        self.path = path

    def load(self):

        with fits.open(self.path) as hdul:

            table = hdul[1].data

            t = table["TIME"]
            y = table["PDCSAP_FLUX"]

        mask = np.isfinite(t) & np.isfinite(y)

        return {
            "t": t[mask],
            "y": y[mask],
            "meta": {
                "source": "local_fits",
                "path": self.path
            }
        }
