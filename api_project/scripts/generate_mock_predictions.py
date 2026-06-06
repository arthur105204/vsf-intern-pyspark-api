from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROW_COUNT = 500_000
SEED = 20260606
MODEL_VERSION = "bank_marketing_mock_v1"
SCORED_AT = "2026-06-06T09:00:00Z"
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data"
PARQUET_PATH = OUTPUT_DIR / "mock_predictions_500k.parquet"
CSV_FALLBACK_PATH = OUTPUT_DIR / "mock_predictions_500k.csv"


def build_mock_predictions() -> pd.DataFrame:
    rng = np.random.default_rng(SEED)

    # Beta distribution creates realistic-looking propensity scores:
    # mostly low/medium values, with a smaller high-propensity tail.
    scores = rng.beta(a=2.0, b=5.0, size=ROW_COUNT).astype("float32")

    return pd.DataFrame(
        {
            "user_id": [f"client_{i:06d}" for i in range(1, ROW_COUNT + 1)],
            "prediction_score": scores,
            "prediction_label": (scores >= 0.5).astype("int8"),
            "model_version": MODEL_VERSION,
            "scored_at": pd.Timestamp(SCORED_AT),
            "source": "mock",
        }
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = build_mock_predictions()

    try:
        df.to_parquet(PARQUET_PATH, index=False)
        output_path = PARQUET_PATH
        output_format = "parquet"
    except Exception:
        df.to_csv(CSV_FALLBACK_PATH, index=False)
        output_path = CSV_FALLBACK_PATH
        output_format = "csv_fallback"

    print(f"output_format={output_format}")
    print(f"output_path={output_path}")
    print(f"row_count={len(df)}")
    print(f"score_min={df['prediction_score'].min():.6f}")
    print(f"score_mean={df['prediction_score'].mean():.6f}")
    print(f"score_max={df['prediction_score'].max():.6f}")
    print(f"positive_labels={int(df['prediction_label'].sum())}")


if __name__ == "__main__":
    main()
