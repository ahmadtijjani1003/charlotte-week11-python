"""Wine Chemistry Outlier Audit — Week 11, Class 2.

Run from this folder:
    python outlier_audit.py
Or provide a CSV path:
    python outlier_audit.py path/to/input.csv
"""
from pathlib import Path
import argparse
import pandas as pd

REQUIRED = [
    "sample_id", "alcohol", "malic_acid",
    "color_intensity", "proline", "target"
]
MEASUREMENTS = ["malic_acid", "proline"]


def _z_score_flags(series: pd.Series) -> pd.Series:
    """Flag observations with absolute population Z-score greater than 3.

    Missing values are not flagged by this statistical test. A zero-variance
    series has no meaningful Z-scores, so it returns False for every row.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    mean = numeric.mean()
    std = numeric.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(False, index=series.index, dtype=bool)
    z_scores = (numeric - mean) / std
    return z_scores.abs().gt(3).fillna(False).astype(bool)


def _iqr_flags(series: pd.Series) -> pd.Series:
    """Flag values outside Q1 - 1.5*IQR and Q3 + 1.5*IQR.

    Uses Pandas' default quantile interpolation. Missing values are not
    statistically flagged.
    """
    numeric = pd.to_numeric(series, errors="coerce")
    q1 = numeric.quantile(0.25)
    q3 = numeric.quantile(0.75)
    if pd.isna(q1) or pd.isna(q3):
        return pd.Series(False, index=series.index, dtype=bool)
    iqr = q3 - q1
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    return (numeric.lt(lower) | numeric.gt(upper)).fillna(False).astype(bool)


def audit_data(data: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Return retained, quarantined and quality summary DataFrames.

    Original columns and values are preserved. Statistical flags trigger
    review, not quarantine. Only the stated domain rules trigger quarantine:
    proline <= 0, and malic_acid negative or missing.
    """
    if not isinstance(data, pd.DataFrame):
        raise TypeError("data must be a pandas DataFrame")

    missing_columns = [column for column in REQUIRED if column not in data.columns]
    if missing_columns:
        raise ValueError(
            "Input data is missing required column(s): "
            + ", ".join(missing_columns)
        )

    audited = data.copy(deep=True)

    for measurement in MEASUREMENTS:
        audited[f"{measurement}_z_flag"] = _z_score_flags(audited[measurement])
        audited[f"{measurement}_iqr_flag"] = _iqr_flags(audited[measurement])

    # Explicit instructional domain rules from the lab guide.
    audited["proline_invalid"] = (
        pd.to_numeric(audited["proline"], errors="coerce").le(0)
    ).fillna(False)
    malic_numeric = pd.to_numeric(audited["malic_acid"], errors="coerce")
    audited["malic_acid_invalid"] = (
        malic_numeric.lt(0) | malic_numeric.isna()
    )
    audited["domain_invalid"] = (
        audited["proline_invalid"] | audited["malic_acid_invalid"]
    )

    statistical_or_validity_flags = [
        "malic_acid_z_flag",
        "malic_acid_iqr_flag",
        "proline_z_flag",
        "proline_iqr_flag",
        "domain_invalid",
    ]
    audited["review_needed"] = audited[statistical_or_validity_flags].any(axis=1)

    quarantined = audited.loc[audited["domain_invalid"]].copy()
    retained = audited.loc[~audited["domain_invalid"]].copy()

    summary = pd.DataFrame([{
        "total_input": len(audited),
        "retained": len(retained),
        "quarantined": len(quarantined),
        "malic_acid_z_flags": int(audited["malic_acid_z_flag"].sum()),
        "malic_acid_iqr_flags": int(audited["malic_acid_iqr_flag"].sum()),
        "proline_z_flags": int(audited["proline_z_flag"].sum()),
        "proline_iqr_flags": int(audited["proline_iqr_flag"].sum()),
        "malic_acid_invalid": int(audited["malic_acid_invalid"].sum()),
        "proline_invalid": int(audited["proline_invalid"].sum()),
        "review_needed": int(audited["review_needed"].sum()),
    }])

    return {
        "retained": retained,
        "quarantined": quarantined,
        "summary": summary,
    }


def write_outputs(results: dict[str, pd.DataFrame], output_dir: Path) -> None:
    """Write the three required CSV deliverables to output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results["retained"].to_csv(output_dir / "retained_flagged.csv", index=False)
    results["quarantined"].to_csv(output_dir / "quarantined_records.csv", index=False)
    results["summary"].to_csv(output_dir / "quality_summary.csv", index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit wine chemistry outliers.")
    parser.add_argument(
        "csv_path",
        nargs="?",
        default=str(Path(__file__).with_name("wine_quality_case_PUBLIC_DERIVED.csv")),
        help="Input CSV path (default: CSV beside this script).",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).parent),
        help="Directory for the three output CSV files (default: script folder).",
    )
    args = parser.parse_args()

    input_path = Path(args.csv_path)
    if not input_path.exists():
        raise FileNotFoundError(f"Input CSV was not found: {input_path}")

    data = pd.read_csv(input_path)
    results = audit_data(data)
    write_outputs(results, Path(args.output_dir))

    print("Wine chemistry audit completed.")
    print(f"Input rows: {len(data)}")
    print(f"Retained rows: {len(results['retained'])}")
    print(f"Quarantined rows: {len(results['quarantined'])}")
    print(f"Outputs saved to: {Path(args.output_dir).resolve()}")


if __name__ == "__main__":
    main()
