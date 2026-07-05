# ==========================================================
# Fleet Management Dashboard
# Part 1
# ==========================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------------------------------------
# Page Configuration
# ----------------------------------------------------------

st.set_page_config(
    page_title="Fleet Management Dashboard",
    page_icon="🚚",
    layout="wide"
)

st.title("🚚 Fleet Management Dashboard")
st.markdown("Fleet Performance | Revenue | Delivery Analytics")

# ----------------------------------------------------------
# Load Data
# ----------------------------------------------------------

@st.cache_data
def load_data():

    df = pd.read_csv("transport data.csv")

    # Clean column names
    df.columns = df.columns.str.strip().str.lower()

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Clean text columns
    object_cols = df.select_dtypes(include="object").columns

    for col in object_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.lower()
        )

    # Numeric columns
    numeric_cols = [
        "distance_km",
        "package_weight_kg",
        "delivery_time_hours",
        "expected_time_hours",
        "delivery_rating",
        "delivery_cost"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna()

    # Revenue
    df["revenue"] = df["delivery_cost"]

    # Weight Category
    # (As per your original requirement)

    df["weight_category"] = np.where(
        df["package_weight_kg"] > 20,
        "light",
        "heavy"
    )

    return df


df = load_data()

# ----------------------------------------------------------
# Sidebar
# ----------------------------------------------------------

st.sidebar.header("Filters")

region = st.sidebar.multiselect(
    "Region",
    sorted(df["region"].unique()),
    default=sorted(df["region"].unique())
)

vehicle = st.sidebar.multiselect(
    "Vehicle Type",
    sorted(df["vehicle_type"].unique()),
    default=sorted(df["vehicle_type"].unique())
)

mode = st.sidebar.multiselect(
    "Delivery Mode",
    sorted(df["delivery_mode"].unique()),
    default=sorted(df["delivery_mode"].unique())
)

weather = st.sidebar.multiselect(
    "Weather",
    sorted(df["weather_condition"].unique()),
    default=sorted(df["weather_condition"].unique())
)

package = st.sidebar.multiselect(
    "Package Type",
    sorted(df["package_type"].unique()),
    default=sorted(df["package_type"].unique())
)

filtered = df[
    (df["region"].isin(region)) &
    (df["vehicle_type"].isin(vehicle)) &
    (df["delivery_mode"].isin(mode)) &
    (df["weather_condition"].isin(weather)) &
    (df["package_type"].isin(package))
]

# ----------------------------------------------------------
# KPI Cards
# ----------------------------------------------------------

total_delivery = len(filtered)
total_revenue = filtered["revenue"].sum()
avg_revenue = filtered["revenue"].mean()
avg_rating = filtered["delivery_rating"].mean()

delay_pct = (
    filtered["delayed"]
    .eq("yes")
    .mean() * 100
)

failure_pct = (
    filtered["delivery_status"]
    .eq("failed")
    .mean() * 100
)

avg_cost = filtered["delivery_cost"].mean()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Deliveries", f"{total_delivery:,}")
c2.metric("Revenue", f"₹ {total_revenue:,.0f}")
c3.metric("Avg Revenue", f"₹ {avg_revenue:,.0f}")
c4.metric("Avg Rating", f"{avg_rating:.2f}")

c5, c6, c7 = st.columns(3)

c5.metric("Delayed %", f"{delay_pct:.1f}%")
c6.metric("Failure %", f"{failure_pct:.1f}%")
c7.metric("Avg Delivery Cost", f"₹ {avg_cost:,.0f}")

st.markdown("---")

# ==========================================================
# Charts Section - 1
# ==========================================================

# -----------------------------
# Row 1
# -----------------------------

col1, col2 = st.columns(2)

# 1. Average Revenue by Region

with col1:

    revenue_region = (
        filtered.groupby("region", as_index=False)["revenue"]
        .mean()
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        revenue_region,
        x="region",
        y="revenue",
        color="region",
        text_auto=".2f",
        title="Average Revenue by Region"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

# 2. Average Rating by Delivery Mode

with col2:

    rating = (
        filtered.groupby("delivery_mode", as_index=False)["delivery_rating"]
        .mean()
        .sort_values("delivery_rating", ascending=False)
    )

    fig = px.bar(
        rating,
        x="delivery_mode",
        y="delivery_rating",
        color="delivery_mode",
        text_auto=".2f",
        title="Average Rating by Delivery Mode"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Row 2
# -----------------------------

col3, col4 = st.columns(2)

# 3. Revenue & Delay by Weight Category

with col3:

    weight = (
        filtered.groupby(
            ["weight_category", "delayed"],
            as_index=False
        )["revenue"]
        .sum()
    )

    fig = px.bar(
        weight,
        x="weight_category",
        y="revenue",
        color="delayed",
        barmode="group",
        text_auto=".2s",
        title="Revenue by Package Weight & Delay"
    )

    st.plotly_chart(fig, use_container_width=True)

# 4. Failure % by Delivery Mode

with col4:

    failure = (
        filtered.groupby("delivery_mode")["delivery_status"]
        .apply(lambda x: (x == "failed").mean() * 100)
        .reset_index(name="failure_pct")
    )

    fig = px.bar(
        failure,
        x="delivery_mode",
        y="failure_pct",
        color="delivery_mode",
        text_auto=".1f",
        title="Failure % by Delivery Mode"
    )

    fig.update_layout(
        yaxis_title="Failure %",
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Row 3
# -----------------------------

col5, col6 = st.columns(2)

# 5. Delay % by Weather & Package Type

with col5:

    delay = (
        filtered.groupby(
            ["weather_condition", "package_type"]
        )["delayed"]
        .apply(lambda x: (x == "yes").mean() * 100)
        .reset_index(name="delay_pct")
    )

    fig = px.imshow(
        delay.pivot(
            index="package_type",
            columns="weather_condition",
            values="delay_pct"
        ),
        text_auto=".1f",
        aspect="auto",
        title="Delay % by Weather & Package Type",
        color_continuous_scale="Reds"
    )

    st.plotly_chart(fig, use_container_width=True)

# 6. Revenue Share by Vehicle & Package Type

with col6:

    revenue_share = (
        filtered.groupby(
            ["vehicle_type", "package_type"],
            as_index=False
        )["revenue"]
        .sum()
    )

    fig = px.bar(
        revenue_share,
        x="vehicle_type",
        y="revenue",
        color="package_type",
        barmode="stack",
        text_auto=".2s",
        title="Revenue Share by Vehicle & Package Type"
    )

    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ==========================================================
# Charts Section - 2
# ==========================================================

# -----------------------------
# Row 4
# -----------------------------

col7, col8 = st.columns(2)

# Revenue by Delivery Partner

with col7:

    partner = (
        filtered.groupby("delivery_partner", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
    )

    fig = px.bar(
        partner,
        x="delivery_partner",
        y="revenue",
        color="delivery_partner",
        text_auto=".2s",
        title="Revenue by Delivery Partner"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)


# Revenue by Vehicle Type

with col8:

    vehicle = (
        filtered.groupby("vehicle_type", as_index=False)["revenue"]
        .sum()
    )

    fig = px.pie(
        vehicle,
        names="vehicle_type",
        values="revenue",
        hole=0.45,
        title="Revenue Share by Vehicle Type"
    )

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Row 5
# -----------------------------

col9, col10 = st.columns(2)

# Average Delivery Time

with col9:

    delivery_time = (
        filtered.groupby("delivery_mode", as_index=False)["delivery_time_hours"]
        .mean()
    )

    fig = px.bar(
        delivery_time,
        x="delivery_mode",
        y="delivery_time_hours",
        color="delivery_mode",
        text_auto=".2f",
        title="Average Delivery Time (Hours)"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)


# Delayed Deliveries by Region

with col10:

    region_delay = (
        filtered.groupby("region")["delayed"]
        .apply(lambda x: (x == "yes").sum())
        .reset_index(name="Delayed Deliveries")
    )

    fig = px.bar(
        region_delay,
        x="region",
        y="Delayed Deliveries",
        color="region",
        text_auto=True,
        title="Delayed Deliveries by Region"
    )

    fig.update_layout(showlegend=False)

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Row 6
# -----------------------------

col11, col12 = st.columns(2)

# Delivery Status

with col11:

    fig = px.pie(
        filtered,
        names="delivery_status",
        hole=0.45,
        title="Delivery Status Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)


# Package Type

with col12:

    fig = px.pie(
        filtered,
        names="package_type",
        hole=0.45,
        title="Package Type Distribution"
    )

    st.plotly_chart(fig, use_container_width=True)

# ==========================================================
# Executive Insights
# ==========================================================

st.markdown("---")

st.subheader("📌 Executive Insights")

if len(filtered) > 0:

    best_region = (
        filtered.groupby("region")["revenue"]
        .sum()
        .idxmax()
    )

    best_vehicle = (
        filtered.groupby("vehicle_type")["revenue"]
        .sum()
        .idxmax()
    )

    highest_failure = (
        filtered.groupby("delivery_mode")["delivery_status"]
        .apply(lambda x: (x == "failed").mean())
        .idxmax()
    )

    highest_delay = (
        filtered.groupby("weather_condition")["delayed"]
        .apply(lambda x: (x == "yes").mean())
        .idxmax()
    )

    st.success(f"🏆 Highest Revenue Region: **{best_region.title()}**")

    st.info(f"🚛 Best Revenue Vehicle: **{best_vehicle.title()}**")

    st.warning(f"⚠ Highest Failure Delivery Mode: **{highest_failure.title()}**")

    st.error(f"🌧 Highest Delay Weather: **{highest_delay.title()}**")

else:

    st.warning("No records available for the selected filters.")

# ==========================================================
# Download Data
# ==========================================================

st.markdown("---")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "📥 Download Filtered Data",
    csv,
    "fleet_dashboard_filtered.csv",
    "text/csv"
)

# ==========================================================
# Footer
# ==========================================================

st.markdown("---")

st.caption(
    "Fleet Management Dashboard | Built using Streamlit • Pandas • Plotly"
)