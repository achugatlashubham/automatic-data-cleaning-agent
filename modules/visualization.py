
import streamlit as st
import pandas as pd
import plotly.express as px


def show_missing_values_chart(df):

    st.subheader("Missing Values Analysis")

    missing = df.isnull().sum()
    missing = missing[missing > 0]

    if missing.empty:
        st.success("No missing values found!")
        return

    missing_df = pd.DataFrame({
        "Column": missing.index,
        "Missing Values": missing.values
    })

    fig = px.bar(
        missing_df,
        x="Column",
        y="Missing Values",
        title="Missing Values by Column",
        text="Missing Values"
    )

    st.plotly_chart(fig, width="stretch")


def show_numeric_distribution(df):

    st.subheader("Numerical Data Distribution")

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if not numeric_columns:
        st.info("No numerical columns available.")
        return

    selected_column = st.selectbox(
        "Select Numerical Column",
        numeric_columns,
        key="numeric_distribution_column"
    )

    fig = px.histogram(
        df,
        x=selected_column,
        title=f"Distribution of {selected_column}",
        marginal="box"
    )

    st.plotly_chart(fig, width="stretch")


def show_categorical_analysis(df):

    st.subheader("Categorical Data Analysis")

    categorical_columns = df.select_dtypes(
        include=["object", "category", "bool"]
    ).columns.tolist()

    if not categorical_columns:
        st.info("No categorical columns available.")
        return

    selected_column = st.selectbox(
        "Select Categorical Column",
        categorical_columns,
        key="categorical_analysis_column"
    )

    value_counts = (
        df[selected_column]
        .astype(str)
        .value_counts()
        .head(10)
        .reset_index()
    )

    value_counts.columns = [
        "Category",
        "Count"
    ]

    fig = px.bar(
        value_counts,
        x="Category",
        y="Count",
        title=f"Top 10 Categories in {selected_column}",
        text="Count"
    )

    st.plotly_chart(fig, width="stretch")

    pie_fig = px.pie(
        value_counts,
        names="Category",
        values="Count",
        title=f"Category Distribution: {selected_column}"
    )

    st.plotly_chart(pie_fig, width="stretch")


def show_revenue_analysis(df):

    st.subheader("Revenue Analysis")

    revenue_columns = [
        col for col in df.columns
        if "revenue" in str(col).lower()
        or "sales" in str(col).lower()
        or "amount" in str(col).lower()
    ]

    revenue_columns = [
        col for col in revenue_columns
        if pd.api.types.is_numeric_dtype(df[col])
    ]

    if not revenue_columns:
        st.info(
            "No Revenue, Sales, or Amount numerical column found."
        )
        return

    selected_revenue = st.selectbox(
        "Select Revenue Column",
        revenue_columns,
        key="revenue_analysis_column"
    )

    revenue_data = df[selected_revenue].dropna()

    col1, col2 = st.columns(2)

    col1.metric(
        "Total Revenue",
        f"{revenue_data.sum():,.2f}"
    )

    col2.metric(
        "Average Revenue",
        f"{revenue_data.mean():,.2f}"
    )

    fig = px.histogram(
        df,
        x=selected_revenue,
        title="Revenue Distribution",
        nbins=20
    )

    st.plotly_chart(fig, width="stretch")


def show_visualization_dashboard(df):

    st.header("📊 Data Visualization Dashboard")

    if df is None or df.empty:
        st.info("No data available for visualization.")
        return

    show_missing_values_chart(df)

    st.divider()

    show_numeric_distribution(df)

    st.divider()

    show_categorical_analysis(df)

    st.divider()

    show_revenue_analysis(df)
