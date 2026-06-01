"""
Local dataset registry for astrocore.

This module provides a lightweight SQLite-backed registry used to
track downloaded datasets, metadata, provenance information, and
local file locations.

The registry acts as the local source of truth for scientific data
products after ingestion from external archives.
"""

import os
import sqlite3
from datetime import datetime

class Registry:
"""
Manage the local SQLite dataset registry.

```
Parameters
----------
db_path : str, optional
    Path to the SQLite database file.
"""

def __init__(self, db_path="datasets/registry.db"):
    self.db_path = db_path

def initialize(self):
    """
    Create the registry database and tables if they do not exist.
    """

    os.makedirs(
        os.path.dirname(self.db_path),
        exist_ok=True
    )

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        target_name TEXT,

        ra REAL,
        dec REAL,

        mission TEXT,
        category TEXT,

        product_type TEXT,
        sector TEXT,

        filepath TEXT,
        source TEXT,

        download_date TEXT
    )
    """)

    conn.commit()
    conn.close()

def register_product(
    self,
    target_name,
    ra,
    dec,
    mission,
    category,
    product_type,
    sector,
    filepath,
    source
):
    """
    Register a newly downloaded data product.

    Parameters
    ----------
    target_name : str
        Target identifier or object name.

    ra : float
        Right ascension in decimal degrees.

    dec : float
        Declination in decimal degrees.

    mission : str
        Mission or survey name.

    category : str
        User-defined scientific category.

    product_type : str
        Product type identifier.

    sector : str
        Mission sector, campaign, or equivalent.

    filepath : str
        Local path to the downloaded file.

    source : str
        Data source or archive name.
    """

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO products (

        target_name,

        ra,
        dec,

        mission,
        category,

        product_type,
        sector,

        filepath,

        source,

        download_date

    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (

        target_name,

        ra,
        dec,

        mission,
        category,

        product_type,
        sector,

        filepath,

        source,

        datetime.utcnow().isoformat()

    ))

    conn.commit()
    conn.close()

def list_products(self):
    """
    Return all registered products.

    Returns
    -------
    list[tuple]
        All database rows ordered by product ID.
    """

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM products
    ORDER BY id
    """)

    rows = cursor.fetchall()

    conn.close()

    return rows

def find_by_category(self, category):
    """
    Return products belonging to a given category.

    Parameters
    ----------
    category : str
        Category name to search for.

    Returns
    -------
    list[tuple]
        Matching database rows.
    """

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM products
    WHERE category = ?
    ORDER BY id
    """, (category,))

    rows = cursor.fetchall()

    conn.close()

    return rows

def find_by_target(self, target_name):
    """
    Return products associated with a target.

    Parameters
    ----------
    target_name : str
        Target identifier or object name.

    Returns
    -------
    list[tuple]
        Matching database rows.
    """

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT *
    FROM products
    WHERE target_name = ?
    ORDER BY id
    """, (target_name,))

    rows = cursor.fetchall()

    conn.close()

    return rows

def get_filepath(self, product_id):
    """
    Return the local filepath for a registered product.

    Parameters
    ----------
    product_id : int
        Registry product identifier.

    Returns
    -------
    str
        Local filepath.

    Raises
    ------
    ValueError
        If the product ID does not exist.
    """

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT filepath
    FROM products
    WHERE id = ?
    """, (product_id,))

    row = cursor.fetchone()

    conn.close()

    if row is None:
        raise ValueError(
            f"No product with id={product_id}"
        )

    return row[0]

def exists(self, filepath):
    """
    Check whether a filepath is already registered.

    Parameters
    ----------
    filepath : str
        Local file path.

    Returns
    -------
    bool
        True if the file exists in the registry,
        otherwise False.
    """

    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT COUNT(*)
    FROM products
    WHERE filepath = ?
    """, (filepath,))

    count = cursor.fetchone()[0]

    conn.close()

    return count > 0
