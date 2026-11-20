from io import BytesIO

import pandas as pd

from utils.export_data import dataframe_to_csv_bytes, dataframe_to_excel_bytes


def test_dataframe_to_csv_bytes_preserves_data():
    original = pd.DataFrame({
        "name": ["Ana", "Sam"],
        "revenue": [120.5, 80.0]
    })

    exported = pd.read_csv(BytesIO(dataframe_to_csv_bytes(original)))

    pd.testing.assert_frame_equal(exported, original)


def test_dataframe_to_excel_bytes_preserves_data():
    original = pd.DataFrame({
        "name": ["Ana", "Sam"],
        "revenue": [120.5, 80.0]
    })

    exported = pd.read_excel(BytesIO(dataframe_to_excel_bytes(original)))

    pd.testing.assert_frame_equal(exported, original)
