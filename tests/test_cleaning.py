
import pandas as pd

from modules.cleaning_engine import automatic_cleaning


def test_automatic_cleaning():

    data = {
        "Customer Name": [" Rahul ", "Amit", "Rahul "],
        "Age": [25, None, 25],
        "Revenue": [5000, 7000, 5000]
    }

    original_df = pd.DataFrame(data)

    cleaned_df, report = automatic_cleaning(
        original_df,
        missing_threshold=65,
        missing_strategy="auto",
        remove_duplicates=True
    )

    # Check duplicate removal
    assert len(cleaned_df) == 2

    # Check missing values
    assert cleaned_df.isna().sum().sum() == 0

    # Check standardized columns
    assert "customer_name" in cleaned_df.columns

    # Check original dataset remains unchanged
    assert original_df.isna().sum().sum() == 1

    # Check cleaning report
    assert report["duplicate_rows_removed"] == 1


def test_automatic_cleaning_standardizes_mixed_dates_month_first():
    original_df = pd.DataFrame({
        "order_date": ["1/4/2018", "4-Jan-18", "4/1/2018"]
    })

    cleaned_df, report = automatic_cleaning(
        original_df,
        remove_duplicates=False
    )

    assert cleaned_df["order_date"].dt.strftime("%Y-%m-%d").tolist() == [
        "2018-01-04",
        "2018-01-04",
        "2018-04-01"
    ]
    assert report["date_columns_standardized"] == ["order_date"]
    assert report["date_columns_skipped"] == []


def test_automatic_cleaning_preserves_unparseable_date_column():
    original_df = pd.DataFrame({
        "delivery_date": ["1/4/2018", "not a date"]
    })

    cleaned_df, report = automatic_cleaning(
        original_df,
        remove_duplicates=False
    )

    assert cleaned_df["delivery_date"].tolist() == [
        "1/4/2018",
        "not a date"
    ]
    assert report["date_columns_standardized"] == []
    assert report["date_columns_skipped"] == ["delivery_date"]
