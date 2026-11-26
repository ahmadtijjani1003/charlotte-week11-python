# Week 11 Class 1 — Missing Data Lab

## Project overview

This project profiles and imputes deliberately missing values in a 96-row,
country/year Gapminder instructional dataset using Python and Pandas.

The work follows the Student Lab Guide. The missing values were deliberately
introduced for this classroom exercise; they must not be described as naturally
occurring missingness. Do not recover missing entries from a published clean copy.

## Files

```text
.
├── gapminder_instructional_missing.csv
├── missing_data_lab.py
├── requirements.txt
├── .gitignore
├── README.md
└── outputs/
    ├── missingness_report.csv
    └── imputed_gapminder.csv
```

Place the instructor-provided CSV beside `missing_data_lab.py`. The script
creates the `outputs` folder automatically.

## Setup and run

1. Install Python.
2. Open a terminal in this project folder.
3. (Recommended) Create and activate a virtual environment.
4. Install the dependency:

   ```bash
   pip install -r requirements.txt
   ```

5. Run:

   ```bash
   python missing_data_lab.py
   ```

The script uses a path relative to its own location; no hard-coded absolute
machine path is required.

## Implementation decisions

1. **Load and validate:** Pandas reads the CSV. The program checks the six
   required columns, exactly 96 rows, nonmissing country/year keys, unique
   country/year combinations, numeric analysis columns, and positive,
   nonmissing population values. Invalid input raises a useful error.
2. **Missingness report:** Every original source column receives a missing
   count and a missing percentage, rounded to two decimal places. The report
   is calculated before imputation.
3. **Missingness flags:** `lifeExp_was_missing` and
   `gdpPercap_was_missing` are created before any filling. They preserve the
   original missingness information as Boolean values.
4. **Continent:** A missing continent is filled only when other rows for the
   same country provide exactly one observed continent. Conflicting or absent
   evidence raises an error rather than guessing.
5. **Numeric imputation:** Missing `lifeExp` and `gdpPercap` values are filled
   using their continent-level medians. If a continent has no observed values
   for that measure, the global median is used as a fallback.
6. **Validation:** The program checks that row count and country/year order
   are unchanged, target columns have no remaining nulls, and originally
   observed numeric values are unchanged.
7. **Outputs:** The missingness report and completed data are written to the
   two required CSV paths under `outputs/`.

## Risks and limitations

- Median imputation reduces variation and can make observations look more alike.
- A continent median may not represent every country or year within that
  continent.
- Imputed values are estimates, not recovered facts; downstream analysis
  should retain and consider the missingness flags.
- The global-median fallback is less specific than a continent median.
- The exercise's missing values were deliberately blanked by the instructor.
  This artificial pattern should not be treated as evidence about how real
  Gapminder data become missing.
- The approach assumes that the other observations for a country provide a
  reliable continent label and that the continent-level distribution is a
  useful basis for imputation.

## Data-quality note about the uploaded workbook

The Excel workbook supplied alongside this work was inspected, but it does not
currently satisfy the documented input schema: its final column is headed
`42951.65309` rather than `gdpPercap`, and 20 country entries are literally
`country`. Therefore, it cannot be used as-is to produce trustworthy required
outputs. The script intentionally stops with a clear schema error instead of
guessing a column rename or inventing/replacing values. Obtain the instructor's
correct instructional CSV (or confirmation of the intended workbook) before
running the final analysis. Do not retrieve a clean public copy to fill the
exercise gaps.

## GitHub submission

From your individual Week 11 repository:

```bash
git switch -c feature/week11-class01-missing-data
git add missing_data_lab.py README.md requirements.txt .gitignore
git add outputs/
git commit -m "feat: profile and impute missing observations"
git push -u origin feature/week11-class01-missing-data
```

Then open a Pull Request from `feature/week11-class01-missing-data` into
`main`, and submit the PR link.

Do not commit `.venv`, credentials, or private data.
