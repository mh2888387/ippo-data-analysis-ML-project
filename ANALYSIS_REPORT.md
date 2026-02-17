# IPPO Waste Analysis + Machine Learning Deliverable

This project now includes a complete technical workflow for:
1. Data preprocessing and KPI analysis.
2. Machine learning model training and comparison to predict waste (`بالكيلو`).

## 1) Data preprocessing and analysis completed
The pipeline in `src/waste_analysis_pipeline.py` performs:
- Raw Excel ingestion for shifted-template source files.
- Header reconstruction and non-data row removal.
- Numeric coercion and required-field filtering.
- Text cleanup for operator/line names.
- Line name normalization (`سليتر 2` → `سليتر2`, etc.).
- Per-line IQR outlier removal.
- Summary outputs by line, operator, and line-operator pair.

## 2) Machine learning models implemented
The module `src/waste_ml_models.py` trains multiple suitable regression models for waste prediction:
- Linear Regression
- Ridge Regression
- Random Forest Regressor
- Gradient Boosting Regressor
- Extra Trees Regressor

### Modeling approach
- Target: `بالكيلو` (waste in kg).
- Features: numeric process variables (`الوزن`, `فرز تاني`, `محلي`, `تصدير`, `السمك`, `المقاس`) and categorical variables (`الفني`, `خط الانتاج`, `الجوده`, `الورديه`) when available.
- Preprocessing inside model pipeline:
  - numeric imputation + scaling
  - categorical imputation + one-hot encoding
- Validation:
  - train/test split metrics: MAE, RMSE, R²
  - 5-fold CV RMSE mean/std
- Best model selected by lowest RMSE and exported.

## 3) Commands to run
### A) Preprocessing + descriptive analysis
```bash
python run_analysis.py --input "<path_to_excel_file>" --out outputs
```

### B) Train and compare ML models
```bash
python run_ml_training.py --input "<path_to_excel_file>" --out outputs
```

## 4) Client-facing outputs generated
After running scripts, the company gets:
- `cleaned_data.csv`
- `line_summary.csv`
- `operator_summary.csv`
- `line_operator_summary.csv`
- `top_waste_events.csv`
- `MANAGEMENT_REPORT.md`
- `model_metrics.csv`
- `best_waste_model.joblib`
- `ML_MODEL_REPORT.md`

## 5) Business benefit to company
- Predict expected waste before execution and flag high-risk conditions.
- Compare expected vs actual waste to identify process drift.
- Prioritize maintenance/training on lines and operator-line combinations with recurring high predicted waste.
- Build a monthly forecasting workflow for material-loss reduction.
