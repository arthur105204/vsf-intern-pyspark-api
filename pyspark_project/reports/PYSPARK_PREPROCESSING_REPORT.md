# PySpark Preprocessing Report

Date: 2026-06-08

## Status

Completed.

## Input Dataset

```text
pyspark_project\data\raw\bank_marketing\bank-full.csv
```

Read options:

```text
header=true
sep=;
inferSchema=true
```

## Dataset Shape

| Metric | Value |
| --- | --- |
| Row count | `45211` |
| Column count after `user_id` and `label` | `19` |

## Target Distribution

| Target | Count |
| --- | --- |
| no | 39922 |
| yes | 5289 |

## Feature Columns

Categorical columns:

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

Numeric columns:

| Column |
| --- |
| age |
| balance |
| day |
| campaign |
| pdays |
| previous |

## Excluded Columns

| Column | Reason |
| --- | --- |
| y | target column; encoded into label |
| duration | excluded by default because call duration may leak post-contact outcome information |
| user_id | identifier for serving lookup, not a model feature |

`duration` is intentionally excluded from the main feature set because it can introduce leakage in a production-like propensity prediction setting. A real pre-call scoring workflow should not depend on information known only after the customer interaction.

## Preprocessing Stages

| Stage |
| --- |
| StringIndexer(handleInvalid='keep') for `job` |
| StringIndexer(handleInvalid='keep') for `marital` |
| StringIndexer(handleInvalid='keep') for `education` |
| StringIndexer(handleInvalid='keep') for `default` |
| StringIndexer(handleInvalid='keep') for `housing` |
| StringIndexer(handleInvalid='keep') for `loan` |
| StringIndexer(handleInvalid='keep') for `contact` |
| StringIndexer(handleInvalid='keep') for `month` |
| StringIndexer(handleInvalid='keep') for `poutcome` |
| OneHotEncoder(handleInvalid='keep') for indexed categorical columns |
| VectorAssembler(handleInvalid='keep') for numeric + encoded categorical features |

Fitted feature vector size:

```text
59
```

## Train/Test Split

Deterministic seed:

```text
20260608
```

Split plan:

```text
train=80%
test=20%
```

| Split | Rows |
| --- | --- |
| Train | `36263` |
| Test | `8948` |

## Spark Actions Used

Spark uses lazy evaluation, so transformations are not executed until actions run.

Actions used in this preprocessing verification:

- `count()` for full dataset, train split, and test split.
- `collect()` for target distribution.
- `first()` after pipeline transformation to verify the feature vector exists.

## Notes

- `user_id` is generated as `client_000001`, `client_000002`, etc.
- `label` is encoded as `1.0` for `yes` and `0.0` for `no`.
- `handleInvalid='keep'` is used to reduce crashes on invalid or unseen categories.
- This script verifies preprocessing only; it does not train a model.

Generated at: `2026-06-08T03:03:32.075892+00:00`
