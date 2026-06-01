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

---

## Example (conceptual)

```python
from astrocore.pipeline import run_pipeline
from astrocore.basic import Normalize
from io.local import LocalCSV

data = LocalCSV("data.csv").load()

pipeline = [
    Normalize(),
]

result = run_pipeline(pipeline, data["y"])
```

## Notes

This repository is under active development.
Structure, naming, and interfaces are expected to evolve.
