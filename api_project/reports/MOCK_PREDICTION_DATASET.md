# Mock Prediction Dataset

Date: 2026-06-06

## Status

Generated successfully.

Output file:

```text
api_project/data/mock_predictions_500k.parquet
```

## Purpose

This dataset is mock serving data for API lookup and performance testing. It is not real raw training data and must not be described as 500k real Bank Marketing users.

The API will use this table to support:

```http
GET /prediction/{user_id}
```

The API should look up one row by `user_id` and return the precomputed prediction result.

## Generation Summary

| Item | Value |
| --- | --- |
| Row count | `500,000` |
| Seed | `20260606` |
| Output format | Parquet |
| Model version | `bank_marketing_mock_v1` |
| Score source | Synthetic beta distribution |
| Label threshold | `prediction_score >= 0.5` |
| Source value | `mock` |

## Schema

| Field | Type | Description |
| --- | --- | --- |
| `user_id` | string | Synthetic lookup ID, from `client_000001` to `client_500000`. |
| `prediction_score` | float | Mock score between 0 and 1. |
| `prediction_label` | int | `1` when score is at least `0.5`, otherwise `0`. |
| `model_version` | string | Mock model version. |
| `scored_at` | timestamp | Fixed scoring timestamp for the generated dataset. |
| `source` | string | Always `mock`. |

Observed Pandas dtypes:

```text
user_id                             str
prediction_score                float32
prediction_label                   int8
model_version                       str
scored_at           datetime64[us, UTC]
source                              str
```

## Sample Rows

| user_id | prediction_score | prediction_label | model_version | scored_at | source |
| --- | --- | --- | --- | --- | --- |
| `client_000001` | `0.108209` | `0` | `bank_marketing_mock_v1` | `2026-06-06 09:00:00+00:00` | `mock` |
| `client_000002` | `0.279601` | `0` | `bank_marketing_mock_v1` | `2026-06-06 09:00:00+00:00` | `mock` |
| `client_000003` | `0.111486` | `0` | `bank_marketing_mock_v1` | `2026-06-06 09:00:00+00:00` | `mock` |
| `client_000004` | `0.265283` | `0` | `bank_marketing_mock_v1` | `2026-06-06 09:00:00+00:00` | `mock` |
| `client_000005` | `0.301612` | `0` | `bank_marketing_mock_v1` | `2026-06-06 09:00:00+00:00` | `mock` |

## Score Distribution Summary

| Metric | Value |
| --- | --- |
| Count | `500,000` |
| Mean | `0.285960` |
| Std | `0.159892` |
| Min | `0.000391` |
| P50 | `0.264726` |
| P95 | `0.582376` |
| P99 | `0.705019` |
| Max | `0.951642` |

Label counts:

| prediction_label | Count |
| --- | --- |
| `0` | `445,061` |
| `1` | `54,939` |

## API Usage

The future lookup API should:

1. Load or access this prediction output table.
2. Receive `GET /prediction/{user_id}`.
3. Search by `user_id`.
4. Return the precomputed prediction fields plus request metadata.
5. Use cache later for repeated `user_id` lookups.

Example lookup ID:

```text
client_000001
```

## Important Caveat

This file is only for API/load testing readiness. It does not replace the real model scoring output that should be produced by the PySpark pipeline later.
