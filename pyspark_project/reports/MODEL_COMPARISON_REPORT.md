# Model Comparison Report

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

| Metric | Value |
| --- | --- |
| Accuracy | 0.8941 |
| Precision | 0.7046 |
| Recall | 0.1863 |
| F1 | 0.2946 |
| AUC | 0.7800 |

## C. Threshold Tuning: Baseline Logistic Regression

| model_name | threshold | accuracy | precision | recall | F1 | TP | FP | TN | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LogisticRegression | 0.10 | 0.6609 | 0.2234 | 0.7488 | 0.3441 | 796 | 2767 | 5118 | 267 |
| LogisticRegression | 0.20 | 0.8801 | 0.4949 | 0.4591 | 0.4763 | 488 | 498 | 7387 | 575 |
| LogisticRegression | 0.30 | 0.8952 | 0.6065 | 0.3349 | 0.4315 | 356 | 231 | 7654 | 707 |
| LogisticRegression | 0.40 | 0.8961 | 0.6580 | 0.2606 | 0.3733 | 277 | 144 | 7741 | 786 |
| LogisticRegression | 0.50 | 0.8941 | 0.7046 | 0.1863 | 0.2946 | 198 | 83 | 7802 | 865 |
| LogisticRegression | 0.60 | 0.8908 | 0.7416 | 0.1242 | 0.2127 | 132 | 46 | 7839 | 931 |
| LogisticRegression | 0.70 | 0.8878 | 0.7864 | 0.0762 | 0.1389 | 81 | 22 | 7863 | 982 |

Lower thresholds predict more positives, which usually increases recall and false positives while reducing precision. Higher thresholds predict fewer positives, which usually improves precision but misses more actual subscribers.

## D. Weighted Logistic Regression Results

Class weights were computed from the training split using:

```text
class_weight = total_train_rows / (2 * class_count)
```

Weights:

| Class | Train Count | Weight |
| --- | --- | --- |
| 0 / no | 32037 | 0.5660 |
| 1 / yes | 4226 | 4.2905 |

Weighted Logistic Regression default threshold 0.5:

| Metric | Value |
| --- | --- |
| Accuracy | 0.7545 |
| Precision | 0.2746 |
| Recall | 0.6500 |
| F1 | 0.3861 |
| AUC | 0.7798 |

Weighted LR threshold table:

| model_name | threshold | accuracy | precision | recall | F1 | TP | FP | TN | FN |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WeightedLogisticRegression | 0.10 | 0.1237 | 0.1192 | 0.9981 | 0.2130 | 1061 | 7839 | 46 | 2 |
| WeightedLogisticRegression | 0.20 | 0.2318 | 0.1309 | 0.9690 | 0.2306 | 1030 | 6841 | 1044 | 33 |
| WeightedLogisticRegression | 0.30 | 0.3747 | 0.1499 | 0.9125 | 0.2575 | 970 | 5502 | 2383 | 93 |
| WeightedLogisticRegression | 0.40 | 0.5606 | 0.1894 | 0.8231 | 0.3080 | 875 | 3744 | 4141 | 188 |
| WeightedLogisticRegression | 0.50 | 0.7545 | 0.2746 | 0.6500 | 0.3861 | 691 | 1825 | 6060 | 372 |
| WeightedLogisticRegression | 0.60 | 0.8567 | 0.4163 | 0.5127 | 0.4595 | 545 | 764 | 7121 | 518 |
| WeightedLogisticRegression | 0.70 | 0.8886 | 0.5427 | 0.3942 | 0.4567 | 419 | 353 | 7532 | 644 |

## E. Tree-Based Model Results

| Field | Value |
| --- | --- |
| Model | GBTClassifier |
| Parameters | maxIter=20, maxDepth=4 |
| Accuracy | 0.8932 |
| Precision | 0.6890 |
| Recall | 0.1834 |
| F1 | 0.2897 |
| AUC | 0.7940 |

## F. Final Comparison Table

| model_variant | threshold | accuracy | precision | recall | F1 | AUC | notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| LR default threshold 0.5 | 0.50 | 0.8941 | 0.7046 | 0.1863 | 0.2946 | 0.7800 | High accuracy, low recall baseline. |
| LR best F1 threshold | 0.20 | 0.8801 | 0.4949 | 0.4591 | 0.4763 | 0.7800 | Best F1 among tested thresholds. |
| LR best recall threshold with precision >= 0.30 | 0.20 | 0.8801 | 0.4949 | 0.4591 | 0.4763 | 0.7800 | Recall-focused LR option with mentor-discussion precision floor. |
| Weighted LR default threshold 0.5 | 0.50 | 0.7545 | 0.2746 | 0.6500 | 0.3861 | 0.7798 | Uses inverse-frequency class weights. |
| Weighted LR best F1 threshold | 0.60 | 0.8567 | 0.4163 | 0.5127 | 0.4595 | 0.7798 | Best weighted LR F1 among tested thresholds. |
| GBTClassifier | default | 0.8932 | 0.6890 | 0.1834 | 0.2897 | 0.7940 | Modest local-runtime tree model; no heavy tuning. |

## G. Interpretation

Accuracy is high because the negative class dominates the dataset. A model can classify many `no` rows correctly while still missing many `yes` rows, so recall is low.

Threshold tuning improves recall by lowering the score cutoff. This makes the model more willing to predict `yes`, but it creates more false positives and lowers precision.

Class weighting helps the model pay more attention to the minority `yes` class. It usually improves recall at the cost of lower precision and sometimes lower accuracy.

The tree-based model provides a useful comparison, but this gate uses modest parameters only. It is not a heavy tuning pass.

Best MVP option should balance recall improvement with an acceptable precision trade-off. The mentor discussion should focus on how costly false positives are compared with missed subscribers.

## H. Recommendation

Recommended next model output candidate:

```text
LR best F1 threshold
```

Recommended metrics:

| Metric | Value |
| --- | --- |
| Threshold | 0.20 |
| Accuracy | 0.8801 |
| Precision | 0.4949 |
| Recall | 0.4591 |
| F1 | 0.4763 |
| AUC | 0.7800 |

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

Generated at: `2026-06-08T08:25:17.542747+00:00`
