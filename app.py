import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Sales Dashboard", layout="wide")

# ---------------- SAMPLE DATA ----------------
@st.cache_data
def load_sample_data():
    np.random.seed(42)
    n = 100

    df = pd.DataFrame({
        "Date": pd.date_range(start="2023-01-01", periods=n),
        "Product": np.random.choice(["Laptop", "Phone", "Tablet"], n),
        "Region": np.random.choice(["North", "South", "East", "West"], n),
        "Salesperson": np.random.choice(["John", "Sarah", "Mike"], n),
        "Quantity": np.random.randint(1, 5, n),
        "Revenue": np.random.randint(500, 5000, n)
    })

    return df

# ---------------- MAIN APP ----------------
def main():
    st.title("📊 Sales & Revenue Analysis Dashboard")

    st.sidebar.header("📁 Data Upload")
    uploaded_file = st.sidebar.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])

    # Load data
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            # Convert Date safely
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

            st.sidebar.success("✅ File uploaded successfully!")

        except Exception as e:
            st.error(f"❌ Error: {e}")
            st.stop()
    else:
        df = load_sample_data()
        st.info("ℹ️ Using sample data")

    # ---------------- FILTERS ----------------
    st.sidebar.header("🔍 Filters")

    if "Region" in df.columns:
        region = st.sidebar.multiselect("Region", df["Region"].dropna().unique())
        if region:
            df = df[df["Region"].isin(region)]

    if "Product" in df.columns:
        product = st.sidebar.multiselect("Product", df["Product"].dropna().unique())
        if product:
            df = df[df["Product"].isin(product)]

    # ---------------- KPI ----------------
    col1, col2, col3 = st.columns(3)

    if "Revenue" in df.columns:
        col1.metric("💰 Total Revenue", int(df["Revenue"].sum()))

    if "Quantity" in df.columns:
        col2.metric("📦 Total Quantity", int(df["Quantity"].sum()))

    if "Product" in df.columns:
        col3.metric("🛍️ Total Products", df["Product"].nunique())

    # ---------------- CHARTS ----------------
    col1, col2 = st.columns(2)

    # Revenue Trend
    with col1:
        st.subheader("📈 Revenue Trend")

        if "Date" in df.columns and "Revenue" in df.columns:
            temp = df.dropna(subset=["Date"])
            trend = temp.groupby("Date")["Revenue"].sum().reset_index()
            fig = px.line(trend, x="Date", y="Revenue")
        else:
            fig = px.line(y=df.index)

        st.plotly_chart(fig, use_container_width=True)

    # Top Products
    with col2:
        st.subheader("🥇 Top Products")

        if "Product" in df.columns:
            if "Revenue" in df.columns:
                data = df.groupby("Product")["Revenue"].sum().reset_index()
                fig = px.bar(data, x="Product", y="Revenue")
            else:
                data = df["Product"].value_counts().reset_index()
                fig = px.bar(data, x="index", y="Product")
        else:
            fig = px.bar(y=df.index)

        st.plotly_chart(fig, use_container_width=True)

    # ---------------- PIE CHART ----------------
    st.subheader("🌍 Revenue by Region")

    if "Region" in df.columns:
        if "Revenue" in df.columns:
            region_data = df.groupby("Region")["Revenue"].sum().reset_index()
            fig = px.pie(region_data, names="Region", values="Revenue")
        else:
            region_data = df["Region"].value_counts().reset_index()
            fig = px.pie(region_data, names="index", values="Region")

        st.plotly_chart(fig, use_container_width=True)

    # ---------------- DATA PREVIEW ----------------
    st.subheader("👀 Preview Data")
    st.dataframe(df.head(), use_container_width=True)

    # ---------------- DOWNLOAD ----------------
    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "📥 Download Data",
        csv,
        "sales_data.csv",
        "text/csv"
    )

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()
