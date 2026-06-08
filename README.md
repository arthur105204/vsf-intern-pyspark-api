# vsf-intern-pyspark-api

Production-inspired internship project for a PySpark data-to-prediction-serving pipeline.

The project uses the Bank Marketing dataset to predict term deposit subscription propensity, generates precomputed prediction output, and serves predictions through a lookup API.

## Current Phase

MVP implementation and review artifacts.

Completed so far:

- Project scope and API documentation.
- Pandas EDA with 5 charts.
- PySpark preprocessing workflow.
- Spark MLlib Logistic Regression baseline.
- Logistic Regression threshold/class-weight comparison gate.
- FastAPI lookup MVP using precomputed mock serving data.

## Repository Structure

```text
.
|-- README.md
|-- api_project/
|   |-- app/
|   |-- data/
|   |-- reports/
|   |-- scripts/
|   `-- tests/
|-- docs/
|   |-- api/
|   |-- daily/
|   |-- data/
|   |-- mentor_materials/
|   |-- project/
|   `-- CODEBASE_WALKTHROUGH.md
`-- pyspark_project/
    |-- data/
    |   |-- raw/
    |   `-- processed/
    |-- reports/
    |   `-- figures/
    `-- scripts/
```

## Main Areas

- `pyspark_project/`: real Bank Marketing EDA, PySpark preprocessing, model training, model comparison reports.
- `api_project/`: FastAPI prediction lookup MVP, API tests, mock serving dataset.
- `docs/`: project intent, API docs, daily notes, codebase walkthrough, mentor-review materials.

## Key Documents

- [Project intent](docs/project/PROJECT_INTENT.md)
- [Dataset and problem](docs/data/DATASET_AND_PROBLEM.md)
- [API scope](docs/api/API_SCOPE.md)
- [API docs](docs/api/API_DOCS.md)
- [Pandas EDA report](pyspark_project/reports/PANDAS_EDA_REPORT.md)
- [PySpark preprocessing report](pyspark_project/reports/PYSPARK_PREPROCESSING_REPORT.md)
- [Logistic Regression report](pyspark_project/reports/LOGISTIC_REGRESSION_REPORT.md)
- [Model comparison report](pyspark_project/reports/MODEL_COMPARISON_REPORT.md)

## Notes

- The API MVP is lookup-based, not realtime model inference.
- `duration` is excluded from model features to avoid leakage.
- Mock 500k API data is for serving/load-test readiness, not model evaluation.
- Do not commit raw sensitive data or generated processed outputs.
