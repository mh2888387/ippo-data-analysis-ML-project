# ippo-data-analysis-ML-project

This project is now fully notebook-based for Google Colab.

## Main file
- `ipp_waste.ipynb` → contains full preprocessing, data analysis, ML model training/comparison, and output export.

## Where to find model accuracies
- Run the ML section in `ipp_waste.ipynb`.
- Check the `metrics_df` output table.
- Accuracy is provided for both targets:
  - `Accuracy_الجوده`
  - `Accuracy_الفني`
  - `Accuracy_Mean` (average of both)
- The same metrics are exported to: `outputs/model_metrics.csv`.

## Usage
1. Open `ipp_waste.ipynb` in Google Colab.
2. Upload your Excel file.
3. Set `DATASET_PATH` in the notebook.
4. Run all cells.
