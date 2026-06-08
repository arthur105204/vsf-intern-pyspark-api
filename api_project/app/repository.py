from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
PREDICTION_DATA_PATH = ROOT / "api_project" / "data" / "mock_predictions_500k.parquet"


class PredictionRepository:
    def __init__(self, data_path: Path = PREDICTION_DATA_PATH) -> None:
        self.data_path = data_path
        self._records: dict[str, dict[str, Any]] | None = None

    def load(self) -> None:
        if self._records is not None:
            return
        if not self.data_path.exists():
            raise FileNotFoundError(f"Prediction data not found: {self.data_path}")

        df = pd.read_parquet(self.data_path)
        records: dict[str, dict[str, Any]] = {}
        for row in df.itertuples(index=False):
            scored_at = row.scored_at
            if hasattr(scored_at, "isoformat"):
                scored_at_value = scored_at.isoformat().replace("+00:00", "Z")
            else:
                scored_at_value = str(scored_at)

            records[row.user_id] = {
                "user_id": row.user_id,
                "prediction_score": float(row.prediction_score),
                "prediction_label": int(row.prediction_label),
                "model_version": row.model_version,
                "scored_at": scored_at_value,
            }
        self._records = records

    def get(self, user_id: str) -> dict[str, Any] | None:
        self.load()
        assert self._records is not None
        return self._records.get(user_id)

    @property
    def record_count(self) -> int | None:
        if self._records is None:
            return None
        return len(self._records)
