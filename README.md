# astrocore

A modular framework for **astrophysics time-series data ingestion, preprocessing, and model orchestration**.

The goal is to build a reproducible system that:
- ingests heterogeneous data sources
- standardizes and preprocesses inputs
- routes data through statistical / AI models
- enables consistent experimentation and analysis

```
astrocore/
├── astrocore/
│   ├── __init__.py
│   ├── module.py
│   ├── pipeline.py
|   ├── segmentation.py
│   └── io/
│       ├── __init__.py
│       ├── base.py
│       ├── local.py
│       ├── registry.py
│       └── remote.py
├── tests/
│   └── ...
├── LICENSE
└── README.md
```

## Design Principles

- **Modularity**: every component is isolated and reusable  
- **Determinism**: same input → same output  
- **Interface-first**: components follow strict contracts  
- **Separation of concerns**:
  - `io/` handles external data
  - `astrocore/` handles processing and orchestration  

---

## Current Scope

- Basic module abstraction  
- Pipeline execution system  
- Initial data ingestion layer (`io/`)
- Preparing the data for preprocessing methods (separating into continuous chunks, etc.)

---

## Example (conceptual)

```python
from astrocore.io.registry import Registry # Dataset pointers/reference to access local database
from astrocore.io.local import LocalFITS

import matplotlib.pyplot as plt

registry = Registry()

# Inspect available products
for row in registry.list_products():

    print(row)

# Select a product from database
product_id = 1

fits_path = registry.get_filepath(product_id)

print()
print("Selected file:")
print(fits_path)

# Load through astrocore abstraction
source = LocalFITS(fits_path)

lc = source.load()

# Quick visualization
plt.figure()

plt.scatter(
    lc["t"],
    lc["y"],
    s=1
)

plt.xlabel("TIME")
plt.ylabel("PDCSAP_FLUX")
plt.tight_layout()

plt.show()
```

## Notes

This repository is under active development.
Structure, naming, and interfaces are expected to evolve.
