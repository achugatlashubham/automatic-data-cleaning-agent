
import pandas as pd
import numpy as np
import re
from datetime import date, datetime


def standardize_column_names(df):
    """Standardize column names."""

    df = df.copy()

    df.columns = [
        re.sub(
            r"_+",
            "_",
            re.sub(
                r"[^a-zA-Z0-9]+",
                "_",
                str(col).strip().lower()
            )
        ).strip("_")
        for col in df.columns
    ]

    return df


def standardize_date_columns(df, dayfirst=False):
    """Parse date-like columns while preserving columns with invalid values."""

    df = df.copy()
    standardized_columns = []
    skipped_columns = []

    for col in df.columns:
        is_datetime = pd.api.types.is_datetime64_any_dtype(df[col])
        is_date_named = re.search(
            r"date|timestamp",
            str(col),
            flags=re.IGNORECASE
        ) is not None

        if not is_datetime and not is_date_named:
            continue

        non_missing = df[col].notna()

        if not non_missing.any():
            continue

        if is_datetime:
            parsed = pd.to_datetime(df[col], errors="coerce")
        else:
            parsed = df[col].map(
                lambda value: pd.to_datetime(
                    value,
                    errors="coerce",
                    dayfirst=dayfirst
                )
                if isinstance(
                    value,
                    (str, date, datetime, pd.Timestamp, np.datetime64)
                )
                else pd.NaT
            )

            try:
                parsed = pd.to_datetime(parsed)
            except (TypeError, ValueError, OverflowError):
                skipped_columns.append(str(col))
                continue

        if parsed.loc[non_missing].isna().any():
            skipped_columns.append(str(col))
            continue

        df[col] = parsed
        standardized_columns.append(str(col))

    return df, standardized_columns, skipped_columns


def clean_text_values(df):
    """Remove unnecessary spaces from text values."""

    df = df.copy()

    for col in df.select_dtypes(include=["object", "string"]).columns:

        df[col] = df[col].apply(
            lambda value: value.strip()
            if isinstance(value, str)
            else value
        )

        df[col] = df[col].replace("", np.nan)

    return df


def remove_high_missing_columns(df, threshold=65):
    """Remove columns exceeding the missing-value threshold."""

    df = df.copy()

    missing_percentage = df.isna().mean() * 100

    columns_to_remove = missing_percentage[
        missing_percentage > threshold
    ].index.tolist()

    df = df.drop(columns=columns_to_remove)

    return df, columns_to_remove


def fill_missing_values(df, strategy="auto", fill_value=0):
    """Fill missing values using selected strategy."""

    df = df.copy()

    filled_columns = []

    for col in df.columns:

        if not df[col].isna().any():
            continue

        if strategy == "zero":

            df[col] = df[col].fillna(fill_value)

        elif strategy == "mean" and pd.api.types.is_numeric_dtype(df[col]):

            value = df[col].mean()
            df[col] = df[col].fillna(value)

        elif strategy == "median" and pd.api.types.is_numeric_dtype(df[col]):

            value = df[col].median()
            df[col] = df[col].fillna(value)

        elif strategy == "mode":

            mode_values = df[col].mode(dropna=True)

            if not mode_values.empty:
                df[col] = df[col].fillna(mode_values.iloc[0])

        elif strategy == "auto":

            if pd.api.types.is_numeric_dtype(df[col]):

                value = df[col].median()

            else:

                mode_values = df[col].mode(dropna=True)

                value = (
                    mode_values.iloc[0]
                    if not mode_values.empty
                    else "Unknown"
                )

            df[col] = df[col].fillna(value)

        filled_columns.append(str(col))

    return df, filled_columns


def remove_duplicate_rows(df):
    """Remove complete duplicate rows."""

    df = df.copy()

    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    return df, removed


def handle_duplicate_ids(df, id_column=None, keep="first"):
    """Handle duplicate IDs without deleting records by default."""

    if id_column is None or id_column not in df.columns:
        return df.copy(), 0

    df = df.copy()

    duplicate_mask = (
        df[id_column].notna()
        & df[id_column].duplicated(keep=keep)
    )

    duplicate_count = int(duplicate_mask.sum())

    df = df.loc[~duplicate_mask].copy()

    return df, duplicate_count


def automatic_cleaning(
    original_df,
    missing_threshold=65,
    missing_strategy="auto",
    fill_value=0,
    remove_duplicates=True,
    id_column=None,
    duplicate_id_keep="first"
):
    """Complete automatic data cleaning pipeline."""

    if original_df is None or original_df.empty:
        raise ValueError("Please provide a non-empty dataset.")

    # Preserve original data
    df = original_df.copy(deep=True)

    report = {}

    # Step 1: Standardize column names
    old_columns = df.columns.astype(str).tolist()

    df = standardize_column_names(df)

    report["standardized_columns"] = (
        old_columns != df.columns.astype(str).tolist()
    )

    # Step 2: Clean text
    df = clean_text_values(df)

    # Step 3: Remove high-missing columns
    df, removed_columns = remove_high_missing_columns(
        df,
        threshold=missing_threshold
    )

    report["removed_columns"] = removed_columns

    # Step 4: Standardize date columns (ambiguous slash dates are month-first)
    df, standardized_date_columns, skipped_date_columns = (
        standardize_date_columns(df, dayfirst=False)
    )

    report["date_columns_standardized"] = standardized_date_columns
    report["date_columns_skipped"] = skipped_date_columns

    # Step 5: Fill missing values
    df, filled_columns = fill_missing_values(
        df,
        strategy=missing_strategy,
        fill_value=fill_value
    )

    report["filled_columns"] = filled_columns

    # Step 6: Remove duplicate rows
    duplicate_rows_removed = 0

    if remove_duplicates:

        df, duplicate_rows_removed = remove_duplicate_rows(df)

    report["duplicate_rows_removed"] = duplicate_rows_removed

    # Step 7: Handle duplicate IDs
    duplicate_ids_removed = 0

    if id_column is not None:

        # Account for standardized column names
        normalized_id = standardize_column_names(
            pd.DataFrame(columns=[id_column])
        ).columns[0]

        if normalized_id in df.columns:

            df, duplicate_ids_removed = handle_duplicate_ids(
                df,
                id_column=normalized_id,
                keep=duplicate_id_keep
            )

    report["duplicate_ids_removed"] = duplicate_ids_removed

    # Step 8: Final missing values
    report["remaining_missing_values"] = int(
        df.isna().sum().sum()
    )

    report["original_rows"] = len(original_df)
    report["cleaned_rows"] = len(df)

    report["original_columns"] = len(original_df.columns)
    report["cleaned_columns"] = len(df.columns)

    return df, report
