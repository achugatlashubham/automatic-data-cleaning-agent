from io import BytesIO

import pandas as pd


def dataframe_to_csv_bytes(df):
    """Serialize a dataframe as a downloadable UTF-8 CSV."""

    return df.to_csv(index=False).encode("utf-8-sig")


def dataframe_to_excel_bytes(df):
    """Serialize a dataframe as a downloadable Excel workbook."""

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter",
        date_format="yyyy-mm-dd",
        datetime_format="yyyy-mm-dd hh:mm:ss"
    ) as writer:
        df.to_excel(writer, index=False, sheet_name="Cleaned Data")
        worksheet = writer.sheets["Cleaned Data"]

        for column_index, column in enumerate(df.columns):
            if not pd.api.types.is_datetime64_any_dtype(df[column]):
                continue

            values = df[column].dropna()
            has_time = (
                (values.dt.hour != 0)
                | (values.dt.minute != 0)
                | (values.dt.second != 0)
                | (values.dt.microsecond != 0)
            ).any()

            number_format = (
                "yyyy-mm-dd hh:mm:ss"
                if has_time
                else "yyyy-mm-dd"
            )
            cell_format = writer.book.add_format(
                {"num_format": number_format}
            )
            worksheet.set_column(
                column_index,
                column_index,
                None,
                cell_format
            )

    return output.getvalue()