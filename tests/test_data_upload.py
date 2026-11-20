from io import BytesIO

import pytest

from modules.data_upload import load_dataset


@pytest.mark.parametrize(
    "encoding",
    ["utf-8-sig", "cp1252", "utf-16"]
)
def test_load_dataset_supports_common_csv_encodings(encoding):
    csv_text = "city,value\nCity²,1\n"
    uploaded_file = BytesIO(csv_text.encode(encoding))
    uploaded_file.name = "cities.csv"

    df, error = load_dataset(uploaded_file)

    assert error is None
    assert df.loc[0, "city"] == "City²"
    assert df.loc[0, "value"] == 1
