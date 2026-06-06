# Pandas EDA Report

Date: 2026-06-06

## Status

`DATASET_MISSING`

The Bank Marketing dataset was not found locally, so Pandas EDA was not executed and no EDA charts were generated today.

Checked likely local locations:

- `data/raw/`
- `pyspark_project/data/raw/`
- `bank.csv`
- `bank-full.csv`
- `bank-additional-full.csv`

Current result: `data/raw/` only contains `.gitkeep`.

## Download Instructions

Dataset source: UCI Machine Learning Repository, Bank Marketing dataset.

Recommended manual steps:

1. Open: `https://archive.ics.uci.edu/dataset/222/bank+marketing`
2. Download `bank.zip` or `bank-additional.zip`.
3. Extract one of these CSV files into `data/raw/`:
   - `bank-full.csv`
   - `bank.csv`
   - `bank-additional-full.csv`
4. Re-run Pandas EDA after the CSV exists locally.

Expected preferred file for this project:

```text
data/raw/bank-full.csv
```

PowerShell download option:

```powershell
Invoke-WebRequest -Uri "https://archive.ics.uci.edu/static/public/222/bank+marketing.zip" -OutFile "data/raw/bank-marketing.zip"
Expand-Archive -LiteralPath "data/raw/bank-marketing.zip" -DestinationPath "data/raw/bank-marketing" -Force
Get-ChildItem -Recurse "data/raw/bank-marketing" -Filter "bank-full.csv" | Select-Object -First 1 | Copy-Item -Destination "data/raw/bank-full.csv"
```

If `bank-full.csv` is not available after extraction, use `bank.csv` or `bank-additional-full.csv` and update the EDA report with the chosen source file.

## Dataset Overview

The intended dataset is Bank Marketing. It is a tabular classification dataset related to direct marketing campaigns for a Portuguese banking institution.

Problem framing:

- Task: term deposit subscription propensity prediction.
- Target column: `y`.
- Positive class: `yes`.
- Negative class: `no`.
- Target encoding plan: `yes = 1`, `no = 0`.

## Required EDA Outputs

The following EDA outputs are still pending because the dataset is missing:

- Row count.
- Column count.
- Schema and dtypes.
- Missing value and `unknown` value summary.
- Target distribution for `y`.
- Numeric feature summary.
- Categorical feature cardinality summary.

## Planned Chart List

Exactly these 5 charts should be generated after the dataset is available:

| # | Chart | Planned File Path | Status |
| --- | --- | --- | --- |
| 1 | Target distribution | `pyspark_project/reports/figures/01_target_distribution.png` | Blocked |
| 2 | Age distribution | `pyspark_project/reports/figures/02_age_distribution.png` | Blocked |
| 3 | Top job categories | `pyspark_project/reports/figures/03_top_job_categories.png` | Blocked |
| 4 | Balance or campaign distribution | `pyspark_project/reports/figures/04_numeric_distribution.png` | Blocked |
| 5 | Target rate by important categorical feature | `pyspark_project/reports/figures/05_target_rate_by_category.png` | Blocked |

## Key Findings

No data-driven findings are available yet because the dataset is not present locally.

Expected analysis questions once the dataset is available:

- How imbalanced is the `y` target?
- Which categorical features have many levels or many `unknown` values?
- Whether numeric fields such as `balance`, `campaign`, `pdays`, or `previous` have strong outliers.
- Whether contact/campaign-related fields create leakage risks.
- Which categorical feature is most useful for target-rate comparison.

## Potential Data Quality Issues to Check

- `unknown` values in categorical columns such as `job`, `education`, `contact`, or `poutcome`.
- Outliers in `balance`, `duration`, `campaign`, `pdays`, and `previous`.
- `pdays = -1`, which usually means the client was not previously contacted.
- Possible leakage from `duration`, because call duration may only be known after the marketing contact.
- Missing stable customer identifier, requiring generated `user_id`.

## Why This Dataset Is Suitable

Bank Marketing is suitable for this PySpark pipeline project because it provides:

- A practical binary classification target.
- Mixed numeric and categorical features.
- Realistic preprocessing needs for `StringIndexer`, `OneHotEncoder`, and `VectorAssembler`.
- A clear output use case for precomputed prediction serving by `user_id`.
- Enough feature variety to compare Logistic Regression with tree-based Spark models later.

## M4 Status

Milestone M4, EDA completed, should be marked `In Progress` or `Blocked`, not `Done`.

Reason: dataset is missing, so EDA statistics and charts cannot be produced truthfully yet.
