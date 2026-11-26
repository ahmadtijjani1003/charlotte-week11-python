# Week 11 Class 3 — Botanical Measurement Preprocessing

## Overview
This solution prepares the supplied Iris measurement dataset for a downstream ML workflow. It performs preprocessing only; **no classifier is trained**.

The four measurement fields are numeric: `sepal_length_cm`, `sepal_width_cm`, `petal_length_cm`, and `petal_width_cm`. The categorical teaching fields are `collection_site` and `instrument_type`. `species` is the outcome label; `sample_id` is an identifier and is excluded from features.

## Dataset provenance and quality
The lab guide describes the four measurement columns as public-derived and the two categorical fields as synthetic teaching fields, with some values deliberately blanked out. The supplied CSV has 150 rows and 8 columns. It contains 11 missing source cells: 4 in `sepal_width_cm`, 3 in `petal_length_cm`, and 4 in `collection_site`.

The guide refers to `DATASET_CARD.md`, but that file was not among the supplied materials. This README therefore does not invent further provenance, licensing, or modification details.

## Installation
Python 3.9+ is recommended.

```bash
python -m pip install -r requirements.txt
```

## Run
```bash
python preprocess_iris.py --input iris_preprocessing_case_PUBLIC_DERIVED.csv --output-dir outputs
```

Run the included smoke tests:
```bash
python -m unittest test_student_smoke.py
```

## Preprocessing decisions
- Split first using `test_size=0.2`, `random_state=42`, and `stratify=y`.
- Numeric columns: median imputation, then `StandardScaler`.
- Categorical columns: most-frequent imputation, then `OneHotEncoder(handle_unknown="ignore")`.
- `ColumnTransformer` combines the two pipelines and drops any unlisted columns.
- Fit preprocessing only on training records; transform test records with that same fitted transformer.

Median imputation is less sensitive to extreme observations than mean imputation. Scaling places numeric features on comparable scales. Most-frequent imputation fills missing categories using the most common category in the training data. One-hot encoding represents categories as indicator columns; ignoring unknown categories prevents transform-time failure for a category not seen during fitting.

## Why reuse fitted training transformations?
Imputation values, scaling statistics, and one-hot category levels are learned from data. Fitting them on test data would allow information from the held-out set to influence preprocessing and would compromise an honest evaluation. The implementation therefore uses `fit_transform` on `X_train` only and `transform` on `X_test` with the already-fitted transformer.

## Output files
The `outputs/` folder contains:
- `train_features.csv`: 120 transformed rows, without `species` or `sample_id`.
- `test_features.csv`: 30 transformed rows with exactly the same feature names and order.
- `data_quality_summary.csv`: `source_rows`, `training_rows`, `test_rows`, `transformed_features`, and `missing_source_cells`.

The script checks column consistency, exclusion of target/identifier fields, and finite numeric outputs.

## Limitations
- `collection_site` and `instrument_type` are synthetic teaching fields, not verified real-world metadata.
- Imputed values are estimates, not recovered original measurements.
- Learned transformations reflect only the training split.
- This practical does not train or assess a prediction model.
- The dataset card was not supplied, so additional provenance details cannot be verified.
