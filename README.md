# ippo-data-analysis-ML-project

## Project files
- `ipp_waste.ipynb`: original exploratory notebook.
- `src/waste_analysis_pipeline.py`: reusable preprocessing + analysis pipeline.
- `run_analysis.py`: command-line entrypoint.
- `ANALYSIS_REPORT.md`: delivery summary for client and management.

## Run full analysis
```bash
python run_analysis.py --input "<path_to_excel_file>" --out outputs
```

Outputs are written to `outputs/`.
