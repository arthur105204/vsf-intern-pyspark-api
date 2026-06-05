# Dataset and Problem

## Dataset Choice

The project uses the Bank Marketing dataset. The dataset contains customer and campaign-related attributes from direct marketing campaigns by a banking institution.

## Why This Dataset Is Suitable

Bank Marketing is suitable because it supports a practical binary prediction problem with tabular data. It gives enough structure to practice PySpark data cleaning, categorical feature handling, numeric feature handling, model training, evaluation, and prediction output generation.

It also fits the project goal: predict whether a client is likely to subscribe to a term deposit, then serve that prediction through an API.

## Problem Framing

The problem is term deposit subscription propensity prediction.

For each client row, the pipeline predicts the likelihood that the client will subscribe to a term deposit.

## Target Column

- Source target: `y`
- Positive class: `yes`
- Negative class: `no`
- Target mapping:
  - `yes = 1`
  - `no = 0`

## Generated User ID Strategy

If the dataset does not provide a stable user or customer ID, the pipeline will generate one during processing.

Example format:

```text
client_000001
client_000002
client_000003
```

The generated ID is used for prediction lookup in the API. In a real system, this ID could be sensitive or linkable, so demo IDs should be synthetic or anonymized.

## Planned PySpark Pipeline

The planned PySpark pipeline should:

1. Load the Bank Marketing dataset.
2. Validate expected columns and target values.
3. Generate `user_id` if needed.
4. Map `y` to a binary label.
5. Clean and prepare numeric and categorical features.
6. Encode categorical features.
7. Assemble features for Spark MLlib.
8. Split data for training and evaluation.
9. Train baseline models.
10. Generate prediction output rows.

## Planned Model and Evaluation

Main model:

- Spark MLlib Logistic Regression.

Second model:

- Spark RandomForestClassifier or GBTClassifier.

Stretch goal:

- SparkXGBClassifier, only if setup is feasible.
- XGBoost must not block the MVP.

Planned evaluation should include practical binary classification metrics such as accuracy, precision, recall, F1, ROC AUC, and confusion matrix where appropriate.

## Prediction Output Schema

The PySpark pipeline should generate a prediction output table with this schema:

| Field | Type | Description |
| --- | --- | --- |
| `user_id` | string | Stable synthetic or generated client identifier. |
| `prediction_score` | float | Probability-like model score for term deposit subscription. |
| `prediction_label` | int | Predicted label, usually `1` for likely subscriber and `0` otherwise. |
| `model_version` | string | Version identifier for the model that produced the score. |
| `scored_at` | timestamp | Time when the row was scored. |
| `source` | string | Data source category, for example `real`, `mock`, or `expanded`. |

For API and load testing, the prediction output may be expanded or mocked to approximately 500k rows using the same schema. These rows must not be described as real raw training users unless they truly come from real source data.

## Limitations

- The Bank Marketing dataset may not contain stable customer IDs.
- Generated IDs are useful for the demo but are not equivalent to real customer identifiers.
- Model predictions are for learning and demonstration, not for real banking decisions.
- Dataset size may be smaller than the desired API load-test dataset, so expanded or mock prediction rows may be needed.
- Privacy and access-control assumptions must be documented before treating the API as production-like.
