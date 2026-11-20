
import pandas as pd
import numpy as np


def get_dataset_overview(df):

    return {
        "total_rows": int(df.shape[0]),
        "total_columns": int(df.shape[1]),
        "total_cells": int(df.size),
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
        "memory_usage": round(
            df.memory_usage(deep=True).sum() / 1024,
            2
        )
    }


def get_missing_value_report(df):

    missing = pd.DataFrame({
        "Column": df.columns,
        "Missing Values": df.isna().sum().values,
        "Missing Percentage": (
            df.isna().mean().values * 100
        ).round(2)
    })

    missing = missing.sort_values(
        by="Missing Percentage",
        ascending=False
    )

    return missing.reset_index(drop=True)


def get_data_type_report(df):

    report = pd.DataFrame({
        "Column": df.columns.astype(str),
        "Data Type": df.dtypes.astype(str).values,
        "Non-Null Values": df.notna().sum().values,
        "Unique Values": df.nunique().values
    })

    return report


def get_duplicate_report(df):

    duplicate_count = int(df.duplicated().sum())

    return {
        "duplicate_rows": duplicate_count,
        "duplicate_percentage": round(
            (duplicate_count / len(df)) * 100, 2
        ) if len(df) > 0 else 0
    }



def get_statistical_summary(df):

    # Select numerical columns
    numeric_df = df.select_dtypes(include=[np.number])

    # Select categorical columns
    categorical_df = df.select_dtypes(
        include=["object", "category", "bool"]
    )

    # Numerical summary
    if not numeric_df.empty and numeric_df.shape[1] > 0:
        numeric_summary = numeric_df.describe().T
    else:
        numeric_summary = pd.DataFrame()

    # Categorical summary
    if not categorical_df.empty and categorical_df.shape[1] > 0:
        categorical_summary = categorical_df.describe().T
    else:
        categorical_summary = pd.DataFrame()

    return numeric_summary, categorical_summary



def calculate_data_quality_score(df):

    if df.empty or df.size == 0:
        return 0.0

    total_cells = df.size

    missing_cells = int(df.isna().sum().sum())

    missing_score = (
        (total_cells - missing_cells) / total_cells
    ) * 100

    duplicate_count = int(df.duplicated().sum())

    duplicate_score = (
        (len(df) - duplicate_count) / len(df)
    ) * 100

    quality_score = (
        0.7 * missing_score +
        0.3 * duplicate_score
    )

    return round(quality_score, 2)


def generate_data_profile(df):

    overview = get_dataset_overview(df)

    missing_report = get_missing_value_report(df)

    datatype_report = get_data_type_report(df)

    duplicate_report = get_duplicate_report(df)

    numeric_summary, categorical_summary = (
        get_statistical_summary(df)
    )

    quality_score = calculate_data_quality_score(df)

    return {
        "overview": overview,
        "missing_report": missing_report,
        "datatype_report": datatype_report,
        "duplicate_report": duplicate_report,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "quality_score": quality_score
    }
