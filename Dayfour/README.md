

\# Week 11 Class 4 — LAS and SCADA Feature Engineering

\## Data sources \& limitations
This project uses two fully synthetic educational datasets:
\- `well\_b\_synthetic.las`: simplified LAS 2.0 well-log data.

\- `scada\_synthetic.csv`: synthetic SCADA-style sensor readings.

Both datasets represent WELL-B and contain nine depth records from 1000 m to 1008 m at 1 m intervals.
\### Units

| Column | Unit |

|---|---|

| depth\_m | metres (m) |

| gamma\_api | API |

| density\_g\_cm3 | g/cm³ |

| pressure\_psi | psi |

| temperature\_c | °C |

| flow\_m3\_h | m³/h |

The LAS null convention is `-999.25`. It is treated as a missing value.
These datasets are synthetic and must not be treated as actual field measurements or used for operational engineering decisions.
The shared depth key is provided for this educational merge exercise. Real LAS and SCADA integration requires an appropriate depth/time reconciliation policy.

\## Running the project
The project uses Python with pandas, NumPy and lasio.
Install dependencies if they are not already installed:

```bash

pip install -r lab/requirements.txt

```
Run the feature pipeline from the repository root:

```bash
python lab/feature\_pipeline.py
```
Run automated tests:
```bash
python -m unittest discover -s lab -p "test\_\*.py" -v

```
\## Feature definitions

All features are calculated separately for each well, ordered by increasing depth.
| Feature | Formula / definition | Grouping and order | Missing-value policy |

|---|---|---|---|

| pressure\_missing\_flag | 1 if pressure is missing, otherwise 0 | Per row | Missing pressure is flagged |

| flow\_missing\_flag | 1 if flow is missing, otherwise 0 | Per row | Missing flow is flagged |

| pressure\_delta\_psi | Current pressure minus previous pressure | Per well, increasing depth | Missing if either required pressure is missing |

| pressure\_var\_3 | Population variance of the trailing three pressure readings | Per well, increasing depth | Requires three valid consecutive readings |

| temperature\_delta\_c | Current temperature minus previous temperature | Per well, increasing depth | Missing if either required temperature is missing |

| cumulative\_sampled\_flow | Running sum of recorded flow-rate values | Per well, increasing depth | Missing at a row with missing flow; later valid readings resume the sum |

| gamma\_density\_ratio | Gamma-ray value divided by bulk density | Per row | Missing if either input is missing |
The cumulative sampled flow is a simple running sum of recorded flow-rate values. It is not a physically integrated total volume. Calculating total volume requires integrating flow over time using the appropriate time intervals.
\## Missingness, imputation and leakage decisions
Missing pressure and flow values are preserved. They are not replaced with zero or estimated values.
Missingness indicator columns are included so that downstream analysis can identify records with missing sensor readings.
No future observations are used to calculate past pressure changes, rolling variance, temperature changes or cumulative flow. The rolling variance uses a trailing window of three observations.
\## Validation evidence
The pipeline produced the following results:
| Validation | Result |

|---|---:|

| SCADA input rows | 9 |

| LAS input rows | 9 |

| Merged output rows | 9 |

| Unmatched merge rows | 0 |

| Missing pressure values | 1 |

| Missing flow values | 1 |
Four automated tests passed:
\- Input files exist.

\- Merge returns nine unique matched rows.

\- Missing sensor values and flags are preserved.

\- Feature calculations return expected values.
\## Output files
The pipeline creates:
\- `outputs/engineered\_features.csv`

\- `outputs/quality\_summary.csv`
\## AWS connection: CSV versus Parquet
CSV is useful for simple data exchange, inspection and compatibility with common tools. Parquet is a columnar format that supports compression and efficient analytical queries, making it more suitable for larger datasets in an S3 analytical data lake.



\## GitHub PR



Branch: `feature/week11-class04-feature-engineering`



Pull Request: To be added after the branch is pushed and the PR is created.



