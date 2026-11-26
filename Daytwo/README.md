# Wine Chemistry Outlier Audit

**Week 11 · Class 2 Independent Lab**

## Project overview

This project audits chemical measurements from the teaching version of the UCI Wine classification dataset. The supplied teaching CSV contains 178 observations and includes three intentionally modified values. It is not an untouched public download.

The audit focuses on `malic_acid` and `proline`. The `target` column is a class identifier and is not treated as a measurement for outlier detection.

## Files

| File | Purpose |
|---|---|
| `outlier_audit.py` | Validates the input, calculates flags, separates invalid-domain rows and writes outputs |
| `test_outlier_audit.py` | Independent unit tests for the core audit logic |
| `wine_quality_case_PUBLIC_DERIVED.csv` | Input teaching dataset |
| `retained_flagged.csv` | Records that pass the specified domain checks, including flagged records pending review |
| `quarantined_records.csv` | Records that fail one or more explicitly documented domain checks |
| `quality_summary.csv` | Counts for input, retained, quarantined and measurement flags |
| `requirements.txt` | Python package dependencies |

## Method

### 1. Input validation

The program checks for these required columns:

- `sample_id`
- `alcohol`
- `malic_acid`
- `color_intensity`
- `proline`
- `target`

It raises a clear `ValueError` if any required column is missing.

### 2. Statistical outlier flags

The original observations are preserved. Two independent statistical methods are applied to both `malic_acid` and `proline`.

**Z-score**

The population standard deviation is used (`ddof=0`). A value is flagged when:

`abs(Z-score) > 3`

If a measurement has zero variance, its Z-score flags are all set to `False`, because division by zero would not produce meaningful Z-scores.

**Interquartile range (IQR)**

Pandas' default quantile calculation is used:

- `IQR = Q3 - Q1`
- Lower fence = `Q1 - 1.5 * IQR`
- Upper fence = `Q3 + 1.5 * IQR`

Values below the lower fence or above the upper fence are flagged.

Missing values are not marked as statistical outliers by these calculations. The explicitly stated malic-acid domain rule separately identifies missing values as invalid.

### 3. Domain sanity checks

The lab guide specifies these instructional validation rules:

- `proline <= 0` is invalid.
- Negative or missing `malic_acid` is invalid.

These are the assignment's domain rules, not universal scientific bounds.

### 4. Review and quarantine decisions

`review_needed` is `True` when a row has any statistical outlier flag or a domain-invalid flag.

Only rows failing the explicit domain sanity rules are quarantined. A statistical outlier by itself remains in `retained_flagged.csv` for review.

The original `sample_id` and raw measurement values are not overwritten.

## Outputs

Running the program creates:

- `retained_flagged.csv`
- `quarantined_records.csv`
- `quality_summary.csv`

The summary includes total input, retained and quarantined rows, separate Z-score and IQR flag counts for both measurements, domain-invalid counts and review-needed count.

## Why a rare high reading may be legitimate

A rare high proline reading may reflect a genuine difference in grape variety, growing conditions, ripeness or the sample itself. Statistical rarity does not prove that a measurement is erroneous. The lab therefore keeps statistical outliers for review unless they violate an explicit domain sanity rule.

## Limitations

- The stated domain rules are instructional checks, not comprehensive scientific validation.
- Z-score results can be affected by skewness and extreme values because they use the mean and standard deviation.
- IQR fences are more resistant to extreme values, but they still identify statistical unusualness rather than proving an error.
- Missing `proline` is not quarantined by the stated `proline <= 0` rule; missing `malic_acid` is quarantined because the guide explicitly says it is invalid.
- The audit does not automatically correct or delete unusual measurements.

## Setup and run commands

Use Python 3.10 or later. From this project folder, create and activate a virtual environment if desired.

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python outlier_audit.py
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python outlier_audit.py
```

To supply a different input path:

```bash
python outlier_audit.py path/to/input.csv
```

To choose an output directory:

```bash
python outlier_audit.py path/to/input.csv --output-dir path/to/output
```

The default input path is the teaching CSV beside the Python script. The default output directory is the project folder. The program works offline after dependencies are installed.

## Test commands

Run the unit tests from this folder:

```bash
python -m unittest -v
```

The tests cover missing-column validation, domain quarantine, retention of statistical outliers, zero-variance handling, preservation of raw values and summary totals.

## Git branch and pull request

Use the required branch name:

```bash
git switch -c feature/week11-class02-outliers
git add outlier_audit.py test_outlier_audit.py README.md requirements.txt
git add wine_quality_case_PUBLIC_DERIVED.csv retained_flagged.csv quarantined_records.csv quality_summary.csv
git commit -m "Complete wine chemistry outlier audit"
git push -u origin feature/week11-class02-outliers
```

Then open an individual Pull Request on GitHub and submit its URL.

## Data source acknowledgement

The teaching dataset is derived from the UCI Machine Learning Repository Wine dataset and is distributed with scikit-learn. The teaching copy used for this lab contains intentionally modified instructional values; it should not be described as an untouched public download.

- UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/109/wine
- scikit-learn documentation: https://scikit-learn.org/stable/datasets/toy_dataset.html#wine-dataset
