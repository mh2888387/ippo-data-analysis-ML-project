#!/usr/bin/env python3
from __future__ import annotations

import argparse

from src.waste_analysis_pipeline import load_and_preprocess, remove_outliers_iqr_per_line
from src.waste_ml_models import save_model_artifacts, train_and_compare_models


def main() -> None:
    parser = argparse.ArgumentParser(description="Train and compare ML models for waste prediction")
    parser.add_argument("--input", required=True, help="Path to source Excel file")
    parser.add_argument("--out", default="outputs", help="Output directory")
    parser.add_argument("--random-state", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument(
        "--skip-iqr-outlier-removal",
        action="store_true",
        help="Skip per-line IQR outlier removal before model training",
    )
    args = parser.parse_args()

    df = load_and_preprocess(args.input)
    if not args.skip_iqr_outlier_removal:
        df = remove_outliers_iqr_per_line(df)

    metrics, best_model = train_and_compare_models(df, random_state=args.random_state)
    metrics_path, model_path, report_path = save_model_artifacts(metrics, best_model, args.out)

    print("Model training completed successfully")
    print(f"Metrics: {metrics_path}")
    print(f"Best model: {model_path}")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
