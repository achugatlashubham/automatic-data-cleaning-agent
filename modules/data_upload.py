
from io import BytesIO

import pandas as pd
import streamlit as st


def _read_csv(uploaded_file):
    content = uploaded_file.getvalue()

    if content.startswith((b"\xff\xfe", b"\xfe\xff")):
        encodings = ("utf-16",)
    elif content.startswith(b"\xef\xbb\xbf"):
        encodings = ("utf-8-sig",)
    else:
        encodings = ("utf-8-sig", "cp1252")

    decode_error = None

    for encoding in encodings:
        try:
            return pd.read_csv(BytesIO(content), encoding=encoding)
        except UnicodeDecodeError as error:
            decode_error = error

    raise ValueError(
        "CSV encoding is not supported. Save the file as UTF-8 or "
        "Windows-1252 and upload it again."
    ) from decode_error


def load_dataset(uploaded_file):
    """
    Load CSV or Excel dataset safely.
    """

    if uploaded_file is None:
        return None, "Please upload a file."

    file_name = uploaded_file.name.lower()

    try:
        if file_name.endswith(".csv"):
            df = _read_csv(uploaded_file)

        elif file_name.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)

        else:
            return None, "Unsupported file format. Upload CSV or Excel."

        if df.empty:
            return None, "The uploaded file is empty."

        if len(df.columns) == 0:
            return None, "No columns found in the uploaded file."

        # Remove extra spaces from column names
        df.columns = df.columns.astype(str).str.strip()

        # Check duplicate column names
        if df.columns.duplicated().any():
            return None, "Duplicate column names found. Please fix them first."

        return df, None

    except pd.errors.EmptyDataError:
        return None, "The CSV file contains no data."

    except pd.errors.ParserError:
        return None, "Unable to read CSV. Please check its format."

    except Exception as e:
        return None, f"File loading error: {str(e)}"


def show_dataset_uploader():

    st.subheader("📤 Upload Your Dataset")

    uploaded_file = st.file_uploader(
        "Choose CSV or Excel file",
        type=["csv", "xlsx", "xls"],
        help="Upload a CSV or Excel dataset."
    )

    if uploaded_file is not None:

        df, error = load_dataset(uploaded_file)

        if error:
            st.error(error)
            return None

        st.success("Dataset uploaded successfully!")

        st.subheader("📊 Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Rows", df.shape[0])

        with col2:
            st.metric("Total Columns", df.shape[1])

        with col3:
            st.metric(
                "Total Missing Values",
                int(df.isna().sum().sum())
            )

        return df

    return None
