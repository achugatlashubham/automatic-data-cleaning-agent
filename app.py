
import streamlit as st
import pandas as pd

from modules.data_upload import show_dataset_uploader
from modules.data_profiling import generate_data_profile
from modules.cleaning_engine import automatic_cleaning
from modules.visualization import show_visualization_dashboard
from utils.export_data import dataframe_to_csv_bytes, dataframe_to_excel_bytes


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="Data Cleaner Agent",
    page_icon="🧹",
    layout="wide"
)


# =====================================
# PASTEL COLORFUL PROFESSIONAL THEME
# =====================================

st.markdown("""
<style>

/* Main Background */
.stApp {
    background: linear-gradient(
        135deg,
        #fff1f2 0%,
        #eff6ff 50%,
        #f5f3ff 100%
    );
}

/* Main Content */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Main Headings */
h1 {
    color: #334155 !important;
    font-weight: 800 !important;
}

h2 {
    color: #475569 !important;
    font-weight: 700 !important;
}

h3 {
    color: #64748b !important;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background: linear-gradient(
        135deg,
        #ffffff,
        #fdf2f8
    );
    padding: 20px;
    border-radius: 16px;
    border: 1px solid #fbcfe8;
    box-shadow: 0 4px 12px rgba(100, 116, 139, 0.08);
}

/* Metric Values */
[data-testid="stMetricValue"] {
    color: #7c3aed !important;
    font-weight: bold;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #ede9fe,
        #fce7f3,
        #e0f2fe
    );
}

/* Buttons */
.stButton > button {
    background: linear-gradient(
        90deg,
        #a78bfa,
        #f0abfc
    );
    color: #ffffff !important;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    transition: 0.3s;
}

/* Button Hover */
.stButton > button:hover {
    background: linear-gradient(
        90deg,
        #8b5cf6,
        #d946ef
    );
    color: white !important;
    border: none;
}

/* DataFrame */
[data-testid="stDataFrame"] {
    border: 1px solid #ddd6fe;
    border-radius: 12px;
}

/* File Uploader */
[data-testid="stFileUploader"] {
    background: #ffffff;
    border: 2px dashed #c4b5fd;
    border-radius: 15px;
    padding: 15px;
}

/* Input Fields */
.stTextInput input,
.stNumberInput input {
    border-radius: 10px;
}

/* Success Message */
[data-testid="stAlert"] {
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)



# =====================================
# PROFESSIONAL HEADER
# =====================================

st.title("🧹 Data Cleaner Agent")

st.caption(
    "Professional Automatic Data Cleaning & Quality Analysis System"
)

st.divider()


# =====================================
# SIDEBAR SETTINGS
# =====================================

st.sidebar.title("⚙️ Cleaning Settings")

st.sidebar.subheader("Missing Value Settings")

missing_threshold = st.sidebar.slider(
    "Missing Value Threshold (%)",
    min_value=10,
    max_value=100,
    value=65,
    step=5
)

missing_strategy = st.sidebar.selectbox(
    "Missing Value Strategy",
    ["auto", "zero", "mean", "median", "mode"]
)

fill_value = st.sidebar.number_input(
    "Custom Fill Value",
    value=0
)

st.sidebar.divider()

st.sidebar.subheader("Duplicate Settings")

remove_duplicates = st.sidebar.checkbox(
    "Remove Duplicate Rows",
    value=True
)

# =====================================
# DATASET UPLOAD
# =====================================


df = show_dataset_uploader()


# =====================================
# SESSION STATE
# =====================================

if "cleaned_df" not in st.session_state:
    st.session_state.cleaned_df = None

if "cleaning_report" not in st.session_state:
    st.session_state.cleaning_report = None

if "original_df" not in st.session_state:
    st.session_state.original_df = None


if df is not None:

    if (
        st.session_state.original_df is not None
        and not st.session_state.original_df.equals(df)
    ):
        st.session_state.cleaned_df = None
        st.session_state.cleaning_report = None

    # Save original dataset
    st.session_state.original_df = df.copy(deep=True)

    st.divider()

    # =================================
    # DATA PROFILING
    # =================================

    st.header("🔍 Original Data Profile")

    profile = generate_data_profile(df)

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Rows", profile["overview"]["total_rows"])

    col2.metric("Total Columns", profile["overview"]["total_columns"])

    col3.metric("Missing Values", profile["overview"]["missing_values"])

    col4.metric("Duplicate Rows", profile["overview"]["duplicate_rows"])

    st.metric(
        "Original Data Quality Score",
        f"{profile['quality_score']}%"
    )

    # =================================
    # DATA VISUALIZATION
    # =================================

    show_visualization_dashboard(df)

    # =================================
    # CLEANING CONTROLS
    # =================================

    st.divider()

    st.header("🧹 Automatic Data Cleaning")

    st.write(
        "Configure your cleaning settings in the sidebar "
        "and start the cleaning process."
    )

    available_id_columns = [
        "None"
    ] + df.columns.astype(str).tolist()

    id_column = st.selectbox(
        "Select ID Column (Optional)",
        available_id_columns
    )

    duplicate_id_keep = st.selectbox(
        "Keep which record for duplicate IDs?",
        ["first", "last"]
    )

    run_cleaning = st.button(
        "🚀 Run Automatic Cleaning",
        type="primary",
        width="stretch"
    )

    if run_cleaning:

        try:

            with st.spinner("Cleaning your dataset..."):

                cleaned_df, report = automatic_cleaning(
                    original_df=df,
                    missing_threshold=missing_threshold,
                    missing_strategy=missing_strategy,
                    fill_value=fill_value,
                    remove_duplicates=remove_duplicates,
                    id_column=None if id_column == "None" else id_column,
                    duplicate_id_keep=duplicate_id_keep
                )

                st.session_state.cleaned_df = cleaned_df

                st.session_state.cleaning_report = report

            st.success("Dataset cleaned successfully!")

        except Exception as e:

            st.error(f"Cleaning failed: {str(e)}")


    # =================================
    # CLEANING RESULTS
    # =================================

    if st.session_state.cleaned_df is not None:

        cleaned = st.session_state.cleaned_df

        report = st.session_state.cleaning_report

        st.divider()

        st.header("📊 Cleaning Results")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Original Rows",
            report["original_rows"]
        )

        col2.metric(
            "Cleaned Rows",
            report["cleaned_rows"]
        )

        col3.metric(
            "Removed Rows",
            report["original_rows"] - report["cleaned_rows"]
        )

        col4.metric(
            "Removed Columns",
            len(report["removed_columns"])
        )

        # =================================
        # BEFORE VS AFTER
        # =================================

        st.subheader("⚖️ Before vs After Comparison")

        comparison = pd.DataFrame({
            "Metric": [
                "Rows",
                "Columns",
                "Missing Values",
                "Duplicate Rows"
            ],

            "Before Cleaning": [
                df.shape[0],
                df.shape[1],
                int(df.isna().sum().sum()),
                int(df.duplicated().sum())
            ],

            "After Cleaning": [
                cleaned.shape[0],
                cleaned.shape[1],
                int(cleaned.isna().sum().sum()),
                int(cleaned.duplicated().sum())
            ]
        })

        st.dataframe(
            comparison,
            width="stretch",
            hide_index=True
        )

        # =================================
        # CLEANING REPORT
        # =================================

        st.subheader("📋 Cleaning Report")

        st.write(
            "Standardized Column Names:",
            "Yes" if report["standardized_columns"] else "No"
        )

        st.write(
            "Removed Columns:",
            report["removed_columns"]
        )

        st.write(
            "Columns with Filled Missing Values:",
            report["filled_columns"]
        )

        st.write(
            "Date Columns Standardized to YYYY-MM-DD:",
            report["date_columns_standardized"]
        )

        if report["date_columns_skipped"]:
            st.warning(
                "Date columns left unchanged because some values could not "
                "be parsed: "
                + ", ".join(report["date_columns_skipped"])
            )

        st.write(
            "Duplicate Rows Removed:",
            report["duplicate_rows_removed"]
        )

        st.write(
            "Duplicate IDs Removed:",
            report["duplicate_ids_removed"]
        )

        st.write(
            "Remaining Missing Values:",
            report["remaining_missing_values"]
        )

        # =================================
        # CLEANED DATA PREVIEW
        # =================================

        st.subheader("✅ Cleaned Dataset Preview")

        st.dataframe(
            cleaned.head(20),
            width="stretch"
        )

        # =================================
        # DOWNLOAD CLEANED DATASET
        # =================================

        st.subheader("⬇️ Download Cleaned Dataset")

        csv_download, excel_download = st.columns(2)

        with csv_download:
            st.download_button(
                "Download CSV",
                data=dataframe_to_csv_bytes(cleaned),
                file_name="cleaned_data.csv",
                mime="text/csv",
                key="download_cleaned_csv",
                width="stretch"
            )

        with excel_download:
            st.download_button(
                "Download Excel",
                data=dataframe_to_excel_bytes(cleaned),
                file_name="cleaned_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="download_cleaned_excel",
                width="stretch"
            )

else:

    st.info("Please upload a dataset to get started.")
