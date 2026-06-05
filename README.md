# vsf-intern-pyspark-api

Production-inspired internship project for a PySpark data-to-prediction-serving pipeline.

The project uses the Bank Marketing dataset to predict term deposit subscription propensity, generates precomputed prediction output, and serves predictions through a lookup API.

## Current Phase

Documentation and scope only.

No pipeline code, notebooks, model training, or API implementation has been added yet.

## Repository Structure

```text
.
|-- README.md
|-- docs/
|   |-- README.md
|   |-- project/
|   |   `-- PROJECT_INTENT.md
|   |-- data/
|   |   `-- DATASET_AND_PROBLEM.md
|   |-- api/
|   |   |-- API_SCOPE.md
|   |   `-- API_DOCS.md
|   `-- reports/
|       |-- meetings/
|       `-- weekly/
|-- data/
|   |-- raw/
|   |-- interim/
|   |-- processed/
|   `-- predictions/
|-- src/
|   |-- pipeline/
|   `-- api/
`-- tests/
    |-- functional/
    `-- performance/
```

## Key Documents

- [Project intent](docs/project/PROJECT_INTENT.md)
- [Dataset and problem](docs/data/DATASET_AND_PROBLEM.md)
- [API scope](docs/api/API_SCOPE.md)
- [API docs](docs/api/API_DOCS.md)

## Notes

- The API MVP is lookup-based, not realtime model inference.
- Prediction output may be expanded or mocked for load testing, but mock rows must not be described as real raw training users.
- Do not commit raw sensitive data.
