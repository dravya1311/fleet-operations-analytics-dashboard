# ==========================================================
# Fleet Management Dashboard
# Part 1 - Imports, Page Config, Data Cleaning & Sidebar
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------------
# Page Configuration
# ----------------------------------------------------------

st.set_page_config(
    page_title="Fleet Management Dashboard",
    page_icon="🚚",
    layout="wide"
)

# ----------------------------------------------------------
# Custom CSS
# ----------------------------------------------------------

st.markdown("""
<style>

.main{
    background-color:#f8f9fa;
}

[data-testid="metric-container"]{
    background:#ffffff;
    border-radius:10px;
    padding:15px;
    box-shadow:0px 2px 8px rgba(0,0,0,0.10);
}

h1,h2,h3{
    color:#003366;
}

</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------
# Dashboard Title
# ----------------------------------------------------------

st.title("🚚 Fleet Management Dashboard")
st.markdown("Operational Performance & Revenue Analytics")

# ----------------------------------------------------------
# Load Data
# ----------------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("transport data.csv")

    # Clean column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    # Remove duplicates
    df.drop_duplicates(inplace=True)

    # Clean text columns
    text_columns = df.select_dtypes(include="object").columns

    for col in text_columns:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.title()
        )

    # Numeric conversion

    numeric_columns = [
        "delivery_cost",
        "delivery_rating",
        "package_weight_kg",
        "delivery_time_hours",
        "expected_time_hours",
        "distance_km"
    ]

    for col in numeric_columns:

        if col in df.columns:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # Remove missing values

    df.dropna(inplace=True)

    # Revenue

    df["revenue"] = df["delivery_cost"]

    # Delay Flag

    df["delay_flag"] = np.where(
        df["delayed"] == "Yes",
        1,
        0
    )

    # Failure Flag

    df["failure_flag"] = np.where(
        df["delivery_status"] == "Failed",
        1,
        0
    )

    # Weight Category
    # (Using industry standard)

    df["weight_category"] = np.where(
        df["package_weight_kg"] <= 20,
        "Light",
        "Heavy"
    )

    return df


df = load_data()

# ----------------------------------------------------------
# Sidebar Filters
# ----------------------------------------------------------

st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Region",
    options=sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

vehicle = st.sidebar.multiselect(
    "Vehicle Type",
    options=sorted(df["vehicle_type"].unique()),
    default=sorted(df["vehicle_type"].unique())
)

mode = st.sidebar.multiselect(
    "Delivery Mode",
    options=sorted(df["delivery_mode"].unique()),
    default=sorted(df["delivery_mode"].unique())
)

weather = st.sidebar.multiselect(
    "Weather",
    options=sorted(df["weather_condition"].unique()),
    default=sorted(df["weather_condition"].unique())
)

package = st.sidebar.multiselect(
    "Package Type",
    options=sorted(df["package_type"].unique()),
    default=sorted(df["package_type"].unique())
)

filtered_df = df[
    (df["region"].isin(region)) &
    (df["vehicle_type"].isin(vehicle)) &
    (df["delivery_mode"].isin(mode)) &
    (df["weather_condition"].isin(weather)) &
    (df["package_type"].isin(package))
]

# ----------------------------------------------------------
# KPI Calculations
# ----------------------------------------------------------

total_delivery = len(filtered_df)

total_revenue = filtered_df["revenue"].sum()

avg_revenue = filtered_df["revenue"].mean()

avg_rating = filtered_df["delivery_rating"].mean()

delay_percent = (
    filtered_df["delay_flag"].mean()*100
)

failure_percent = (
    filtered_df["failure_flag"].mean()*100
)

avg_cost = filtered_df["delivery_cost"].mean()

# ----------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------

c1,c2,c3,c4 = st.columns(4)

c1.metric(
    "Total Deliveries",
    f"{total_delivery:,}"
)

c2.metric(
    "Total Revenue",
    f"₹ {total_revenue:,.0f}"
)

c3.metric(
    "Avg Revenue",
    f"₹ {avg_revenue:,.0f}"
)

c4.metric(
    "Avg Rating",
    f"{avg_rating:.2f}"
)

c5,c6,c7 = st.columns(3)

c5.metric(
    "Delayed %",
    f"{delay_percent:.1f}%"
)

c6.metric(
    "Failure %",
    f"{failure_percent:.1f}%"
)

c7.metric(
    "Avg Delivery Cost",
    f"₹ {avg_cost:,.0f}"
)

st.markdown("---")

# ==========================================================
# Charts Section - 1
# ==========================================================

# -------------------------------
# Row 1
# -------------------------------

col1, col2 = st.columns(2)

# KPI 1 : Average Revenue by Region

with col1:

    revenue_region = (
        filtered_df
        .groupby("region", as_index=False)["revenue"]
        .mean()
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        revenue_region,
        x="region",
        y="revenue",
        color="revenue",
        text_auto=".2s",
        title="Average Revenue by Region"
    )

    fig.update_layout(
        xaxis_title="Region",
        yaxis_title="Average Revenue",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


# KPI 2 : Average Rating by Delivery Mode

with col2:

    rating = (
        filtered_df
        .groupby("delivery_mode", as_index=False)["delivery_rating"]
        .mean()
        .sort_values("delivery_rating", ascending=False)
    )

    fig = px.bar(
        rating,
        x="delivery_mode",
        y="delivery_rating",
        color="delivery_rating",
        text_auto=".2f",
        title="Average Rating by Delivery Mode"
    )

    fig.update_layout(
        showlegend=False,
        xaxis_title="Delivery Mode",
        yaxis_title="Average Rating"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Row 2
# ==========================================================

col3, col4 = st.columns(2)

# KPI 3
# Revenue by Package Weight & Delay

with col3:

    weight_delay = (

        filtered_df

        .groupby(
            ["weight_category","delayed"],
            as_index=False
        )["revenue"]

        .sum()

    )

    fig = px.bar(

        weight_delay,

        x="weight_category",

        y="revenue",

        color="delayed",

        barmode="group",

        text_auto=".2s",

        title="Revenue by Package Weight & Delay"

    )

    fig.update_layout(

        xaxis_title="Package Weight",

        yaxis_title="Revenue"

    )

    st.plotly_chart(fig,use_container_width=True)



# KPI 4
# Failure % by Delivery Mode

with col4:

    failure = (

        filtered_df

        .groupby("delivery_mode")

        ["failure_flag"]

        .mean()

        .reset_index()

    )

    failure["Failure %"] = failure["failure_flag"]*100

    fig = px.bar(

        failure,

        x="delivery_mode",

        y="Failure %",

        color="Failure %",

        text_auto=".1f",

        title="Failure % by Delivery Mode"

    )

    fig.update_layout(

        showlegend=False,

        xaxis_title="Delivery Mode",

        yaxis_title="Failure %"

    )

    st.plotly_chart(fig,use_container_width=True)

# ==========================================================
# Row 3
# ==========================================================

col5,col6 = st.columns(2)

# KPI 5
# Delay % by Weather & Package Type

with col5:

    delay = (

        filtered_df

        .groupby(
            ["weather_condition","package_type"]
        )["delay_flag"]

        .mean()

        .reset_index()

    )

    delay["Delay %"] = delay["delay_flag"]*100

    fig = px.density_heatmap(

        delay,

        x="weather_condition",

        y="package_type",

        z="Delay %",

        text_auto=True,

        title="Delay % : Weather vs Package"

    )

    st.plotly_chart(fig,use_container_width=True)



# KPI 6
# Revenue Share

with col6:

    revenue_share = (

        filtered_df

        .groupby(
            ["vehicle_type","package_type"],
            as_index=False
        )["revenue"]

        .sum()

    )

    fig = px.bar(

        revenue_share,

        x="vehicle_type",

        y="revenue",

        color="package_type",

        text_auto=".2s",

        title="Revenue Share by Vehicle & Package"

    )

    fig.update_layout(

        xaxis_title="Vehicle Type",

        yaxis_title="Revenue"

    )

    st.plotly_chart(fig,use_container_width=True)

st.markdown("---")

# ==========================================================
# Charts Section - 2
# ==========================================================

# -------------------------------
# Row 4
# -------------------------------

col7, col8 = st.columns(2)

# KPI 7
# Revenue by Delivery Partner

with col7:

    partner = (
        filtered_df
        .groupby("delivery_partner", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        partner,
        x="delivery_partner",
        y="revenue",
        color="revenue",
        text_auto=".2s",
        title="Revenue by Delivery Partner"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

# KPI 8
# Revenue by Vehicle Type

with col8:

    vehicle = (
        filtered_df
        .groupby("vehicle_type", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        vehicle,
        x="vehicle_type",
        y="revenue",
        color="revenue",
        text_auto=".2s",
        title="Revenue by Vehicle Type"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Row 5
# ==========================================================

col9, col10 = st.columns(2)

# KPI 9
# Average Delivery Time

with col9:

    delivery_time = (
        filtered_df
        .groupby("delivery_mode", as_index=False)["delivery_time_hours"]
        .mean()
    )

    fig = px.bar(
        delivery_time,
        x="delivery_mode",
        y="delivery_time_hours",
        color="delivery_time_hours",
        text_auto=".2f",
        title="Average Delivery Time (Hours)"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

# KPI 10
# Delayed Deliveries by Region

with col10:

    region_delay = (
        filtered_df
        .groupby("region", as_index=False)["delay_flag"]
        .sum()
    )

    fig = px.bar(
        region_delay,
        x="region",
        y="delay_flag",
        color="delay_flag",
        text_auto=True,
        title="Delayed Deliveries by Region"
    )

    fig.update_layout(
        yaxis_title="Delayed Deliveries",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Row 6
# ==========================================================

col11, col12 = st.columns(2)

# KPI 11
# Delivery Status Distribution

with col11:

    fig = px.pie(
        filtered_df,
        names="delivery_status",
        hole=0.55,
        title="Delivery Status Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# KPI 12
# Package Type Distribution

with col12:

    fig = px.pie(
        filtered_df,
        names="package_type",
        hole=0.55,
        title="Package Type Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Executive Summary
# ==========================================================

st.markdown("---")

st.subheader("Executive Summary")

best_region = (
    filtered_df.groupby("region")["revenue"]
    .sum()
    .idxmax()
)

best_vehicle = (
    filtered_df.groupby("vehicle_type")["revenue"]
    .sum()
    .idxmax()
)

highest_failure = (
    filtered_df.groupby("delivery_mode")["failure_flag"]
    .mean()
    .idxmax()
)

highest_delay_weather = (
    filtered_df.groupby("weather_condition")["delay_flag"]
    .mean()
    .idxmax()
)

st.success(f"🏆 Highest Revenue Region : {best_region}")

st.info(f"🚛 Best Revenue Generating Vehicle : {best_vehicle}")

st.warning(f"⚠ Highest Failure Delivery Mode : {highest_failure}")

st.error(f"🌧 Highest Delay Weather : {highest_delay_weather}")

# ==========================================================
# Download Data
# ==========================================================

st.markdown("---")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Data",
    data=csv,
    file_name="fleet_dashboard_filtered.csv",
    mime="text/csv"
)

# ==========================================================
# Footer
# ==========================================================

st.markdown("---")

st.caption(
    "Fleet Management Dashboard | Built using Streamlit, Pandas & Plotly"
)
