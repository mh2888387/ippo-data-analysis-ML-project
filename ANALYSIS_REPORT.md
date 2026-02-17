# IPPO Waste Analysis – Reviewed & Upgraded Deliverable

This project now includes a **reproducible analysis pipeline** (not only a narrative summary) so the company can re-run preprocessing and analytics on every new monthly file.

## What was missing before (now fixed)
- Analysis was mostly notebook-only and hard to re-run consistently.
- Preprocessing logic was not packaged as a reusable workflow.
- No automatic export of clean datasets + KPI summary tables.

## What is now implemented
1. `src/waste_analysis_pipeline.py`
   - End-to-end preprocessing from raw Excel structure.
   - Numeric conversion and null handling.
   - Text normalization for operator/line fields.
   - Line-name standardization (e.g., `سليتر 2` -> `سليتر2`).
   - Outlier removal per line using IQR.
   - KPI summaries by line/operator/operator-line.
2. `run_analysis.py`
   - CLI runner to execute all preprocessing + analysis in one command.
3. Automatic output artifacts in `outputs/`
   - `cleaned_data.csv`
   - `line_summary.csv`
   - `operator_summary.csv`
   - `line_operator_summary.csv`
   - `top_waste_events.csv`
   - `MANAGEMENT_REPORT.md`

## How to run
```bash
python run_analysis.py --input "<path_to_excel_file>" --out outputs
```

Optional: skip IQR outlier filtering
```bash
python run_analysis.py --input "<path_to_excel_file>" --skip-iqr-outlier-removal
```

## Business value for the client
- The company now has a **repeatable monthly process** for waste analysis.
- Management receives both:
  - detailed data outputs for engineers/analysts.
  - an executive markdown summary for decisions.
- This removes dependency on manual notebook editing and makes KPI tracking consistent.
