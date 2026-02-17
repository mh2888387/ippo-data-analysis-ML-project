from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd


EXPECTED_COLUMNS = [
    "بالكيلو",
    "الوزن",
    "فرز تاني",
    "محلي",
    "تصدير",
    "السمك",
    "المقاس",
    "الاوردر",
    "الفني",
    "الجوده",
    "خط الانتاج",
    "الورديه",
]

TEXT_COLUMNS = ["الفني", "الجوده", "خط الانتاج", "الورديه", "الاوردر"]
NUMERIC_COLUMNS = ["بالكيلو", "الوزن", "فرز تاني", "محلي", "تصدير", "السمك", "المقاس"]


LINE_NORMALIZATION = {
    "سليتر 1": "سليتر1",
    "سليتر 2": "سليتر2",
    "تناية 1": "تناية1",
    "تناية 2": "تناية2",
    "تناية 3": "تناية3",
    "تناية 4": "تناية4",
    "تناية1 ": "تناية1",
}


@dataclass
class AnalysisOutputs:
    cleaned: pd.DataFrame
    line_summary: pd.DataFrame
    operator_summary: pd.DataFrame
    line_operator_summary: pd.DataFrame
    top_waste_events: pd.DataFrame


def _normalize_whitespace(value: str) -> str:
    return " ".join(str(value).strip().split())


def normalize_text_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
    for col in columns:
        if col in df.columns:
            df[col] = df[col].astype(str).map(_normalize_whitespace)
            df[col] = df[col].replace({"nan": pd.NA, "": pd.NA})

    if "خط الانتاج" in df.columns:
        df["خط الانتاج"] = df["خط الانتاج"].replace(LINE_NORMALIZATION)

    return df


def load_and_preprocess(path: str | Path) -> pd.DataFrame:
    """Load raw Excel and convert to a clean, analysis-ready DataFrame."""
    raw = pd.read_excel(path, header=None)

    # Raw file has metadata columns and a shifted header in row 2.
    working = raw.drop(columns=[0, 1, 9, 15], errors="ignore").copy()
    header_row = working.iloc[2].loc[1:]
    working.columns = header_row

    # Data starts after row 27 in current template.
    data = working.drop(index=working.index[0:27]).copy()

    # keep only known business columns, if they exist.
    available = [c for c in EXPECTED_COLUMNS if c in data.columns]
    data = data[available].copy()

    # Type cleanup.
    for col in NUMERIC_COLUMNS:
        if col in data.columns:
            data[col] = pd.to_numeric(data[col], errors="coerce")

    # Mandatory columns for analysis.
    must_have = [c for c in ["بالكيلو", "الفني", "خط الانتاج"] if c in data.columns]
    data = data.dropna(subset=must_have)

    data = normalize_text_columns(data, TEXT_COLUMNS)

    # Remove physically impossible or placeholder values.
    if "بالكيلو" in data.columns:
        data = data[(data["بالكيلو"] >= 0) & (data["بالكيلو"] < 400)].copy()

    return data


def remove_outliers_iqr_per_line(df: pd.DataFrame, value_col: str = "بالكيلو") -> pd.DataFrame:
    """Apply IQR outlier filtering per production line."""
    if value_col not in df.columns or "خط الانتاج" not in df.columns:
        return df.copy()

    kept_chunks: list[pd.DataFrame] = []
    for _, grp in df.groupby("خط الانتاج", dropna=False):
        if len(grp) < 4:
            kept_chunks.append(grp)
            continue
        q1 = grp[value_col].quantile(0.25)
        q3 = grp[value_col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        kept = grp[(grp[value_col] >= lower) & (grp[value_col] <= upper)]
        kept_chunks.append(kept)

    return pd.concat(kept_chunks, ignore_index=True)


def build_summaries(df: pd.DataFrame) -> AnalysisOutputs:
    line_summary = (
        df.groupby("خط الانتاج", as_index=False)["بالكيلو"]
        .agg(["mean", "median", "std", "count", "min", "max"])
        .reset_index()
        .sort_values("mean", ascending=False)
    )

    operator_summary = (
        df.groupby("الفني", as_index=False)["بالكيلو"]
        .agg(["mean", "median", "count"])
        .reset_index()
        .rename(columns={"mean": "avg_waste", "count": "records"})
        .sort_values(["avg_waste", "records"], ascending=[False, False])
    )

    line_operator_summary = (
        df.groupby(["خط الانتاج", "الفني"], as_index=False)["بالكيلو"]
        .agg(["mean", "count"])
        .reset_index()
        .rename(columns={"mean": "avg_waste", "count": "records"})
        .sort_values("avg_waste", ascending=False)
    )

    top_waste_events = (
        df.sort_values("بالكيلو", ascending=False)
        .head(25)
        .loc[:, [c for c in ["بالكيلو", "خط الانتاج", "الفني", "الاوردر", "السمك", "المقاس"] if c in df.columns]]
    )

    return AnalysisOutputs(
        cleaned=df,
        line_summary=line_summary,
        operator_summary=operator_summary,
        line_operator_summary=line_operator_summary,
        top_waste_events=top_waste_events,
    )


def write_outputs(outputs: AnalysisOutputs, out_dir: str | Path) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    outputs.cleaned.to_csv(out_path / "cleaned_data.csv", index=False)
    outputs.line_summary.to_csv(out_path / "line_summary.csv", index=False)
    outputs.operator_summary.to_csv(out_path / "operator_summary.csv", index=False)
    outputs.line_operator_summary.to_csv(out_path / "line_operator_summary.csv", index=False)
    outputs.top_waste_events.to_csv(out_path / "top_waste_events.csv", index=False)


def render_management_report(outputs: AnalysisOutputs, out_dir: str | Path) -> Path:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    top_lines = outputs.line_summary.head(5)
    top_ops = outputs.operator_summary.head(10)

    report = [
        "# Management Waste Report (Auto-generated)",
        "",
        f"- Total cleaned records: **{len(outputs.cleaned)}**",
        f"- Distinct lines: **{outputs.cleaned['خط الانتاج'].nunique()}**",
        f"- Distinct operators: **{outputs.cleaned['الفني'].nunique()}**",
        "",
        "## Highest-waste lines (Top 5)",
        top_lines.to_markdown(index=False),
        "",
        "## Highest-waste operators (Top 10)",
        top_ops.to_markdown(index=False),
        "",
        "## Recommended next actions",
        "1. Start maintenance + setup validation on top 2 waste lines.",
        "2. Review operator-line pairs with high avg_waste and high records together.",
        "3. Track weekly trend of mean/median waste by line after interventions.",
    ]

    path = out_path / "MANAGEMENT_REPORT.md"
    path.write_text("\n".join(report), encoding="utf-8")
    return path
