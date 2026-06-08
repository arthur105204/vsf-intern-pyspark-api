from __future__ import annotations

import os
import sys
from pathlib import Path

from pyspark.ml import Pipeline
from pyspark.ml.feature import OneHotEncoder, StringIndexer, VectorAssembler
from pyspark.sql import DataFrame, SparkSession, Window
from pyspark.sql import functions as F


ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = ROOT / "pyspark_project" / "data" / "raw" / "bank_marketing" / "bank-full.csv"
PROCESSED_DIR = ROOT / "pyspark_project" / "data" / "processed"
SEED = 20260608
TRAIN_RATIO = 0.8
MODEL_VERSION = "bank_marketing_lr_v1"

CATEGORICAL_COLUMNS = [
    "job",
    "marital",
    "education",
    "default",
    "housing",
    "loan",
    "contact",
    "month",
    "poutcome",
]

NUMERIC_COLUMNS = [
    "age",
    "balance",
    "day",
    "campaign",
    "pdays",
    "previous",
]

EXCLUDED_COLUMNS = {
    "y": "target column; encoded into label",
    "duration": "excluded by default because call duration may leak post-contact outcome information",
    "user_id": "identifier for serving lookup, not a model feature",
}


def configure_pyspark_python() -> None:
    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    os.environ.setdefault("PYSPARK_DRIVER_PYTHON", sys.executable)


def create_spark(app_name: str) -> SparkSession:
    configure_pyspark_python()
    spark = (
        SparkSession.builder.master("local[*]")
        .appName(app_name)
        .config("spark.sql.shuffle.partitions", "8")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("WARN")
    return spark


def load_bank_marketing(spark: SparkSession) -> DataFrame:
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

    return (
        spark.read.option("header", True)
        .option("sep", ";")
        .option("inferSchema", True)
        .csv(str(DATASET_PATH))
    )


def add_user_id_and_label(df: DataFrame) -> DataFrame:
    if "user_id" not in df.columns:
        window = Window.orderBy(F.monotonically_increasing_id())
        df = df.withColumn("row_num_for_user_id", F.row_number().over(window))
        df = df.withColumn("user_id", F.format_string("client_%06d", F.col("row_num_for_user_id")))
        df = df.drop("row_num_for_user_id")

    return df.withColumn("label", F.when(F.col("y") == F.lit("yes"), F.lit(1.0)).otherwise(F.lit(0.0)))


def build_preprocessing_pipeline() -> Pipeline:
    indexers = [
        StringIndexer(
            inputCol=col,
            outputCol=f"{col}_idx",
            handleInvalid="keep",
        )
        for col in CATEGORICAL_COLUMNS
    ]
    encoder = OneHotEncoder(
        inputCols=[f"{col}_idx" for col in CATEGORICAL_COLUMNS],
        outputCols=[f"{col}_ohe" for col in CATEGORICAL_COLUMNS],
        handleInvalid="keep",
    )
    assembler = VectorAssembler(
        inputCols=NUMERIC_COLUMNS + [f"{col}_ohe" for col in CATEGORICAL_COLUMNS],
        outputCol="features",
        handleInvalid="keep",
    )
    return Pipeline(stages=indexers + [encoder, assembler])


def prepare_data(spark: SparkSession) -> tuple[DataFrame, DataFrame, DataFrame, Pipeline]:
    raw_df = load_bank_marketing(spark)
    prepared_df = add_user_id_and_label(raw_df)
    train_df, test_df = prepared_df.randomSplit([TRAIN_RATIO, 1.0 - TRAIN_RATIO], seed=SEED)
    pipeline = build_preprocessing_pipeline()
    return prepared_df, train_df, test_df, pipeline


def target_distribution(df: DataFrame) -> list[dict[str, object]]:
    return [
        {"y": row["y"], "count": int(row["count"])}
        for row in df.groupBy("y").count().orderBy("y").collect()
    ]


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)
