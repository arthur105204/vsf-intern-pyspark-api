# Codebase Walkthrough

Date: 2026-06-08

This report is a quick mentor-review briefing for `vsf-intern-spark-api`. It explains what the repo does, where important code lives, how the data/model/API flow works, what has been validated, and what caveats remain.

## 1. Project Purpose

This repo builds a production-inspired data-to-prediction-serving pipeline for the Bank Marketing dataset.

The prediction problem is term deposit subscription propensity:

- Dataset: Bank Marketing.
- Target: `y`.
- Positive class: `yes`.
- Negative class: `no`.
- Encoded label: `yes = 1`, `no = 0`.

The production pattern it simulates is:

```text
raw dataset
-> exploratory analysis
-> PySpark preprocessing
-> model training/evaluation
-> prediction output table
-> lookup API serving precomputed predictions
-> API cache/tests/docs
```

In scope:

- Pandas EDA and charts.
- PySpark preprocessing.
- Spark MLlib Logistic Regression.
- Threshold tuning and class-weighted Logistic Regression comparison.
- One modest tree-based Spark MLlib comparison model.
- Prediction output schema.
- FastAPI lookup API.
- Mock 500k serving dataset for API lookup/cache/load-test readiness.
- API docs and basic tests.

Out of scope for the current MVP:

- Realtime model inference inside the API.
- Redis or distributed cache.
- Docker/Kubernetes/MLOps.
- SparkXGBClassifier.
- UI.
- Load/stress/performance testing results.
- Treating mock 500k rows as real training users.

## 2. Folder Structure

| Folder | What it contains | Why it exists | Reviewer should look at first |
| --- | --- | --- | --- |
| `pyspark_project/` | PySpark data, scripts, reports, EDA figures. | Owns real dataset processing and model work. | `pyspark_project/reports/` for results, then `pyspark_project/scripts/`. |
| `pyspark_project/scripts/` | EDA, shared pipeline utilities, preprocessing, training, model comparison scripts. | Keeps data/model execution code separate from API serving code. | `pipeline_utils.py`, then `preprocess_pyspark.py`, `train_logistic_regression.py`, `model_comparison.py`. |
| `pyspark_project/reports/` | EDA report, preprocessing report, LR report, model comparison report, figures. | Mentor-review evidence for each modeling phase. | `MODEL_COMPARISON_REPORT.md` and `LOGISTIC_REGRESSION_REPORT.md`. |
| `api_project/` | API app, mock serving data, mock data generator, reports, tests. | Owns lookup-serving MVP. | `api_project/app/main.py`, `api_project/tests/test_prediction_api.py`. |
| `api_project/app/` | FastAPI app, repository, cache, schemas. | Implements lookup API over precomputed prediction rows. | `main.py`, then `repository.py`, `cache.py`, `schemas.py`. |
| `api_project/scripts/` | Mock prediction data generation script. | Generates 500k serving rows for API/load-test readiness. | `generate_mock_predictions.py`. |
| `api_project/tests/` | API tests. | Verifies health endpoint, lookup success, missing-user behavior, metadata. | `test_prediction_api.py`. |
| `api_project/reports/` | Mock prediction dataset documentation. | Documents what mock data is and is not. | `MOCK_PREDICTION_DATASET.md`. |
| `docs/` | Project docs, API docs, daily notes, mentor materials. | Mentor-facing documentation and planning history. | `CODEBASE_WALKTHROUGH.md`, `docs/api/API_DOCS.md`. |
| `docs/api/` | API scope and API docs. | Documents API contract and run/test instructions. | `API_DOCS.md`. |
| `docs/daily/` | Daily progress notes. | Tracks tasks, commands, blockers, milestone status. | `2026-06-08.md`. |

## 3. End-to-End Data/Model/API Flow

1. Raw Bank Marketing dataset is expected at:

   ```text
   pyspark_project/data/raw/bank_marketing/bank-full.csv
   ```

   The delimiter is `;`.

2. Pandas EDA is run with:

   ```powershell
   & 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\run_pandas_eda.py
   ```

   It loads the CSV, computes summaries, and writes exactly 5 charts under:

   ```text
   pyspark_project/reports/figures/
   ```

3. PySpark preprocessing is run with:

   ```powershell
   & 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\preprocess_pyspark.py
   ```

   It loads the real dataset, generates `user_id`, encodes `label`, excludes `duration`, builds Spark ML preprocessing stages, splits train/test, and writes:

   ```text
   pyspark_project/reports/PYSPARK_PREPROCESSING_REPORT.md
   ```

4. Logistic Regression training is run with:

   ```powershell
   & 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\train_logistic_regression.py
   ```

   It trains Spark MLlib Logistic Regression on the real train split, evaluates on test split, writes metrics, and generates real model predictions at:

   ```text
   pyspark_project/data/processed/predictions_lr.parquet
   ```

   This processed output is generated locally and should not be committed.

5. Model comparison is run with:

   ```powershell
   & 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\model_comparison.py
   ```

   It evaluates:

   - Baseline Logistic Regression threshold table.
   - Class-weighted Logistic Regression threshold table.
   - GBTClassifier with modest parameters.

   It writes:

   ```text
   pyspark_project/reports/MODEL_COMPARISON_REPORT.md
   pyspark_project/reports/model_comparison_metrics.json
   ```

6. Mock 500k prediction data is generated with:

   ```powershell
   & 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' api_project\scripts\generate_mock_predictions.py
   ```

   It writes:

   ```text
   api_project/data/mock_predictions_500k.parquet
   ```

7. FastAPI reads prediction data from:

   ```text
   api_project/data/mock_predictions_500k.parquet
   ```

   The API currently serves mock prediction rows, not real Logistic Regression predictions.

8. `/prediction/{user_id}` works by:

   - Creating request metadata.
   - Checking in-memory cache by `user_id`.
   - If missing in cache, checking repository dictionary.
   - Returning a prediction response for existing users.
   - Returning 404 `USER_NOT_FOUND` for missing users.

9. Cache is implemented as a simple in-memory LRU-style cache in `api_project/app/cache.py`.

10. API tests verify:

   - `/health` returns 200 and record count.
   - Existing user returns prediction response.
   - Missing user returns 404.
   - Metadata exists.
   - Repeated request does not fail.

## 4. Important Files Table

| File | Purpose | Inputs | Outputs | How to run / how it is used | Important concepts |
| --- | --- | --- | --- | --- | --- |
| `pyspark_project/scripts/run_pandas_eda.py` | Runs Pandas EDA and creates charts. | `bank-full.csv` with `sep=";"`. | 5 PNG charts, printed JSON summary. | Run directly with Python. | EDA, target distribution, unknown values, cardinality, chart generation. |
| `pyspark_project/scripts/pipeline_utils.py` | Shared PySpark data/preprocessing utilities. | Raw Bank Marketing CSV. | Spark DataFrames and preprocessing `Pipeline`. | Imported by preprocessing/training/comparison scripts. | `user_id`, `label`, `duration` exclusion, StringIndexer, OneHotEncoder, VectorAssembler. |
| `pyspark_project/scripts/preprocess_pyspark.py` | Verifies PySpark preprocessing workflow. | Real dataset via `pipeline_utils.py`. | `PYSPARK_PREPROCESSING_REPORT.md`. | Run directly with Python. | Spark lazy evaluation, train/test split, feature vector size. |
| `pyspark_project/scripts/train_logistic_regression.py` | Trains/evaluates baseline Logistic Regression. | Real train/test split. | `LOGISTIC_REGRESSION_REPORT.md`, local `predictions_lr.parquet`. | Run directly with Python. | LogisticRegression, AUC, confusion matrix, pandas Parquet fallback on Windows. |
| `pyspark_project/scripts/model_comparison.py` | Runs recall-improvement gate. | Real train/test split. | `MODEL_COMPARISON_REPORT.md`, `model_comparison_metrics.json`. | Run directly with Python. | Threshold tuning, class weights, GBT comparison, precision/recall trade-off. |
| `api_project/scripts/generate_mock_predictions.py` | Generates 500k mock serving rows. | Synthetic random scores. | `mock_predictions_500k.parquet` or CSV fallback. | Run directly with Python. | Deterministic seed, mock serving data, schema contract. |
| `api_project/app/main.py` | FastAPI application. | Repository/cache modules. | `/health`, `/prediction/{user_id}`, `/metadata`. | Run with Uvicorn. | Lifespan startup, metadata, error handling. |
| `api_project/app/repository.py` | Loads prediction data and builds lookup dictionary. | `api_project/data/mock_predictions_500k.parquet`. | In-memory `dict[user_id, record]`. | Used by `main.py`. | Parquet read with pandas, dictionary lookup. |
| `api_project/app/cache.py` | Simple in-memory cache. | `user_id` lookup keys. | Cached prediction records, hit/miss counters. | Used by `main.py`. | LRU-style OrderedDict, cache metrics. |
| `api_project/app/schemas.py` | Pydantic response models. | API response fields. | Typed response schemas. | Used by FastAPI route declarations. | PredictionResponse, ErrorResponse, HealthResponse. |
| `api_project/tests/test_prediction_api.py` | API test suite. | FastAPI `TestClient`. | Test pass/fail results. | `python -m pytest api_project\tests -q`. | Health, success lookup, missing lookup, metadata, repeated lookup. |
| `docs/api/API_DOCS.md` | Practical API documentation. | API contract and examples. | Reviewer-facing API docs. | Read by mentor/developer. | Endpoint contract, responses, cache, run/test commands. |
| `docs/api/API_SCOPE.md` | API scope and boundaries. | Project/API decisions. | Scope definition. | Read before implementing API changes. | Lookup API, mock data source, out-of-scope items. |
| `pyspark_project/reports/MODEL_COMPARISON_REPORT.md` | Model comparison evidence. | `model_comparison.py` outputs. | Threshold/class-weight/tree comparison. | Read by mentor. | LR threshold 0.2 recommendation, mock data not used for metrics. |
| `pyspark_project/reports/LOGISTIC_REGRESSION_REPORT.md` | Baseline LR report. | `train_logistic_regression.py` outputs. | Baseline metrics and prediction output path. | Read by mentor. | Accuracy vs recall, AUC, class imbalance. |
| `pyspark_project/reports/PYSPARK_PREPROCESSING_REPORT.md` | Preprocessing report. | `preprocess_pyspark.py` outputs. | Dataset shape, stages, split sizes. | Read by mentor. | `duration` exclusion, Spark actions, feature vector. |
| `api_project/reports/MOCK_PREDICTION_DATASET.md` | Mock data documentation. | Mock Parquet dataset. | Row count, schema, sample rows, caveat. | Read by mentor/API reviewer. | Mock data is serving/test data, not training/evaluation data. |

## 5. Mock Data Generation

500k mock prediction rows are generated in:

```text
api_project/scripts/generate_mock_predictions.py
```

Run command:

```powershell
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' api_project\scripts\generate_mock_predictions.py
```

Output path:

```text
api_project/data/mock_predictions_500k.parquet
```

Row count:

```text
500,000
```

Schema:

| Field | Meaning |
| --- | --- |
| `user_id` | Synthetic lookup ID. |
| `prediction_score` | Synthetic float score between 0 and 1. |
| `prediction_label` | `1` if score >= 0.5, else `0`. |
| `model_version` | Fixed mock version string. |
| `scored_at` | Fixed timestamp for generated mock rows. |
| `source` | `mock`, to avoid confusing with real model output. |

Generation details:

- `user_id` is generated as `client_000001`, `client_000002`, ..., `client_500000`.
- `prediction_score` is generated from NumPy beta distribution: `rng.beta(a=2.0, b=5.0, size=500000)`.
- `prediction_label` uses threshold `0.5`.
- `model_version` is `bank_marketing_mock_v1`.
- `scored_at` is `2026-06-06T09:00:00Z`.
- `source` is `mock`.
- Deterministic seed is used: `20260606`.

Important:

- Mock 500k data is not real training data.
- Mock 500k data is not used to compute Logistic Regression metrics.
- Mock 500k data is for API lookup/cache/load/stress/performance testing.
- Real model evaluation uses only the real Bank Marketing train/test split.

## 6. API Flow

The FastAPI app is defined in:

```text
api_project/app/main.py
```

Startup:

- `main.py` creates global `PredictionRepository` and `InMemoryCache`.
- FastAPI lifespan calls `repository.load()` at startup.

Prediction loading:

- `api_project/app/repository.py` reads:

  ```text
  api_project/data/mock_predictions_500k.parquet
  ```

- It uses pandas `read_parquet`.
- It converts rows into an in-memory dictionary keyed by `user_id`.
- Lookup uses dictionary access, not Spark and not realtime model inference.

`GET /health` returns:

- `status`
- `record_count`
- `cache_size`
- `cache_hits`
- `cache_misses`

`GET /prediction/{user_id}` for existing user returns:

- `user_id`
- `prediction_score`
- `prediction_label`
- `model_version`
- `scored_at`
- `request_id`
- `trace_id`
- `timestamp`

For missing user it returns HTTP 404:

- `error = USER_NOT_FOUND`
- `message = No prediction found for user_id=...`
- `request_id`
- `trace_id`
- `timestamp`

Metadata is created in `metadata()` inside `api_project/app/main.py`:

- `request_id`: `req_` plus UUID fragment.
- `trace_id`: `trace_` plus UUID.
- `timestamp`: current UTC ISO timestamp.

Cache is implemented in:

```text
api_project/app/cache.py
```

It is a simple in-memory LRU-style cache with:

- max size: `10,000`
- `hits`
- `misses`
- `size`

So the cache is both MVP functional and has basic hit/miss metrics exposed through `/health`.

## 7. Tests and Validation

Tests live in:

```text
api_project/tests/test_prediction_api.py
```

Current tests verify:

- `/health` returns 200.
- `/health` reports `record_count = 500000`.
- Existing user `client_000001` returns 200 and correct fields.
- Missing user `client_missing` returns 404.
- Responses include request metadata.
- Repeated lookup works.

Run API tests:

```powershell
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest api_project\tests -q
```

Generic command if Python is on PATH:

```powershell
python -m pytest api_project\tests -q
```

Static compile commands used in previous gates:

```powershell
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile pyspark_project\scripts\pipeline_utils.py pyspark_project\scripts\preprocess_pyspark.py pyspark_project\scripts\train_logistic_regression.py api_project\app\main.py api_project\app\repository.py api_project\app\cache.py api_project\app\schemas.py api_project\tests\test_prediction_api.py

& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m py_compile pyspark_project\scripts\model_comparison.py
```

Run commands:

```powershell
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\run_pandas_eda.py
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\preprocess_pyspark.py
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\train_logistic_regression.py
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' pyspark_project\scripts\model_comparison.py
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' api_project\scripts\generate_mock_predictions.py
```

API run command:

```powershell
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m uvicorn api_project.app.main:app --host 127.0.0.1 --port 8000
```

Coverage gap:

- Tests currently cover the API only.
- PySpark scripts are validated by running scripts and generating reports, not by automated unit tests.
- No automated test currently asserts model metrics or preprocessing schema.
- No load/stress/performance tests yet.

## 8. Current Metrics and Interpretation

Dataset:

- Shape: 45,211 rows, 17 columns.
- Target: `y`.
- Positive class: about 11.7%.
- `duration` excluded for leakage risk.

Baseline Logistic Regression, threshold 0.5:

| Metric | Value |
| --- | --- |
| Accuracy | 0.8941 |
| Precision | 0.7046 |
| Recall | 0.1863 |
| F1 | 0.2946 |
| AUC | 0.7800 |

Logistic Regression, threshold 0.2:

| Metric | Value |
| --- | --- |
| Accuracy | 0.8801 |
| Precision | 0.4949 |
| Recall | 0.4591 |
| F1 | 0.4763 |
| AUC | 0.7800 |

Weighted Logistic Regression:

| Variant | Threshold | Accuracy | Precision | Recall | F1 | AUC |
| --- | --- | --- | --- | --- | --- | --- |
| Weighted LR default | 0.50 | 0.7545 | 0.2746 | 0.6500 | 0.3861 | 0.7798 |
| Weighted LR best F1 | 0.60 | 0.8567 | 0.4163 | 0.5127 | 0.4595 | 0.7798 |

GBTClassifier:

| Metric | Value |
| --- | --- |
| Accuracy | 0.8932 |
| Precision | 0.6890 |
| Recall | 0.1834 |
| F1 | 0.2897 |
| AUC | 0.7940 |

Current recommendation:

```text
Logistic Regression with threshold 0.20
```

Why recall was low:

- The dataset is imbalanced.
- Default threshold 0.5 predicts relatively few positive `yes` cases.
- This keeps precision high but misses many true positives.

Why AUC stays the same when threshold changes:

- AUC measures ranking quality across thresholds.
- Changing the threshold changes final class labels and confusion-matrix metrics like precision/recall/F1.
- It does not change the underlying score ranking from the same trained model, so AUC remains the same for threshold-only changes.

## 9. DoD / Milestone Status

| Milestone | Evidence files | Commands / validation | Status | Caveats |
| --- | --- | --- | --- | --- |
| M6 PySpark preprocessing completed | `preprocess_pyspark.py`, `pipeline_utils.py`, `PYSPARK_PREPROCESSING_REPORT.md` | `python ... preprocess_pyspark.py`; row count 45,211; train/test 36,263/8,948; feature vector size 59 | Done | Spark Windows warnings about `winutils.exe`; `user_id` generation uses a global window, okay for MVP but not ideal for huge data. |
| M7 API MVP completed | `api_project/app/*.py`, `test_prediction_api.py`, `API_DOCS.md` | `python -m pytest api_project\tests -q`; 4 tests passed | Done | API serves mock 500k rows, not real LR output. |
| M8 Basic model trained | `train_logistic_regression.py`, `LOGISTIC_REGRESSION_REPORT.md` | `python ... train_logistic_regression.py`; metrics generated; prediction output generated | Done | Spark writer falls back to pandas + pyarrow Parquet on Windows. |
| Modeling improvement gate | `model_comparison.py`, `MODEL_COMPARISON_REPORT.md`, `model_comparison_metrics.json` | `python ... model_comparison.py`; threshold/weighted/tree comparison generated | Done | It is a modest comparison gate, not full hyperparameter tuning. |

## 10. How to Run Locally

Use the bundled Python path used during development:

```powershell
$PY = 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
```

Install dependencies:

```powershell
& $PY -m pip install pandas numpy pyarrow pillow pyspark fastapi uvicorn httpx pytest
```

Verify dataset exists:

```powershell
Test-Path pyspark_project\data\raw\bank_marketing\bank-full.csv
```

Run Pandas EDA:

```powershell
& $PY pyspark_project\scripts\run_pandas_eda.py
```

Run PySpark preprocessing:

```powershell
& $PY pyspark_project\scripts\preprocess_pyspark.py
```

Train Logistic Regression:

```powershell
& $PY pyspark_project\scripts\train_logistic_regression.py
```

Run model comparison:

```powershell
& $PY pyspark_project\scripts\model_comparison.py
```

Generate mock predictions:

```powershell
& $PY api_project\scripts\generate_mock_predictions.py
```

Run API:

```powershell
& $PY -m uvicorn api_project.app.main:app --host 127.0.0.1 --port 8000
```

Call `/health`:

```powershell
curl http://127.0.0.1:8000/health
```

Call existing prediction:

```powershell
curl http://127.0.0.1:8000/prediction/client_000001
```

Call missing prediction:

```powershell
curl http://127.0.0.1:8000/prediction/client_missing
```

Run tests:

```powershell
& $PY -m pytest api_project\tests -q
```

## 11. Risks / Caveats

- API currently looks up mock 500k predictions, not real model predictions.
- Real model predictions are generated separately under `pyspark_project/data/processed/`.
- Cache is MVP in-memory cache; it has hit/miss counters but no production cache backend.
- Spark on Windows warns about missing `winutils.exe`.
- Spark writer may fail on Windows; LR training script falls back to pandas + pyarrow Parquet.
- `duration` leakage risk is handled by exclusion.
- No load/stress/performance test yet.
- No Redis yet.
- Current split is train/test only, not train/validation/test.
- PySpark scripts are not unit-tested yet; they are script-validated.
- Raw data and generated processed data should not be committed.

## 12. Mentor Q&A

### What production pattern does this project simulate?

It simulates an offline model scoring pipeline plus online lookup-serving API. The model is trained and predictions are precomputed; the API serves predictions by `user_id` without realtime inference.

### Why Bank Marketing?

It is a practical tabular binary classification dataset with mixed categorical/numeric features, imbalance, realistic preprocessing needs, and a clear prediction target.

### Why exclude `duration`?

`duration` is call duration. In a production-like pre-call propensity model, call duration is not known before the contact happens, so including it could leak outcome information.

### Why is accuracy high but recall low?

The negative class dominates the dataset. A model can correctly predict many `no` rows and get high accuracy while missing many `yes` rows.

### Why threshold 0.2?

For baseline Logistic Regression, threshold 0.2 produced the best F1 among tested thresholds and improved recall from 0.1863 to 0.4591 while keeping precision near 0.4949.

### Is the API using mock or real predictions?

Currently the API uses mock 500k prediction rows from `api_project/data/mock_predictions_500k.parquet`.

### What is 500k mock data for?

It is for API lookup/cache/load/stress/performance testing readiness. It is not real training data and is not used for model metrics.

### How do I run the API?

```powershell
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m uvicorn api_project.app.main:app --host 127.0.0.1 --port 8000
```

### How do I run tests?

```powershell
& 'C:\Users\nmp10\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m pytest api_project\tests -q
```

### What should be next?

Next steps should be:

1. Decide with mentor whether LR threshold 0.2 is acceptable.
2. Generate the next real prediction output using the chosen threshold.
3. Optionally wire API to real model predictions instead of mock serving rows.
4. Add API load/stress testing.
5. Add cache comparison evidence.
6. Add PySpark tests or lightweight validation checks.
