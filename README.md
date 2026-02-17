# ippo-data-analysis-ML-project

## Project files
- `ipp_waste.ipynb`: original exploratory notebook.
- `src/waste_analysis_pipeline.py`: reusable preprocessing + analysis pipeline.
- `src/waste_ml_models.py`: machine learning model training/comparison for waste prediction.
- `run_analysis.py`: command-line entrypoint for preprocessing + KPI outputs.
- `run_ml_training.py`: command-line entrypoint for model training/evaluation.
- `ANALYSIS_REPORT.md`: delivery summary for client and management.

## Run full preprocessing + descriptive analysis
```bash
python run_analysis.py --input "<path_to_excel_file>" --out outputs
```

## Train ML models to predict waste
```bash
python run_ml_training.py --input "<path_to_excel_file>" --out outputs
```

## Output artifacts
The scripts write artifacts in `outputs/`, including:
- cleaned datasets and KPI summaries (`*.csv`)
- management report (`MANAGEMENT_REPORT.md`)
- model metrics (`model_metrics.csv`)
- saved best model (`best_waste_model.joblib`)
- model comparison report (`ML_MODEL_REPORT.md`)
