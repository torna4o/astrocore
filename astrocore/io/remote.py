"""
Remote data ingestion utilities for TESS observations via MAST.

This module provides query and download interfaces built on top of
astroquery.mast (currently, for TESS). The architecture separates:

1. Observation discovery/querying
2. Product filtering
3. Product downloading

All query classes return standardized dictionaries intended for
pipeline-level orchestration inside astrocore.
"""

from .base import DataSource

from astroquery.mast import Observations
from astropy.coordinates import SkyCoord
import astropy.units as u

import requests
import time

class MastTESSQuery(DataSource):
    """
    Query interface for retrieving TESS observations and products
    from the MAST archive.

    Methods
    -------
    by_target(target_name)
        Query TESS observations by target identifier or object name.

    by_region(ra, dec, radius="0.02 deg")
        Query TESS observations around a sky position.
    """
    def by_target(self, target_name):
        """
        Query TESS observations by target name or identifier.

        Parameters
        ----------
        target_name : str
            Target name or identifier resolvable by MAST.

        Returns
        -------
        dict
            Dictionary containing:
            - obs : observation table
            - products : filtered product table
            - meta : query metadata and timing information

        Raises
        ------
        ValueError
            If no observations or downloadable products are found.
        """

        start = time.perf_counter()

        obs = Observations.query_criteria(
            target_name=target_name,
            obs_collection="TESS"
        )

        elapsed1 = time.perf_counter() - start

        if len(obs) == 0:

            raise ValueError(
                f"No TESS observations found for "
                f"target: {target_name}"
            )
        
        products = Observations.get_product_list(obs)

        products = products[
            products["productSubGroupDescription"] == "LC"
        ]

        mask = [
            str(name).endswith(".fits")
            for name in products["productFilename"]
        ]

        products = products[mask]

        if len(products) == 0:

            raise ValueError(
                f"No downloadable products found for "
                f"target: {target_name}"
            )

        elapsed2 = time.perf_counter() - start - elapsed1

        return {
            "obs": obs,
            "products": products,
            "meta": {
                "query_type": "target",
                "target_name": target_name,
                "elapsed_seconds": elapsed1 + elapsed2,
                "elapsed_query": elapsed1,
                "elapsed_filtering": elapsed2
            }
        }

    def by_region(self, ra, dec, radius="0.02 deg"):
        """
        Query TESS observations around a sky coordinate.

        Parameters
        ----------
        ra : float
            Right ascension in decimal degrees.

        dec : float
            Declination in decimal degrees.

        radius : str, optional
            Search radius accepted by astroquery/astropy,
            by default "0.02 deg".

        Returns
        -------
        dict
            Dictionary containing:
            - obs : filtered observation table
            - products : filtered product table
            - meta : query metadata and timing information

        Raises
        ------
        ValueError
            If no observations or downloadable products are found.
        """

        start = time.perf_counter()

        coord = SkyCoord(ra=ra, dec=dec, unit=(u.deg, u.deg))

        obs = Observations.query_region(
            coord,
            radius=radius,
        )

        elapsed1 = time.perf_counter() - start

        if len(obs) == 0:

            raise ValueError(
                f"No TESS observations found for "
                f"00.2 degree around: {ra}, {dec}"
            )
        
        tess_obs = obs[
            obs["obs_collection"] == "TESS"
        ]

        tess_obs = tess_obs[tess_obs["dataproduct_type"] == "timeseries"]

        products = Observations.get_product_list(tess_obs)

        products = products[
            products["productSubGroupDescription"] == "LC"
        ]

        mask = [
            str(name).endswith(".fits")
            for name in products["productFilename"]
        ]

        products = products[mask]

        if len(products) == 0:

            raise ValueError(
                f"No downloadable products found for "
                f"00.2 degree around: {ra}, {dec}"
            )

        products = Observations.filter_products(
            products,
            productType="SCIENCE",
            productSubGroupDescription="LC"
        )

        elapsed2 = time.perf_counter() - start - elapsed1

        return {
            "obs": tess_obs,
            "products": products,
            "meta": {
                "query_type": "region",
                "ra": ra,
                "dec": dec,
                "radius": radius,
                "elapsed_seconds": elapsed1 + elapsed2,
                "elapsed_query": elapsed1,
                "elapsed_filtering": elapsed2
            }
        }


class MastTESSDownload(DataSource):
    """
    Download interface for TESS products from MAST.
    """

    def __init__(self, download_dir="downloads"):
        """
        Parameters
        ----------
        download_dir : str, optional
            Local directory where downloaded products
            will be stored. A folder within the library 
            directory is used by default.
        """
        self.download_dir = download_dir

    def download(self, products):
        """
        Download selected MAST products.

        Parameters
        ----------
        products : astropy.table.Table
            Product table returned from query methods.

        Returns
        -------
        dict
            Dictionary containing:
            - manifest : download manifest table
            - meta : download metadata
        """

        manifest = Observations.download_products(
            products,
            download_dir=self.download_dir
        )

        return {
            "manifest": manifest,
            "meta": {
                "download_dir": self.download_dir
            }
        }
