# Pandas EDA Report

Date: 2026-06-06

## Status

Completed.

Dataset used:

```text
pyspark_project/data/raw/bank_marketing/bank-full.csv
```

The dataset was loaded with `sep=";"`. Raw dataset files are kept out of git. The report and generated figures are the reviewable artifacts.

## Dataset Overview

Bank Marketing is a tabular classification dataset from direct marketing campaigns by a banking institution.

Problem framing:

- Task: term deposit subscription propensity prediction.
- Target column: `y`.
- Positive class: `yes`.
- Negative class: `no`.
- Target encoding plan: `yes = 1`, `no = 0`.

Dataset shape:

| Metric | Value |
| --- | --- |
| Rows | `45,211` |
| Columns | `17` |

Columns:

```text
age, job, marital, education, default, balance, housing, loan, contact,
day, month, duration, campaign, pdays, previous, poutcome, y
```

## Schema and Dtypes

| Column | Dtype |
| --- | --- |
| `age` | int64 |
| `job` | str |
| `marital` | str |
| `education` | str |
| `default` | str |
| `balance` | int64 |
| `housing` | str |
| `loan` | str |
| `contact` | str |
| `day` | int64 |
| `month` | str |
| `duration` | int64 |
| `campaign` | int64 |
| `pdays` | int64 |
| `previous` | int64 |
| `poutcome` | str |
| `y` | str |

## Target Distribution

| Target | Rows | Share |
| --- | --- | --- |
| `no` | `39,922` | `88.30%` |
| `yes` | `5,289` | `11.70%` |

The target is imbalanced, so accuracy alone is not enough for evaluation. Precision, recall, F1, and AUC should also be tracked.

## Missing and Unknown Values

No null values were detected by Pandas.

Literal `unknown` values:

| Column | Unknown Count |
| --- | --- |
| `job` | `288` |
| `education` | `1,857` |
| `contact` | `13,020` |
| `poutcome` | `36,959` |

`unknown` should be treated as a categorical level initially, then reviewed during feature analysis.

## Numeric Feature Summary

| Feature | Mean | Std | Min | P50 | Max |
| --- | --- | --- | --- | --- | --- |
| `age` | `40.936` | `10.619` | `18` | `39` | `95` |
| `balance` | `1362.272` | `3044.766` | `-8019` | `448` | `102127` |
| `day` | `15.806` | `8.322` | `1` | `16` | `31` |
| `duration` | `258.163` | `257.528` | `0` | `180` | `4918` |
| `campaign` | `2.764` | `3.098` | `1` | `2` | `63` |
| `pdays` | `40.198` | `100.129` | `-1` | `-1` | `871` |
| `previous` | `0.580` | `2.303` | `0` | `0` | `275` |

## Categorical Feature Cardinality

| Feature | Cardinality |
| --- | --- |
| `job` | `12` |
| `marital` | `3` |
| `education` | `4` |
| `default` | `2` |
| `housing` | `2` |
| `loan` | `2` |
| `contact` | `3` |
| `month` | `12` |
| `poutcome` | `4` |

## Chart List

Exactly 5 EDA charts were generated:

| # | Chart | File Path |
| --- | --- | --- |
| 1 | Target distribution | `pyspark_project/reports/figures/01_target_distribution.png` |
| 2 | Age distribution | `pyspark_project/reports/figures/02_age_distribution.png` |
| 3 | Top job categories | `pyspark_project/reports/figures/03_top_job_categories.png` |
| 4 | Balance distribution, clipped p1-p99 | `pyspark_project/reports/figures/04_balance_distribution.png` |
| 5 | Target rate by job | `pyspark_project/reports/figures/05_target_rate_by_job.png` |

## Key Findings

- The dataset has 45,211 rows, enough for a meaningful internship-scale PySpark pipeline.
- The target is imbalanced: only about 11.70% of rows are `yes`.
- `balance`, `duration`, `campaign`, `pdays`, and `previous` have large ranges and likely outliers.
- `pdays = -1` is common and should be treated as meaningful, not ordinary missingness.
- `contact` and `poutcome` contain many `unknown` values.
- Top target-rate job categories include `student`, `retired`, and `unemployed`.

Target rate by job, top 10:

| Job | Yes Rate |
| --- | --- |
| `student` | `28.68%` |
| `retired` | `22.79%` |
| `unemployed` | `15.50%` |
| `management` | `13.76%` |
| `admin.` | `12.20%` |
| `self-employed` | `11.84%` |
| `unknown` | `11.81%` |
| `technician` | `11.06%` |
| `services` | `8.88%` |
| `housemaid` | `8.79%` |

## Potential Data Quality Issues

- High `unknown` count in `poutcome` and `contact`.
- Strong outliers in `balance` and `duration`.
- `duration` may be leakage-prone if predictions are meant to happen before campaign call completion.
- No stable customer identifier exists, so the pipeline should generate `user_id`.
- Class imbalance should influence metric selection and model interpretation.

## Cleaning and Feature Implications

- Generate `user_id` before scoring so each prediction row can be served by API lookup.
- Encode `y` into `label` using `yes = 1` and `no = 0`.
- Keep literal `unknown` as its own category for the MVP instead of dropping rows.
- Use `StringIndexer` and `OneHotEncoder` for categorical columns.
- Use numeric columns directly after checking outliers and nulls.
- Consider excluding or separately evaluating `duration` if the intended prediction moment is before call completion.
- Track precision, recall, F1, and AUC because the positive class is only about 11.70%.

## Why This Dataset Is Suitable for PySpark

Bank Marketing is suitable because it includes:

- Mixed numeric and categorical features.
- Clear binary target.
- Realistic cleaning needs around `unknown`, outliers, and generated IDs.
- Categorical preprocessing needs for `StringIndexer` and `OneHotEncoder`.
- A natural prediction output table for lookup API serving.

## M4 Status

Milestone M4, EDA completed, can be marked `Done`.
