
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px

# -------------------------------------------------------------------
# Page setup
# -------------------------------------------------------------------
st.set_page_config(
    page_title="Retail Sales Dashboard",
    page_icon="\U0001F4CA",
    layout="wide",
)

st.title("Retail Sales Dashboard")
st.caption("Explore revenue, sales volume, customer behavior, and product performance.")

# -------------------------------------------------------------------
# Load & prepare data
# -------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("retail_sales.csv")
    df["date"] = pd.to_datetime(df["date"])
    df["revenue"] = df["units_sold"] * df["unit_price"] * (1 - df["discount"])
    df["net_revenue"] = df["revenue"] - df["shipping_cost"]
    df["order_value"] = df["revenue"]
    df["weekday"] = df["date"].dt.day_name()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# -------------------------------------------------------------------
# Sidebar filters
# -------------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = df["date"].min(), df["date"].max()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

selected_regions = st.sidebar.multiselect(
    "Region", options=sorted(df["region"].unique()), default=sorted(df["region"].unique())
)
selected_categories = st.sidebar.multiselect(
    "Product category", options=sorted(df["product_category"].unique()),
    default=sorted(df["product_category"].unique())
)
selected_segments = st.sidebar.multiselect(
    "Customer segment", options=sorted(df["customer_segment"].unique()),
    default=sorted(df["customer_segment"].unique())
)
selected_channels = st.sidebar.multiselect(
    "Sales channel", options=sorted(df["sales_channel"].unique()),
    default=sorted(df["sales_channel"].unique())
)
selected_statuses = st.sidebar.multiselect(
    "Order status", options=sorted(df["order_status"].unique()),
    default=sorted(df["order_status"].unique())
)

st.sidebar.divider()
exclude_returns = st.sidebar.checkbox("Exclude returned/cancelled orders from revenue", value=True)

filtered_df = df[
    (df["region"].isin(selected_regions))
    & (df["product_category"].isin(selected_categories))
    & (df["customer_segment"].isin(selected_segments))
    & (df["sales_channel"].isin(selected_channels))
    & (df["order_status"].isin(selected_statuses))
    & (df["date"].between(pd.to_datetime(start_date), pd.to_datetime(end_date)))
].copy()

if exclude_returns:
    revenue_df = filtered_df[filtered_df["order_status"] == "Completed"]
else:
    revenue_df = filtered_df

if filtered_df.empty:
    st.warning("No data matches the selected filters. Try widening your selection.")
    st.stop()

# -------------------------------------------------------------------
# KPI row
# -------------------------------------------------------------------
total_revenue = revenue_df["revenue"].sum()
total_orders = filtered_df["order_id"].nunique()
avg_order_value = revenue_df["order_value"].mean() if len(revenue_df) else 0
total_units = revenue_df["units_sold"].sum()
return_rate = (filtered_df["order_status"] == "Returned").mean() * 100
unique_customers = filtered_df["customer_id"].nunique()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("Total Revenue", f"${total_revenue:,.0f}")
k2.metric("Orders", f"{total_orders:,}")
k3.metric("Avg Order Value", f"${avg_order_value:,.2f}")
k4.metric("Units Sold", f"{total_units:,}")
k5.metric("Return Rate", f"{return_rate:.1f}%")
k6.metric("Unique Customers", f"{unique_customers:,}")

st.divider()

# -------------------------------------------------------------------
# Tabs for the different analysis views
# -------------------------------------------------------------------
tab_trends, tab_products, tab_regions, tab_customers, tab_data = st.tabs(
    ["Sales Trends", "Product Analysis", "Regional Analysis", "Customer Insights", "Raw Data"]
)

# --- Sales Trends -----------------------------------------------------
with tab_trends:
    col1, col2 = st.columns((2, 1))

    with col1:
        monthly_revenue = (
            revenue_df.set_index("date").resample("ME")["revenue"].sum().reset_index()
        )
        fig = px.line(monthly_revenue, x="date", y="revenue", markers=True,
                       title="Monthly Revenue Trend")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        channel_rev = revenue_df.groupby("sales_channel")["revenue"].sum().reset_index()
        fig = px.pie(channel_rev, names="sales_channel", values="revenue",
                      title="Revenue by Sales Channel", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekday_rev = (
            revenue_df.groupby("weekday")["revenue"].sum()
            .reindex(weekday_order).reset_index()
        )
        fig = px.bar(weekday_rev, x="weekday", y="revenue", title="Revenue by Day of Week")
        st.plotly_chart(fig, use_container_width=True)

    with col4:
        status_counts = filtered_df["order_status"].value_counts().reset_index()
        status_counts.columns = ["order_status", "count"]
        fig = px.bar(status_counts, x="order_status", y="count", color="order_status",
                      title="Order Status Breakdown")
        st.plotly_chart(fig, use_container_width=True)

# --- Product Analysis ---------------------------------------------------
with tab_products:
    col1, col2 = st.columns(2)

    with col1:
        cat_rev = revenue_df.groupby("product_category")["revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(cat_rev, x="product_category", y="revenue", title="Revenue by Category")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        sub_rev = (
            revenue_df.groupby(["product_category", "product_subcategory"])["revenue"]
            .sum().reset_index().sort_values("revenue", ascending=False).head(10)
        )
        fig = px.bar(sub_rev, x="revenue", y="product_subcategory", color="product_category",
                      orientation="h", title="Top 10 Subcategories by Revenue")
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

    discount_impact = (
        revenue_df.groupby("product_category")
        .agg(avg_discount=("discount", "mean"), revenue=("revenue", "sum"))
        .reset_index()
    )
    fig = px.scatter(discount_impact, x="avg_discount", y="revenue", size="revenue",
                      color="product_category", title="Average Discount vs Revenue by Category")
    st.plotly_chart(fig, use_container_width=True)

# --- Regional Analysis ---------------------------------------------------
with tab_regions:
    col1, col2 = st.columns(2)

    with col1:
        region_rev = revenue_df.groupby("region")["revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(region_rev, x="region", y="revenue", title="Revenue by Region")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        state_rev = revenue_df.groupby("state")["revenue"].sum().sort_values(ascending=False).head(10).reset_index()
        fig = px.bar(state_rev, x="revenue", y="state", orientation="h",
                      title="Top 10 States by Revenue")
        fig.update_layout(yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig, use_container_width=True)

    store_rev = revenue_df.groupby(["region", "store_id"])["revenue"].sum().reset_index()
    fig = px.treemap(store_rev, path=["region", "store_id"], values="revenue",
                      title="Revenue by Region and Store")
    st.plotly_chart(fig, use_container_width=True)

# --- Customer Insights ---------------------------------------------------
with tab_customers:
    col1, col2 = st.columns(2)

    with col1:
        segment_rev = revenue_df.groupby("customer_segment")["revenue"].sum().reset_index()
        fig = px.pie(segment_rev, names="customer_segment", values="revenue",
                      title="Revenue by Customer Segment", hole=0.45)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        payment_rev = revenue_df.groupby("payment_method")["revenue"].sum().sort_values(ascending=False).reset_index()
        fig = px.bar(payment_rev, x="payment_method", y="revenue", title="Revenue by Payment Method")
        st.plotly_chart(fig, use_container_width=True)

    top_customers = (
        revenue_df.groupby("customer_id")
        .agg(total_spent=("revenue", "sum"), orders=("order_id", "nunique"))
        .sort_values("total_spent", ascending=False).head(10).reset_index()
    )
    st.subheader("Top 10 Customers by Spend")
    st.dataframe(top_customers, use_container_width=True, hide_index=True)

# --- Raw Data ---------------------------------------------------
with tab_data:
    st.subheader("Filtered Transaction Data")
    search = st.text_input("Search (matches any column as text)")
    display_df = filtered_df.copy()
    if search:
        mask = display_df.apply(lambda col: col.astype(str).str.contains(search, case=False, na=False))
        display_df = display_df[mask.any(axis=1)]

    st.dataframe(display_df.sort_values("date", ascending=False), use_container_width=True, hide_index=True)
    st.caption(f"Showing {len(display_df):,} of {len(filtered_df):,} filtered rows.")

    csv_bytes = display_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download filtered data as CSV",
        data=csv_bytes,
        file_name="filtered_retail_sales.csv",
        mime="text/csv",
    )
