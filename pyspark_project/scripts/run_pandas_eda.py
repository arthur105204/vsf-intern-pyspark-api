from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pandas as pd
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[2]
DATASET_CANDIDATES = [
    ROOT / "pyspark_project" / "data" / "raw" / "bank_marketing" / "bank-full.csv",
    ROOT / "data" / "raw" / "bank-full.csv",
    ROOT / "pyspark_project" / "data" / "raw" / "bank-full.csv",
]
ZIP_CANDIDATES = [
    ROOT / "pyspark_project" / "data" / "raw" / "bank_marketing" / "bank.zip",
    ROOT / "data" / "raw" / "bank.zip",
]
FIGURES_DIR = ROOT / "pyspark_project" / "reports" / "figures"


def load_dataset() -> tuple[pd.DataFrame, str]:
    for path in DATASET_CANDIDATES:
        if path.exists():
            return pd.read_csv(path, sep=";"), str(path.relative_to(ROOT))

    for path in ZIP_CANDIDATES:
        if not path.exists():
            continue
        with zipfile.ZipFile(path) as zf:
            with zf.open("bank-full.csv") as fh:
                return pd.read_csv(fh, sep=";"), f"{path.relative_to(ROOT)}::bank-full.csv"

    raise FileNotFoundError("Bank Marketing bank-full.csv was not found.")


def font(size: int = 18) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype("arial.ttf", size)
    except OSError:
        return ImageFont.load_default()


def save_bar_chart(title: str, labels: list[str], values: list[float], path: Path, y_label: str) -> None:
    width, height = 1100, 700
    margin_left, margin_right, margin_top, margin_bottom = 95, 40, 90, 150
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    title_font = font(26)
    label_font = font(15)
    small_font = font(13)

    draw.text((margin_left, 25), title, fill="#111827", font=title_font)
    draw.line((margin_left, margin_top + plot_h, width - margin_right, margin_top + plot_h), fill="#374151", width=2)
    draw.line((margin_left, margin_top, margin_left, margin_top + plot_h), fill="#374151", width=2)
    draw.text((10, margin_top + plot_h // 2 - 20), y_label, fill="#374151", font=small_font)

    max_value = max(values) if values else 1
    bar_gap = 10
    bar_w = max(12, int((plot_w - bar_gap * (len(values) - 1)) / max(1, len(values))))
    colors = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#DC2626", "#0891B2", "#4B5563"]

    for idx, (label, value) in enumerate(zip(labels, values)):
        x0 = margin_left + idx * (bar_w + bar_gap)
        bar_h = int((value / max_value) * (plot_h - 20))
        y0 = margin_top + plot_h - bar_h
        x1 = x0 + bar_w
        y1 = margin_top + plot_h
        draw.rectangle((x0, y0, x1, y1), fill=colors[idx % len(colors)])
        draw.text((x0, max(95, y0 - 20)), f"{value:.2f}" if value < 100 else f"{int(value)}", fill="#111827", font=small_font)
        draw.text((x0, y1 + 12), label[:16], fill="#111827", font=label_font)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def save_hist_chart(title: str, series: pd.Series, path: Path, x_label: str) -> None:
    counts = pd.cut(series, bins=20).value_counts().sort_index()
    labels = [f"{int(interval.left)}-{int(interval.right)}" for interval in counts.index]
    save_bar_chart(title, labels, counts.astype(float).tolist(), path, "count")


def main() -> None:
    df, source = load_dataset()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    target_counts = df["y"].value_counts().reindex(["no", "yes"]).fillna(0)
    save_bar_chart(
        "Target distribution",
        target_counts.index.tolist(),
        target_counts.astype(float).tolist(),
        FIGURES_DIR / "01_target_distribution.png",
        "rows",
    )

    save_hist_chart("Age distribution", df["age"], FIGURES_DIR / "02_age_distribution.png", "age")

    job_counts = df["job"].value_counts().head(10)
    save_bar_chart(
        "Top job categories",
        job_counts.index.tolist(),
        job_counts.astype(float).tolist(),
        FIGURES_DIR / "03_top_job_categories.png",
        "rows",
    )

    balance = df["balance"].clip(lower=df["balance"].quantile(0.01), upper=df["balance"].quantile(0.99))
    save_hist_chart("Balance distribution, clipped p1-p99", balance, FIGURES_DIR / "04_balance_distribution.png", "balance")

    target_rate_by_job = (
        df.assign(label=(df["y"] == "yes").astype(int))
        .groupby("job")["label"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )
    save_bar_chart(
        "Target rate by job, top 10",
        target_rate_by_job.index.tolist(),
        (target_rate_by_job * 100).tolist(),
        FIGURES_DIR / "05_target_rate_by_job.png",
        "yes rate %",
    )

    categorical_cols = [
        c for c in df.columns
        if pd.api.types.is_string_dtype(df[c]) and c != "y"
    ]
    numeric_cols = [
        c for c in df.columns
        if pd.api.types.is_numeric_dtype(df[c]) and c != "y"
    ]
    unknown_counts = {
        col: int((df[col].astype(str).str.lower() == "unknown").sum())
        for col in categorical_cols
    }
    cardinality = {col: int(df[col].nunique(dropna=True)) for col in categorical_cols}

    summary = {
        "source": source,
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "target_distribution": target_counts.astype(int).to_dict(),
        "missing_values": {col: int(v) for col, v in df.isna().sum().items() if int(v) > 0},
        "unknown_counts": {col: count for col, count in unknown_counts.items() if count > 0},
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "categorical_cardinality": cardinality,
        "numeric_summary": df[numeric_cols].describe().round(3).to_dict(),
        "target_rate_by_job_pct": (target_rate_by_job * 100).round(2).to_dict(),
    }

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
