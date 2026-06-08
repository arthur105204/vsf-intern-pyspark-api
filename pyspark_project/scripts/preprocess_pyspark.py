from __future__ import annotations

from datetime import datetime, timezone

from pipeline_utils import (
    CATEGORICAL_COLUMNS,
    DATASET_PATH,
    EXCLUDED_COLUMNS,
    NUMERIC_COLUMNS,
    SEED,
    TRAIN_RATIO,
    create_spark,
    markdown_table,
    prepare_data,
    target_distribution,
)


PROJECT_DIR = DATASET_PATH.parents[3]
REPORT_PATH = PROJECT_DIR / "reports" / "PYSPARK_PREPROCESSING_REPORT.md"


def main() -> None:
    spark = create_spark("bank-marketing-preprocessing")
    try:
        prepared_df, train_df, test_df, pipeline = prepare_data(spark)
        pipeline_model = pipeline.fit(train_df)
        transformed_train = pipeline_model.transform(train_df)

        row_count = prepared_df.count()
        column_count = len(prepared_df.columns)
        train_count = train_df.count()
        test_count = test_df.count()
        feature_vector_size = transformed_train.select("features").first()["features"].size
        distribution = target_distribution(prepared_df)

        stages = [
            f"StringIndexer(handleInvalid='keep') for `{col}`"
            for col in CATEGORICAL_COLUMNS
        ]
        stages.extend(
            [
                "OneHotEncoder(handleInvalid='keep') for indexed categorical columns",
                "VectorAssembler(handleInvalid='keep') for numeric + encoded categorical features",
            ]
        )

        report = f"""# PySpark Preprocessing Report

Date: 2026-06-08

## Status

Completed.

## Input Dataset

```text
{DATASET_PATH.relative_to(PROJECT_DIR.parents[0])}
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
| Row count | `{row_count}` |
| Column count after `user_id` and `label` | `{column_count}` |

## Target Distribution

{markdown_table(["Target", "Count"], [[item["y"], item["count"]] for item in distribution])}

## Feature Columns

Categorical columns:

{markdown_table(["Column"], [[col] for col in CATEGORICAL_COLUMNS])}

Numeric columns:

{markdown_table(["Column"], [[col] for col in NUMERIC_COLUMNS])}

## Excluded Columns

{markdown_table(["Column", "Reason"], [[col, reason] for col, reason in EXCLUDED_COLUMNS.items()])}

`duration` is intentionally excluded from the main feature set because it can introduce leakage in a production-like propensity prediction setting. A real pre-call scoring workflow should not depend on information known only after the customer interaction.

## Preprocessing Stages

{markdown_table(["Stage"], [[stage] for stage in stages])}

Fitted feature vector size:

```text
{feature_vector_size}
```

## Train/Test Split

Deterministic seed:

```text
{SEED}
```

Split plan:

```text
train={TRAIN_RATIO:.0%}
test={1.0 - TRAIN_RATIO:.0%}
```

| Split | Rows |
| --- | --- |
| Train | `{train_count}` |
| Test | `{test_count}` |

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

Generated at: `{datetime.now(timezone.utc).isoformat()}`
"""
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(report, encoding="utf-8")
        print(f"row_count={row_count}")
        print(f"column_count={column_count}")
        print(f"train_count={train_count}")
        print(f"test_count={test_count}")
        print(f"feature_vector_size={feature_vector_size}")
        print(f"report_path={REPORT_PATH}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
