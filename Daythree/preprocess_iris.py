"""Week 11 Class 3: leakage-safe Iris feature preprocessing."""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = ["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"]
CATEGORICAL = ["collection_site", "instrument_type"]
LABEL = "species"
IDENTIFIER = "sample_id"

def build_preprocessor():
    numeric = Pipeline([("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler())])
    categorical = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                            ("onehot", OneHotEncoder(handle_unknown="ignore"))])
    return ColumnTransformer([("numeric", numeric, NUMERIC),
                              ("categorical", categorical, CATEGORICAL)],
                             remainder="drop", verbose_feature_names_out=False)

def _dense(values):
    return values.toarray() if hasattr(values, "toarray") else np.asarray(values)

def prepare_dataset(input_csv):
    data = pd.read_csv(input_csv)
    required = [IDENTIFIER, *NUMERIC, LABEL, *CATEGORICAL]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    if data.empty or data[LABEL].isna().any():
        raise ValueError("Dataset must contain records and a complete species target.")
    X = data[NUMERIC + CATEGORICAL].copy()
    y = data[LABEL].copy()
    X_train, X_test, _, _ = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    transformer = build_preprocessor()
    train_values = _dense(transformer.fit_transform(X_train))
    test_values = _dense(transformer.transform(X_test))
    names = transformer.get_feature_names_out().tolist()
    train = pd.DataFrame(train_values, columns=names)
    test = pd.DataFrame(test_values, columns=names)
    if train.columns.tolist() != test.columns.tolist():
        raise RuntimeError("Train/test feature columns do not match.")
    if LABEL in names or IDENTIFIER in names:
        raise RuntimeError("Target or identifier leaked into features.")
    if not np.isfinite(train.to_numpy(dtype=float)).all() or not np.isfinite(test.to_numpy(dtype=float)).all():
        raise RuntimeError("Transformed data contains non-finite values.")
    report = {"source_rows": len(data), "training_rows": len(train),
              "test_rows": len(test), "transformed_features": len(names),
              "missing_source_cells": int(data.isna().sum().sum())}
    return transformer, train, test, report

def write_outputs(train_df, test_df, report, output_dir):
    folder = Path(output_dir)
    folder.mkdir(parents=True, exist_ok=True)
    train_df.to_csv(folder / "train_features.csv", index=False)
    test_df.to_csv(folder / "test_features.csv", index=False)
    pd.DataFrame([report], columns=["source_rows", "training_rows", "test_rows",
                                    "transformed_features", "missing_source_cells"]).to_csv(
                                        folder / "data_quality_summary.csv", index=False)

def main():
    parser = argparse.ArgumentParser(description="Leakage-safe Iris preprocessing")
    parser.add_argument("--input", default="iris_preprocessing_case_PUBLIC_DERIVED.csv")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    _, train, test, report = prepare_dataset(args.input)
    write_outputs(train, test, report, args.output_dir)
    print("Preprocessing completed")
    for key, value in report.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
