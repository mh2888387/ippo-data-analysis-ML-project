#!/usr/bin/env python3
from __future__ import annotations

import argparse

from src.waste_analysis_pipeline import (
    build_summaries,
    load_and_preprocess,
    remove_outliers_iqr_per_line,
    render_management_report,
    write_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full waste preprocessing + analysis pipeline")
    parser.add_argument("--input", required=True, help="Path to source Excel file")
    parser.add_argument("--out", default="outputs", help="Output directory for CSV summaries and report")
    parser.add_argument(
        "--skip-iqr-outlier-removal",
        action="store_true",
        help="Skip per-line IQR outlier removal step",
    )
    args = parser.parse_args()

    df = load_and_preprocess(args.input)
    if not args.skip_iqr_outlier_removal:
        df = remove_outliers_iqr_per_line(df)

    outputs = build_summaries(df)
    write_outputs(outputs, args.out)
    report_path = render_management_report(outputs, args.out)

    print("Analysis completed successfully")
    print(f"Cleaned records: {len(outputs.cleaned)}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
