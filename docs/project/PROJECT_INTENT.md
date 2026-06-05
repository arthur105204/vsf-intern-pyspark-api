# Project Intent

## Why This Project Exists

`vsf-intern-pyspark-api` is a production-inspired learning project for building a data-to-prediction-serving pipeline. The goal is to practice a company-style workflow that connects data processing, model training, prediction generation, API serving, documentation, caching, testing, and privacy awareness.

This is not a toy PySpark script and not just a CRUD API. The project should simulate the shape of a real data product while staying small enough for internship learning.

## Production Workflow Simulated

The project simulates this workflow:

1. Load and prepare a structured dataset with PySpark.
2. Generate stable user identifiers when the source data does not provide them.
3. Train and evaluate baseline machine learning models with Spark MLlib.
4. Produce a prediction output table.
5. Serve precomputed prediction results through an API.
6. Add clear API documentation and test plans.
7. Add cache and performance testing later.
8. Document privacy and PII assumptions.

## In Scope

- Bank Marketing dataset.
- Term deposit subscription propensity prediction.
- Target column: `y`.
- Target mapping: `yes = 1`, `no = 0`.
- Generated `user_id` values such as `client_000001`, `client_000002`, etc. if no stable customer ID exists.
- PySpark data preparation and feature engineering.
- Main model: Spark MLlib Logistic Regression.
- Second model: Spark RandomForestClassifier or GBTClassifier.
- Stretch model: SparkXGBClassifier if setup is feasible.
- Precomputed prediction output table.
- Lookup API: `GET /prediction/{user_id}`.
- In-memory cache for repeated `user_id` lookups.
- Functional, load, and stress test planning.
- PII and privacy notes.

## Out of Scope

- Realtime model inference inside the API.
- Full production authentication and authorization implementation.
- Redis or distributed cache implementation for MVP.
- XGBoost as an MVP blocker.
- Claiming expanded or mock 500k-row prediction data as real raw training users.
- Committing raw sensitive data.
- Building notebooks, training models, or implementing the API in this documentation-only phase.

## High-Level Architecture

```text
Bank Marketing dataset
        |
        v
PySpark data preparation
        |
        v
Spark MLlib model training and evaluation
        |
        v
Prediction output table
        |
        v
Lookup API with in-memory cache
        |
        v
Client receives prediction by user_id
```

## MVP Success Criteria

- Dataset and problem framing are documented.
- Prediction output schema is defined.
- API scope is clear and lookup-based.
- API response and error contracts are documented.
- Cache behavior is explained at MVP level.
- Functional, load, and stress testing plans are documented.
- PII and privacy assumptions are documented.
- The project scope is ready for mentor review before implementation begins.
