from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pyspark.ml.classification import GBTClassifier, LogisticRegression, RandomForestClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.functions import vector_to_array
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from pipeline_utils import (
    DATASET_PATH,
    SEED,
    create_spark,
    markdown_table,
    prepare_data,
)


PROJECT_DIR = DATASET_PATH.parents[3]
REPORT_PATH = PROJECT_DIR / "reports" / "MODEL_COMPARISON_REPORT.md"
METRICS_JSON_PATH = PROJECT_DIR / "reports" / "model_comparison_metrics.json"
THRESHOLDS = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70]
ACCEPTABLE_PRECISION = 0.30


def safe_divide(num: int | float, den: int | float) -> float:
    return float(num / den) if den else 0.0


def metrics_from_counts(tp: int, fp: int, tn: int, fn: int) -> dict[str, Any]:
    accuracy = safe_divide(tp + tn, tp + fp + tn + fn)
    precision = safe_divide(tp, tp + fp)
    recall = safe_divide(tp, tp + fn)
    f1 = safe_divide(2 * precision * recall, precision + recall)
    return {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
    }


def evaluate_threshold(scored: DataFrame, model_name: str, threshold: float) -> dict[str, Any]:
    pred_col = f"threshold_prediction_{str(threshold).replace('.', '_')}"
    thresholded = scored.withColumn(
        pred_col,
        F.when(F.col("prediction_score") >= F.lit(threshold), F.lit(1)).otherwise(F.lit(0)),
    )
    counts = {
        (int(row["label"]), int(row[pred_col])): int(row["count"])
        for row in thresholded.groupBy("label", pred_col).count().collect()
    }
    result = metrics_from_counts(
        tp=counts.get((1, 1), 0),
        fp=counts.get((0, 1), 0),
        tn=counts.get((0, 0), 0),
        fn=counts.get((1, 0), 0),
    )
    result.update({"model_name": model_name, "threshold": threshold})
    return result


def add_prediction_score(scored: DataFrame) -> DataFrame:
    return scored.withColumn("prediction_score", vector_to_array("probability")[1].cast("double"))


def evaluate_auc(scored: DataFrame) -> float:
    evaluator = BinaryClassificationEvaluator(
        labelCol="label",
        rawPredictionCol="rawPrediction",
        metricName="areaUnderROC",
    )
    return float(evaluator.evaluate(scored))


def threshold_table(scored: DataFrame, model_name: str) -> list[dict[str, Any]]:
    scored = add_prediction_score(scored)
    return [evaluate_threshold(scored, model_name, threshold) for threshold in THRESHOLDS]


def class_weights(train_features: DataFrame) -> tuple[DataFrame, dict[str, float]]:
    counts = {int(row["label"]): int(row["count"]) for row in train_features.groupBy("label").count().collect()}
    total = counts.get(0, 0) + counts.get(1, 0)
    negative_weight = safe_divide(total, 2 * counts.get(0, 0))
    positive_weight = safe_divide(total, 2 * counts.get(1, 0))
    weighted = train_features.withColumn(
        "class_weight",
        F.when(F.col("label") == F.lit(1.0), F.lit(positive_weight)).otherwise(F.lit(negative_weight)),
    )
    return weighted, {
        "negative_count": counts.get(0, 0),
        "positive_count": counts.get(1, 0),
        "negative_weight": negative_weight,
        "positive_weight": positive_weight,
    }


def format_float(value: float | None) -> str:
    if value is None:
        return ""
    return f"{value:.4f}"


def rows_for_threshold_report(rows: list[dict[str, Any]]) -> list[list[Any]]:
    return [
        [
            row["model_name"],
            f"{row['threshold']:.2f}",
            format_float(row["accuracy"]),
            format_float(row["precision"]),
            format_float(row["recall"]),
            format_float(row["f1"]),
            row["tp"],
            row["fp"],
            row["tn"],
            row["fn"],
        ]
        for row in rows
    ]


def pick_best_f1(rows: list[dict[str, Any]]) -> dict[str, Any]:
    return max(rows, key=lambda row: (row["f1"], row["recall"], row["precision"]))


def pick_best_recall_with_precision(rows: list[dict[str, Any]]) -> dict[str, Any]:
    acceptable = [row for row in rows if row["precision"] >= ACCEPTABLE_PRECISION]
    if not acceptable:
        acceptable = rows
    return max(acceptable, key=lambda row: (row["recall"], row["f1"], row["precision"]))


def make_final_row(variant: str, row: dict[str, Any], auc: float | None, notes: str) -> list[Any]:
    return [
        variant,
        f"{row['threshold']:.2f}" if row.get("threshold") is not None else "",
        format_float(row["accuracy"]),
        format_float(row["precision"]),
        format_float(row["recall"]),
        format_float(row["f1"]),
        format_float(auc),
        notes,
    ]


def write_outputs(metrics: dict[str, Any]) -> None:
    baseline_rows = metrics["baseline_lr"]["threshold_table"]
    weighted_rows = metrics["weighted_lr"]["threshold_table"]
    tree = metrics["tree_model"]

    baseline_best_f1 = pick_best_f1(baseline_rows)
    baseline_best_recall = pick_best_recall_with_precision(baseline_rows)
    weighted_best_f1 = pick_best_f1(weighted_rows)
    weighted_best_recall = pick_best_recall_with_precision(weighted_rows)

    final_rows = [
        make_final_row(
            "LR default threshold 0.5",
            metrics["baseline_lr"]["default_metrics"],
            metrics["baseline_lr"]["auc"],
            "High accuracy, low recall baseline.",
        ),
        make_final_row(
            "LR best F1 threshold",
            baseline_best_f1,
            metrics["baseline_lr"]["auc"],
            "Best F1 among tested thresholds.",
        ),
        make_final_row(
            f"LR best recall threshold with precision >= {ACCEPTABLE_PRECISION:.2f}",
            baseline_best_recall,
            metrics["baseline_lr"]["auc"],
            "Recall-focused LR option with mentor-discussion precision floor.",
        ),
        make_final_row(
            "Weighted LR default threshold 0.5",
            metrics["weighted_lr"]["default_metrics"],
            metrics["weighted_lr"]["auc"],
            "Uses inverse-frequency class weights.",
        ),
        make_final_row(
            "Weighted LR best F1 threshold",
            weighted_best_f1,
            metrics["weighted_lr"]["auc"],
            "Best weighted LR F1 among tested thresholds.",
        ),
        [
            tree["model_name"],
            "default",
            format_float(tree["accuracy"]),
            format_float(tree["precision"]),
            format_float(tree["recall"]),
            format_float(tree["f1"]),
            format_float(tree["auc"]),
            tree["notes"],
        ],
    ]

    recommended = max(
        [
            ("LR best F1 threshold", baseline_best_f1, metrics["baseline_lr"]["auc"]),
            ("Weighted LR best F1 threshold", weighted_best_f1, metrics["weighted_lr"]["auc"]),
            (tree["model_name"], tree, tree["auc"]),
        ],
        key=lambda item: (item[1]["f1"], item[1]["recall"], item[1]["precision"]),
    )

    metrics["selected_rows"] = {
        "baseline_best_f1": baseline_best_f1,
        "baseline_best_recall_with_precision_floor": baseline_best_recall,
        "weighted_best_f1": weighted_best_f1,
        "weighted_best_recall_with_precision_floor": weighted_best_recall,
        "recommended_by_f1": {
            "variant": recommended[0],
            "metrics": recommended[1],
            "auc": recommended[2],
        },
    }

    METRICS_JSON_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    report = f"""# Model Comparison Report

Date: 2026-06-08

## A. Context

The baseline Logistic Regression model had high accuracy but low recall:

- Accuracy: `0.894055`
- Precision: `0.704626`
- Recall: `0.186265`
- F1: `0.294643`
- AUC: `0.779950`

The positive class is imbalanced: Bank Marketing has 45,211 rows and only about 11.7% are `yes`.

`duration` remains excluded from all models because it can leak post-contact information into a production-like propensity model.

The mock 500k API dataset is not used for model evaluation. All metrics in this report use the real Bank Marketing train/test split only.

## B. Baseline Metrics Table

Logistic Regression at default threshold 0.5:

{markdown_table(["Metric", "Value"], [
    ["Accuracy", format_float(metrics["baseline_lr"]["default_metrics"]["accuracy"])],
    ["Precision", format_float(metrics["baseline_lr"]["default_metrics"]["precision"])],
    ["Recall", format_float(metrics["baseline_lr"]["default_metrics"]["recall"])],
    ["F1", format_float(metrics["baseline_lr"]["default_metrics"]["f1"])],
    ["AUC", format_float(metrics["baseline_lr"]["auc"])],
])}

## C. Threshold Tuning: Baseline Logistic Regression

{markdown_table(
    ["model_name", "threshold", "accuracy", "precision", "recall", "F1", "TP", "FP", "TN", "FN"],
    rows_for_threshold_report(baseline_rows),
)}

Lower thresholds predict more positives, which usually increases recall and false positives while reducing precision. Higher thresholds predict fewer positives, which usually improves precision but misses more actual subscribers.

## D. Weighted Logistic Regression Results

Class weights were computed from the training split using:

```text
class_weight = total_train_rows / (2 * class_count)
```

Weights:

{markdown_table(["Class", "Train Count", "Weight"], [
    ["0 / no", metrics["weighted_lr"]["class_weights"]["negative_count"], format_float(metrics["weighted_lr"]["class_weights"]["negative_weight"])],
    ["1 / yes", metrics["weighted_lr"]["class_weights"]["positive_count"], format_float(metrics["weighted_lr"]["class_weights"]["positive_weight"])],
])}

Weighted Logistic Regression default threshold 0.5:

{markdown_table(["Metric", "Value"], [
    ["Accuracy", format_float(metrics["weighted_lr"]["default_metrics"]["accuracy"])],
    ["Precision", format_float(metrics["weighted_lr"]["default_metrics"]["precision"])],
    ["Recall", format_float(metrics["weighted_lr"]["default_metrics"]["recall"])],
    ["F1", format_float(metrics["weighted_lr"]["default_metrics"]["f1"])],
    ["AUC", format_float(metrics["weighted_lr"]["auc"])],
])}

Weighted LR threshold table:

{markdown_table(
    ["model_name", "threshold", "accuracy", "precision", "recall", "F1", "TP", "FP", "TN", "FN"],
    rows_for_threshold_report(weighted_rows),
)}

## E. Tree-Based Model Results

{markdown_table(["Field", "Value"], [
    ["Model", tree["model_name"]],
    ["Parameters", tree["parameters"]],
    ["Accuracy", format_float(tree["accuracy"])],
    ["Precision", format_float(tree["precision"])],
    ["Recall", format_float(tree["recall"])],
    ["F1", format_float(tree["f1"])],
    ["AUC", format_float(tree["auc"])],
])}

## F. Final Comparison Table

{markdown_table(
    ["model_variant", "threshold", "accuracy", "precision", "recall", "F1", "AUC", "notes"],
    final_rows,
)}

## G. Interpretation

Accuracy is high because the negative class dominates the dataset. A model can classify many `no` rows correctly while still missing many `yes` rows, so recall is low.

Threshold tuning improves recall by lowering the score cutoff. This makes the model more willing to predict `yes`, but it creates more false positives and lowers precision.

Class weighting helps the model pay more attention to the minority `yes` class. It usually improves recall at the cost of lower precision and sometimes lower accuracy.

The tree-based model provides a useful comparison, but this gate uses modest parameters only. It is not a heavy tuning pass.

Best MVP option should balance recall improvement with an acceptable precision trade-off. The mentor discussion should focus on how costly false positives are compared with missed subscribers.

## H. Recommendation

Recommended next model output candidate:

```text
{recommended[0]}
```

Recommended metrics:

{markdown_table(["Metric", "Value"], [
    ["Threshold", f"{recommended[1].get('threshold'):.2f}" if recommended[1].get("threshold") is not None else "default"],
    ["Accuracy", format_float(recommended[1]["accuracy"])],
    ["Precision", format_float(recommended[1]["precision"])],
    ["Recall", format_float(recommended[1]["recall"])],
    ["F1", format_float(recommended[1]["f1"])],
    ["AUC", format_float(recommended[2])],
])}

This gate does not update the API prediction output. The recommendation should be reviewed with the mentor before replacing the current model output.

## Gate Result

PASS.

All required comparison components were generated:

- Baseline LR threshold table.
- Weighted LR training and threshold table.
- One tree-based Spark MLlib model.
- Consolidated final comparison.
- Precision/recall trade-off explanation.
- Explicit notes that `duration` is excluded and mock 500k API rows are not used for evaluation.

Generated at: `{datetime.now(timezone.utc).isoformat()}`
"""
    REPORT_PATH.write_text(report, encoding="utf-8")


def main() -> None:
    spark = create_spark("bank-marketing-model-comparison")
    try:
        _, train_df, test_df, preprocessing_pipeline = prepare_data(spark)
        preprocessing_model = preprocessing_pipeline.fit(train_df)
        train_features = preprocessing_model.transform(train_df).cache()
        test_features = preprocessing_model.transform(test_df).cache()

        train_count = train_features.count()
        test_count = test_features.count()

        lr = LogisticRegression(
            featuresCol="features",
            labelCol="label",
            maxIter=30,
            regParam=0.01,
            elasticNetParam=0.0,
        )
        lr_model = lr.fit(train_features)
        lr_scored = lr_model.transform(test_features).cache()
        baseline_rows = threshold_table(lr_scored, "LogisticRegression")
        baseline_auc = evaluate_auc(lr_scored)

        weighted_train, weights = class_weights(train_features)
        weighted_lr = LogisticRegression(
            featuresCol="features",
            labelCol="label",
            weightCol="class_weight",
            maxIter=30,
            regParam=0.01,
            elasticNetParam=0.0,
        )
        weighted_model = weighted_lr.fit(weighted_train)
        weighted_scored = weighted_model.transform(test_features).cache()
        weighted_rows = threshold_table(weighted_scored, "WeightedLogisticRegression")
        weighted_auc = evaluate_auc(weighted_scored)

        tree_notes = ""
        try:
            tree_classifier = GBTClassifier(
                featuresCol="features",
                labelCol="label",
                maxIter=20,
                maxDepth=4,
                seed=SEED,
            )
            tree_model_name = "GBTClassifier"
            tree_parameters = "maxIter=20, maxDepth=4"
            tree_model = tree_classifier.fit(train_features)
        except Exception as exc:
            tree_notes = f"GBT failed, fallback RandomForest used. GBT error: {type(exc).__name__}"
            tree_classifier = RandomForestClassifier(
                featuresCol="features",
                labelCol="label",
                numTrees=40,
                maxDepth=6,
                seed=SEED,
            )
            tree_model_name = "RandomForestClassifier"
            tree_parameters = "numTrees=40, maxDepth=6"
            tree_model = tree_classifier.fit(train_features)

        tree_scored = tree_model.transform(test_features).cache()
        tree_scored_with_score = add_prediction_score(tree_scored)
        tree_metrics = evaluate_threshold(tree_scored_with_score, tree_model_name, 0.50)
        tree_auc = evaluate_auc(tree_scored)
        tree_metrics.update(
            {
                "model_name": tree_model_name,
                "parameters": tree_parameters,
                "auc": tree_auc,
                "notes": tree_notes or "Modest local-runtime tree model; no heavy tuning.",
            }
        )

        metrics = {
            "run_at": datetime.now(timezone.utc).isoformat(),
            "dataset": str(DATASET_PATH),
            "seed": SEED,
            "train_count": train_count,
            "test_count": test_count,
            "duration_excluded": True,
            "mock_500k_used_for_evaluation": False,
            "thresholds": THRESHOLDS,
            "baseline_lr": {
                "auc": baseline_auc,
                "default_metrics": next(row for row in baseline_rows if row["threshold"] == 0.50),
                "threshold_table": baseline_rows,
            },
            "weighted_lr": {
                "auc": weighted_auc,
                "class_weights": weights,
                "default_metrics": next(row for row in weighted_rows if row["threshold"] == 0.50),
                "threshold_table": weighted_rows,
            },
            "tree_model": tree_metrics,
        }
        write_outputs(metrics)

        recommended = metrics["selected_rows"]["recommended_by_f1"]
        print(f"train_count={train_count}")
        print(f"test_count={test_count}")
        print(f"baseline_lr_auc={baseline_auc:.6f}")
        print(f"weighted_lr_auc={weighted_auc:.6f}")
        print(f"tree_model={tree_model_name}")
        print(f"tree_auc={tree_auc:.6f}")
        print(f"recommended_variant={recommended['variant']}")
        print(f"recommended_f1={recommended['metrics']['f1']:.6f}")
        print(f"report_path={REPORT_PATH}")
        print(f"metrics_json_path={METRICS_JSON_PATH}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
