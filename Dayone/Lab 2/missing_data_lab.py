
from pathlib import Path
import pandas as pd

DATA = Path(__file__).with_name("gapminder_instructional_missing.csv")
OUTPUT = Path(__file__).with_name("outputs")
REQUIRED = {"country", "continent", "year", "lifeExp", "pop", "gdpPercap"}
TARGET_COLUMNS = ["continent", "lifeExp", "gdpPercap"]
NUMERIC_COLUMNS = ["year", "lifeExp", "pop", "gdpPercap"]
EXPECTED_ROWS = 96


def load_and_validate(path: Path) -> pd.DataFrame:
    """Read the CSV and validate its required schema and basic data rules."""
    try:
        df = pd.read_csv(path)
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Could not find the input CSV: {path}\n"
        ) from exc
    except Exception as exc:
        raise ValueError(f"Could not read the CSV file: {exc}") from exc

    missing_columns = REQUIRED - set(df.columns)
    if missing_columns:
        extra_columns = set(df.columns) - REQUIRED
        raise ValueError(
            "The input file does not have the required six columns. "
            f"Missing columns: {sorted(missing_columns)}. "
            f"Columns found: {list(df.columns)}. "
            f"Unexpected columns: {list(extra_columns)}. "
        )

    if len(df) != EXPECTED_ROWS:
        raise ValueError(
            f"Expected {EXPECTED_ROWS} data rows, but found {len(df)}."
        )

    if df[["country", "year"]].isna().any().any():
        raise ValueError("The country/year key contains missing values.")

    duplicate_keys = df.duplicated(subset=["country", "year"], keep=False)
    if duplicate_keys.any():
        examples = df.loc[duplicate_keys, ["country", "year"]].head(5)
        raise ValueError(
            "Each country/year combination must be unique. "
            f"Example duplicate keys:\n{examples.to_string(index=False)}"
        )

    for column in NUMERIC_COLUMNS:
        if not pd.api.types.is_numeric_dtype(df[column]):
            raise ValueError(f"Column '{column}' must contain numeric values.")

    if df["pop"].isna().any() or (df["pop"] <= 0).any():
        raise ValueError("Every population value must be present and greater than zero.")

    return df


def missingness_report(df: pd.DataFrame) -> pd.DataFrame:
    total_rows = len(df)
    if total_rows == 0:
        raise ValueError("Cannot create a missingness report for an empty dataset.")

    report = pd.DataFrame({
        "column": df.columns,
        "missing_count": [int(df[column].isna().sum()) for column in df.columns],
        "missing_pct": [
            round(float(df[column].isna().sum() / total_rows * 100), 2)
            for column in df.columns
        ],
    })
    return report


def _fill_continent_from_same_country(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()

    continent_by_country = {}
    for country, group in result.groupby("country", dropna=False):
        observed = group["continent"].dropna().unique()
        if len(observed) > 1:
            raise ValueError(
                f"Country '{country}' has conflicting observed continent labels: "
                f"{list(observed)}. Cannot safely infer its missing continent."
            )
        if len(observed) == 1:
            continent_by_country[country] = observed[0]

    missing_continent = result["continent"].isna()
    result.loc[missing_continent, "continent"] = (
        result.loc[missing_continent, "country"].map(continent_by_country)
    )

    if result["continent"].isna().any():
        unresolved = result.loc[
            result["continent"].isna(), "country"
        ].drop_duplicates().tolist()
        raise ValueError(
            f"observed row for the same country: {unresolved}"
        )

    return result


def _impute_numeric_by_continent(df: pd.DataFrame, column: str) -> pd.Series:

    original = df[column]
    global_median = original.median(skipna=True)

    if pd.isna(global_median):
        raise ValueError(
            f"Cannot impute '{column}': the entire column has no observed values."
        )

    continent_medians = df.groupby("continent")[column].transform("median")
    filled = original.fillna(continent_medians)
    filled = filled.fillna(global_median)
    return filled


def impute_data(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["lifeExp_was_missing"] = result["lifeExp"].isna()
    result["gdpPercap_was_missing"] = result["gdpPercap"].isna()
    result = _fill_continent_from_same_country(result)
    result["lifeExp"] = _impute_numeric_by_continent(result, "lifeExp")
    result["gdpPercap"] = _impute_numeric_by_continent(result, "gdpPercap")

    return result


def validate_cleaned_data(source: pd.DataFrame, cleaned: pd.DataFrame) -> None:
    if len(cleaned) != len(source):
        raise ValueError(
            f"Row count changed: source={len(source)}, cleaned={len(cleaned)}."
        )

    if not cleaned[["country", "year"]].equals(source[["country", "year"]]):
        raise ValueError("Country/year rows or their order changed during cleaning.")

    unresolved = cleaned[TARGET_COLUMNS].isna().sum()
    unresolved = unresolved[unresolved > 0]
    if not unresolved.empty:
        raise ValueError(
            "Unresolved missing values remain in target columns: "
            f"{unresolved.to_dict()}"
        )

    for column in ["lifeExp", "gdpPercap"]:
        observed_mask = source[column].notna()
        if not cleaned.loc[observed_mask, column].equals(
            source.loc[observed_mask, column]
        ):
            raise ValueError(
                f"Originally observed values in '{column}' were changed."
            )

    for flag in ["lifeExp_was_missing", "gdpPercap_was_missing"]:
        if cleaned[flag].dtype != bool:
            raise ValueError(f"'{flag}' must be a Boolean column.")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    source = load_and_validate(DATA)
    report = missingness_report(source)
    cleaned = impute_data(source)
    validate_cleaned_data(source, cleaned)

    report.to_csv(OUTPUT / "missingness_report.csv", index=False)
    cleaned.to_csv(OUTPUT / "imputed_gapminder.csv", index=False)

    print(f"Success: validated and processed {len(cleaned)} rows.")
    print("Created:")
    print(" -", OUTPUT / "missingness_report.csv")
    print(" -", OUTPUT / "imputed_gapminder.csv")


if __name__ == "__main__":
    main()
