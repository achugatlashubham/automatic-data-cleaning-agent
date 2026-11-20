# Data Cleaner Agent

Data Cleaner Agent is a simple web app for checking, cleaning, and downloading datasets. It is built with Python, Streamlit, and pandas.

## What it can do

- Upload CSV and Excel files (`.csv`, `.xlsx`, and `.xls`).
- Read CSV files saved as UTF-8, Windows-1252, or UTF-16 with a byte-order mark.
- Show dataset size, missing values, duplicates, and a data quality score.
- Visualize missing values, number distributions, categories, and revenue-like columns.
- Standardize column names and remove extra spaces from text.
- Remove columns with more missing values than the selected threshold.
- Fill missing values using the selected strategy.
- Remove duplicate rows and, optionally, duplicate IDs.
- Convert date columns to dates. Ambiguous slash dates such as `1/4/2018` are read as month-first (January 4) and exported in ISO style (`YYYY-MM-DD`). If a date column contains values that cannot be parsed, it is left unchanged and reported.
- Preview and download the cleaned dataset as CSV or Excel.

The uploaded file is not overwritten. Cleaning creates a separate result that you can review and download.

## Set up the project

These commands are for Windows PowerShell. Open PowerShell in this project folder first.

Create and activate a virtual environment:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Start the app

```powershell
python -m streamlit run app.py
```

Streamlit will print a local web address. Open that address in your browser.

## Use the app

1. Upload a CSV or Excel file.
2. Review its profile and charts.
3. Choose cleaning settings in the sidebar.
4. Choose an ID column if you want to remove duplicate IDs.
5. Select **Run Automatic Cleaning**.
6. Review the results and download the cleaned dataset as CSV or Excel.

## Run the tests

```powershell
python -m pytest
```

## Project structure

```text
data cleaning agent/
├── app.py
├── requirements.txt
├── modules/
│   ├── cleaning_engine.py
│   ├── data_profiling.py
│   ├── data_upload.py
│   └── visualization.py
├── tests/
│   ├── test_cleaning.py
│   ├── test_data_upload.py
│   └── test_export_data.py
└── utils/
    └── export_data.py
```
