from __future__ import annotations

import shutil
from datetime import datetime, timezone

from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.functions import vector_to_array
from pyspark.sql import functions as F

from pipeline_utils import (
    CATEGORICAL_COLUMNS,
    DATASET_PATH,
    MODEL_VERSION,
    NUMERIC_COLUMNS,
    PROCESSED_DIR,
    SEED,
    create_spark,
    markdown_table,
    prepare_data,
)


PROJECT_DIR = DATASET_PATH.parents[3]
REPORT_PATH = PROJECT_DIR / "reports" / "LOGISTIC_REGRESSION_REPORT.md"
PARQUET_OUTPUT_PATH = PROCESSED_DIR / "predictions_lr.parquet"
CSV_FALLBACK_PATH = PROCESSED_DIR / "predictions_lr_csv"


def safe_divide(num: int, den: int) -> float:
    return float(num / den) if den else 0.0


def main() -> None:
    spark = create_spark("bank-marketing-logistic-regression")
    try:
        prepared_df, train_df, test_df, preprocessing_pipeline = prepare_data(spark)
        preprocessing_model = preprocessing_pipeline.fit(train_df)
        train_features = preprocessing_model.transform(train_df)
        test_features = preprocessing_model.transform(test_df)

        lr = LogisticRegression(
            featuresCol="features",
            labelCol="label",
            predictionCol="prediction",
            probabilityCol="probability",
            rawPredictionCol="rawPrediction",
            maxIter=30,
            regParam=0.01,
            elasticNetParam=0.0,
        )
        model = lr.fit(train_features)
        scored_test = model.transform(test_features)

        train_count = train_features.count()
        test_count = scored_test.count()

        confusion = {
            (int(row["label"]), int(row["prediction"])): int(row["count"])
            for row in scored_test.groupBy("label", "prediction").count().collect()
        }
        tp = confusion.get((1, 1), 0)
        tn = confusion.get((0, 0), 0)
        fp = confusion.get((0, 1), 0)
        fn = confusion.get((1, 0), 0)

        accuracy = safe_divide(tp + tn, tp + tn + fp + fn)
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall)

        evaluator = BinaryClassificationEvaluator(
            labelCol="label",
            rawPredictionCol="rawPrediction",
            metricName="areaUnderROC",
        )
        auc = float(evaluator.evaluate(scored_test))

        scored_all = model.transform(preprocessing_model.transform(prepared_df))
        prediction_output = (
            scored_all.withColumn("prediction_score", vector_to_array("probability")[1].cast("float"))
            .withColumn("prediction_label", F.col("prediction").cast("int"))
            .withColumn("model_version", F.lit(MODEL_VERSION))
            .withColumn("scored_at", F.current_timestamp())
            .withColumn("source", F.lit("real_model"))
            .select(
                "user_id",
                "prediction_score",
                "prediction_label",
                "model_version",
                "scored_at",
                "source",
            )
        )

        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        output_count = prediction_output.count()
        output_path = PARQUET_OUTPUT_PATH
        output_format = "spark_parquet"
        try:
            prediction_output.write.mode("overwrite").parquet(str(PARQUET_OUTPUT_PATH))
        except Exception:
            if PARQUET_OUTPUT_PATH.exists():
                if PARQUET_OUTPUT_PATH.is_dir():
                    shutil.rmtree(PARQUET_OUTPUT_PATH)
                else:
                    PARQUET_OUTPUT_PATH.unlink()
            try:
                prediction_output.toPandas().to_parquet(PARQUET_OUTPUT_PATH, index=False)
                output_format = "pandas_parquet_fallback"
            except Exception:
                if CSV_FALLBACK_PATH.exists():
                    if CSV_FALLBACK_PATH.is_dir():
                        shutil.rmtree(CSV_FALLBACK_PATH)
                    else:
                        CSV_FALLBACK_PATH.unlink()
                output_path = CSV_FALLBACK_PATH
                output_format = "pandas_csv_fallback"
                prediction_output.toPandas().to_csv(CSV_FALLBACK_PATH, index=False)

        report = f"""# Logistic Regression Report

Date: 2026-06-08

## Status

Completed.

## Model

| Field | Value |
| --- | --- |
| Model | Spark MLlib LogisticRegression |
| Model version | `{MODEL_VERSION}` |
| Seed | `{SEED}` |

## Feature Set Summary

Categorical features:

{markdown_table(["Column"], [[col] for col in CATEGORICAL_COLUMNS])}

Numeric features:

{markdown_table(["Column"], [[col] for col in NUMERIC_COLUMNS])}

Leakage note:

- `duration` is excluded because call duration can leak information from after the customer interaction.
- This keeps the MVP closer to a production-like propensity prediction workflow.

## Train/Test Sizes

| Split | Rows |
| --- | --- |
| Train | `{train_count}` |
| Test | `{test_count}` |

## Metrics

{markdown_table(["Metric", "Value"], [
    ["Accuracy", f"{accuracy:.4f}"],
    ["Precision", f"{precision:.4f}"],
    ["Recall", f"{recall:.4f}"],
    ["F1", f"{f1:.4f}"],
    ["AUC", f"{auc:.4f}"],
])}

Confusion matrix on test split:

{markdown_table(["", "Predicted 0", "Predicted 1"], [
    ["Actual 0", tn, fp],
    ["Actual 1", fn, tp],
])}

## Class Imbalance Note

The positive class is only about 11.7% of the dataset. Accuracy alone is not enough because a model can achieve high accuracy by mostly predicting the majority `no` class. Precision, recall, F1, and AUC are reported to make the evaluation more honest.

## Prediction Output Schema

{markdown_table(["Field", "Type"], [
    ["user_id", "string"],
    ["prediction_score", "float"],
    ["prediction_label", "int"],
    ["model_version", "string"],
    ["scored_at", "timestamp"],
    ["source", "string"],
])}

Output:

```text
{output_path.relative_to(PROJECT_DIR.parents[0])}
```

Output format:

```text
{output_format}
```

Output row count:

```text
{output_count}
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

Generated at: `{datetime.now(timezone.utc).isoformat()}`
"""
        REPORT_PATH.write_text(report, encoding="utf-8")

        print(f"train_count={train_count}")
        print(f"test_count={test_count}")
        print(f"accuracy={accuracy:.6f}")
        print(f"precision={precision:.6f}")
        print(f"recall={recall:.6f}")
        print(f"f1={f1:.6f}")
        print(f"auc={auc:.6f}")
        print(f"prediction_output_count={output_count}")
        print(f"prediction_output_path={output_path}")
        print(f"report_path={REPORT_PATH}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
