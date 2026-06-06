# Cleaning and Feature Plan

Date: 2026-06-06

## Goal

Prepare a practical preprocessing plan for the Bank Marketing term deposit subscription prediction pipeline.

This plan is implementation-ready but does not train a model today.

## Target Encoding Plan

Source target column:

- `y`

Encoding:

| Source Value | Encoded Label |
| --- | --- |
| `yes` | `1` |
| `no` | `0` |

Planned output label column:

- `label`

## User ID Generation Plan

If the source dataset does not contain a stable customer identifier, generate `user_id` during preprocessing.

Format:

```text
client_000001
client_000002
client_000003
```

Rules:

- Generate IDs after loading the dataset.
- Keep IDs stable within one pipeline run.
- Use `user_id` for prediction output and API lookup.
- Treat `user_id` as potentially sensitive or linkable in real systems.

## Expected Categorical Columns

For `bank-full.csv` style data:

- `job`
- `marital`
- `education`
- `default`
- `housing`
- `loan`
- `contact`
- `month`
- `poutcome`

For `bank-additional-full.csv`, additional categorical fields may include:

- `day_of_week`

The final column list should be confirmed after loading the actual dataset.

## Expected Numeric Columns

For `bank-full.csv` style data:

- `age`
- `balance`
- `day`
- `duration`
- `campaign`
- `pdays`
- `previous`

For `bank-additional-full.csv`, additional numeric/economic fields may include:

- `emp.var.rate`
- `cons.price.idx`
- `cons.conf.idx`
- `euribor3m`
- `nr.employed`

The final column list should be confirmed after loading the actual dataset.

## Unknown and Missing Handling

Planned handling:

- Treat literal `unknown` as a valid categorical level at first.
- Report `unknown` counts per categorical column during EDA.
- Do not drop rows only because one categorical value is `unknown`.
- For null numeric values, consider median imputation if missing values exist.
- For null categorical values, fill with `unknown`.
- Keep `pdays = -1` as meaningful unless later analysis shows a better encoding is needed.

## Features to Keep or Drop

Keep for initial MVP:

- Demographic/client fields.
- Loan/default/housing indicators.
- Campaign/contact count fields.
- Previous campaign fields.

Review carefully:

- `duration`, because it may be leakage-prone if the prediction is meant to happen before the call outcome is known.

Drop from model features:

- `y`, after creating `label`.
- `user_id`, because it is an identifier, not a model feature.
- Any duplicate or raw-only helper columns created during preprocessing.

## PySpark Preprocessing Stages

Planned MVP pipeline:

1. Load CSV with Spark.
2. Generate `user_id` if needed.
3. Encode target `y` into `label`.
4. Fill missing categorical values with `unknown`.
5. Fill or validate numeric missing values.
6. Apply `StringIndexer` to categorical columns.
7. Apply `OneHotEncoder` to indexed categorical columns.
8. Combine numeric columns and encoded categorical vectors with `VectorAssembler`.
9. Train main model with `LogisticRegression`.
10. Evaluate model.
11. Generate prediction output table.

Later model options:

- `RandomForestClassifier`.
- `GBTClassifier`.
- `SparkXGBClassifier` as stretch/deferred only if setup is feasible.

SparkXGBClassifier should not block the MVP.

## Train and Evaluation Split Plan

Planned split:

- Train: 80%.
- Evaluation/test: 20%.
- Use deterministic seed.
- Consider stratification or class-weighting later if the target is strongly imbalanced.

## Evaluation Metrics

Planned metrics:

- Accuracy.
- Precision.
- Recall.
- F1.
- AUC, if a binary evaluator is available.

Also report:

- Target class distribution.
- Confusion matrix if practical.

## Prediction Output Schema

The PySpark scoring pipeline should produce:

| Field | Type | Description |
| --- | --- | --- |
| `user_id` | string | Generated or stable client identifier. |
| `prediction_score` | float | Probability-like score for term deposit subscription. |
| `prediction_label` | int | Predicted class using threshold, usually `0.5`. |
| `model_version` | string | Model version used for scoring. |
| `scored_at` | timestamp | Timestamp when scoring happened. |
| `source` | string | Source category such as `real`, `mock`, or `expanded`. |

This table is the data source for `GET /prediction/{user_id}` in the API project.
