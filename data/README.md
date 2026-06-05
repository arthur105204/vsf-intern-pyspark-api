# Data Directory

This directory is reserved for dataset and pipeline outputs.

## Structure

| Path | Purpose |
| --- | --- |
| `raw/` | Original downloaded dataset files. Do not commit raw sensitive data. |
| `interim/` | Temporary intermediate outputs during PySpark processing. |
| `processed/` | Cleaned and feature-ready datasets. |
| `predictions/` | Precomputed prediction output used by the lookup API. |

For API and performance testing, prediction output may be expanded or mocked to approximately 500k rows. Mock or expanded rows must use the same schema and must be labeled with an appropriate `source` value.
