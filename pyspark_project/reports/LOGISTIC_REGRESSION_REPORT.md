# Logistic Regression Report

Date: 2026-06-08

## Status

Completed.

## Model

| Field | Value |
| --- | --- |
| Model | Spark MLlib LogisticRegression |
| Model version | `bank_marketing_lr_v1` |
| Seed | `20260608` |

## Feature Set Summary

Categorical features:

| Column |
| --- |
| job |
| marital |
| education |
| default |
| housing |
| loan |
| contact |
| month |
| poutcome |

Numeric features:

| Column |
| --- |
| age |
| balance |
| day |
| campaign |
| pdays |
| previous |

Leakage note:

- `duration` is excluded because call duration can leak information from after the customer interaction.
- This keeps the MVP closer to a production-like propensity prediction workflow.

## Train/Test Sizes

| Split | Rows |
| --- | --- |
| Train | `36263` |
| Test | `8948` |

## Metrics

| Metric | Value |
| --- | --- |
| Accuracy | 0.8941 |
| Precision | 0.7046 |
| Recall | 0.1863 |
| F1 | 0.2946 |
| AUC | 0.7800 |

Confusion matrix on test split:

|  | Predicted 0 | Predicted 1 |
| --- | --- | --- |
| Actual 0 | 7802 | 83 |
| Actual 1 | 865 | 198 |

## Class Imbalance Note

The positive class is only about 11.7% of the dataset. Accuracy alone is not enough because a model can achieve high accuracy by mostly predicting the majority `no` class. Precision, recall, F1, and AUC are reported to make the evaluation more honest.

## Prediction Output Schema

| Field | Type |
| --- | --- |
| user_id | string |
| prediction_score | float |
| prediction_label | int |
| model_version | string |
| scored_at | timestamp |
| source | string |

Output:

```text
pyspark_project\data\processed\predictions_lr.parquet
```

Output format:

```text
pandas_parquet_fallback
```

Output row count:

```text
45211
```

## Limitations

- This is a baseline model only.
- No hyperparameter tuning was performed.
- No class weighting was applied yet.
- Feature leakage around campaign timing should be reviewed further before treating results as production-ready.

## Next Model Options

- RandomForestClassifier.
- GBTClassifier.
- SparkXGBClassifier as stretch/deferred only; it should not block the MVP.

Generated at: `2026-06-08T03:06:02.552903+00:00`
