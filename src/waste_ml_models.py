from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from joblib import dump
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import ExtraTreesRegressor, GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET_COLUMN = "بالكيلو"
CATEGORICAL_COLUMNS = ["الفني", "خط الانتاج", "الجوده", "الورديه"]
NUMERIC_COLUMNS = ["الوزن", "فرز تاني", "محلي", "تصدير", "السمك", "المقاس"]


@dataclass
class ModelResult:
    name: str
    mae: float
    rmse: float
    r2: float
    cv_rmse_mean: float
    cv_rmse_std: float


def _feature_columns(df: pd.DataFrame) -> tuple[list[str], list[str]]:
    numeric = [col for col in NUMERIC_COLUMNS if col in df.columns]
    categorical = [col for col in CATEGORICAL_COLUMNS if col in df.columns]
    return numeric, categorical


def build_preprocessor(df: pd.DataFrame) -> ColumnTransformer:
    numeric, categorical = _feature_columns(df)

    num_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    cat_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numeric),
            ("cat", cat_pipeline, categorical),
        ],
        remainder="drop",
    )


def build_model_candidates(random_state: int = 42) -> dict[str, object]:
    return {
        "linear_regression": LinearRegression(),
        "ridge": Ridge(alpha=1.0),
        "random_forest": RandomForestRegressor(n_estimators=400, random_state=random_state, n_jobs=-1),
        "gradient_boosting": GradientBoostingRegressor(random_state=random_state),
        "extra_trees": ExtraTreesRegressor(n_estimators=500, random_state=random_state, n_jobs=-1),
    }


def _rmse(y_true: pd.Series, y_pred: pd.Series) -> float:
    return mean_squared_error(y_true, y_pred) ** 0.5


def train_and_compare_models(df: pd.DataFrame, random_state: int = 42) -> tuple[pd.DataFrame, Pipeline]:
    if TARGET_COLUMN not in df.columns:
        raise ValueError(f"Expected target column {TARGET_COLUMN!r} in dataframe")

    usable = df.dropna(subset=[TARGET_COLUMN]).copy()
    numeric, categorical = _feature_columns(usable)
    feature_cols = numeric + categorical
    if not feature_cols:
        raise ValueError("No feature columns available for model training")

    X = usable[feature_cols]
    y = usable[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=random_state,
    )

    preprocessor = build_preprocessor(usable)
    candidates = build_model_candidates(random_state=random_state)
    cv = KFold(n_splits=5, shuffle=True, random_state=random_state)

    results: list[ModelResult] = []
    fitted_pipelines: dict[str, Pipeline] = {}

    for name, estimator in candidates.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", estimator),
            ]
        )
        pipeline.fit(X_train, y_train)
        preds = pipeline.predict(X_test)

        neg_mse_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="neg_mean_squared_error")
        rmse_scores = (-neg_mse_scores) ** 0.5

        results.append(
            ModelResult(
                name=name,
                mae=mean_absolute_error(y_test, preds),
                rmse=_rmse(y_test, preds),
                r2=r2_score(y_test, preds),
                cv_rmse_mean=float(rmse_scores.mean()),
                cv_rmse_std=float(rmse_scores.std()),
            )
        )
        fitted_pipelines[name] = pipeline

    results_df = pd.DataFrame([r.__dict__ for r in results]).sort_values("rmse", ascending=True)
    best_model_name = results_df.iloc[0]["name"]
    best_pipeline = fitted_pipelines[best_model_name]
    return results_df, best_pipeline


def save_model_artifacts(
    metrics: pd.DataFrame,
    best_model: Pipeline,
    out_dir: str | Path,
) -> tuple[Path, Path, Path]:
    output_dir = Path(out_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = output_dir / "model_metrics.csv"
    best_model_path = output_dir / "best_waste_model.joblib"
    report_path = output_dir / "ML_MODEL_REPORT.md"

    metrics.to_csv(metrics_path, index=False)
    dump(best_model, best_model_path)

    report = [
        "# Waste Prediction Model Report",
        "",
        "## Candidate models",
        metrics.to_markdown(index=False),
        "",
        f"Best model by RMSE: **{metrics.iloc[0]['name']}**",
        "",
        "## Interpretation",
        "- Lower MAE/RMSE means better waste prediction accuracy.",
        "- Positive R2 near 1 indicates stronger explanatory power.",
        "- Use the best saved model for monthly waste forecasting and scenario planning.",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")

    return metrics_path, best_model_path, report_path
