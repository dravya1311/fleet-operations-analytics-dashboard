import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------
# Page Configuration
# -------------------------------
st.set_page_config(
    page_title="Fleet Operations Dashboard",
    page_icon="🚛",
    layout="wide"
)

st.title("🚛 Fleet Operations Dashboard")
st.markdown("---")

# -------------------------------
# Load Data
# -------------------------------
@st.cache_data
def load_data():

    df = pd.read_csv("transport data(3).csv", header=1)

    numeric_cols = [
        "KM Traveled",
        "Liters",
        "Fuel",
        "Maintenance",
        "Fixed Costs"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Date"] = pd.to_datetime(
        df["Date"],
        dayfirst=True,
        errors="coerce"
    )

    df = df.dropna(subset=["Date"])

    return df

df = load_data()

# -------------------------------
# Sidebar Filters
# -------------------------------
st.sidebar.header("Filters")

truck = st.sidebar.multiselect(
    "Truck",
    sorted(df["Truck ID"].unique())
)

driver = st.sidebar.multiselect(
    "Driver",
    sorted(df["Drive ID"].unique())
)

if truck:
    df = df[df["Truck ID"].isin(truck)]

if driver:
    df = df[df["Drive ID"].isin(driver)]

# -------------------------------
# KPI Calculations
# -------------------------------
total_km = df["KM Traveled"].sum()

fleet_size = df["Truck ID"].nunique()

fuel_cost = df["Fuel"].sum()

maintenance_cost = df["Maintenance"].sum()

fixed_cost = df["Fixed Costs"].sum()

operating_cost = fuel_cost + maintenance_cost + fixed_cost

cost_per_km = (
    operating_cost / total_km
    if total_km > 0 else 0
)

fuel_cost_per_km = (
    fuel_cost / total_km
    if total_km > 0 else 0
)

mileage = (
    total_km / df["Liters"].sum()
    if df["Liters"].sum() > 0 else 0
)

# -------------------------------
# KPI Cards
# -------------------------------
c1, c2, c3, c4, c5, c6 = st.columns(6)

c1.metric("Total KM", f"{total_km:,.0f}")

c2.metric("Fleet Size", fleet_size)

c3.metric("Operating Cost", f"₹{operating_cost:,.0f}")

c4.metric("Cost / KM", f"₹{cost_per_km:.2f}")

c5.metric("Fuel Cost / KM", f"₹{fuel_cost_per_km:.2f}")

c6.metric("Mileage", f"{mileage:.2f} km/L")

st.markdown("---")

# -------------------------------
# Distance by Truck
# -------------------------------
truck_km = (
    df.groupby("Truck ID")["KM Traveled"]
      .sum()
      .sort_values(ascending=False)
      .head(10)
      .reset_index()
)

fig1 = px.bar(
    truck_km,
    x="Truck ID",
    y="KM Traveled",
    title="Top 10 Trucks by Distance"
)

# -------------------------------
# Cost Breakdown
# -------------------------------
cost_df = pd.DataFrame({
    "Category": [
        "Fuel",
        "Maintenance",
        "Fixed Cost"
    ],
    "Amount": [
        fuel_cost,
        maintenance_cost,
        fixed_cost
    ]
})

fig2 = px.pie(
    cost_df,
    names="Category",
    values="Amount",
    hole=0.5,
    title="Operating Cost Breakdown"
)

# -------------------------------
# Daily KM Trend
# -------------------------------
daily = (
    df.groupby("Date")["KM Traveled"]
      .sum()
      .reset_index()
)

fig3 = px.line(
    daily,
    x="Date",
    y="KM Traveled",
    title="Daily Distance Trend"
)

# -------------------------------
# Truck-wise Cost per KM
# -------------------------------
truck_cost = (
    df.groupby("Truck ID")
      .agg({
          "KM Traveled":"sum",
          "Fuel":"sum",
          "Maintenance":"sum",
          "Fixed Costs":"sum"
      })
)

truck_cost["Cost per KM"] = (
    (
        truck_cost["Fuel"] +
        truck_cost["Maintenance"] +
        truck_cost["Fixed Costs"]
    )
    /
    truck_cost["KM Traveled"]
)

truck_cost = (
    truck_cost
    .sort_values("Cost per KM", ascending=False)
    .head(10)
    .reset_index()
)

fig4 = px.bar(
    truck_cost,
    x="Truck ID",
    y="Cost per KM",
    title="Top 10 Trucks by Cost per KM"
)

# -------------------------------
# Layout
# -------------------------------
left, right = st.columns(2)

with left:
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

with right:
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig4, use_container_width=True)

# -------------------------------
# Data Table
# -------------------------------
st.markdown("## Fleet Data")

st.dataframe(df, use_container_width=True)

# -------------------------------
# Download Button
# -------------------------------
csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="fleet_filtered_data.csv",
    mime="text/csv"
)
# -----------------------------------------
# Operations Insights
# -----------------------------------------
st.markdown("---")
st.subheader("📌 Fleet Operations Insights")

top_truck = truck_km.iloc[0]["Truck ID"]
top_km = truck_km.iloc[0]["KM Traveled"]

highest_cost_truck = truck_cost.iloc[0]["Truck ID"]
highest_cost = truck_cost.iloc[0]["Cost per KM"]

fuel_percent = (fuel_cost / operating_cost) * 100 if operating_cost else 0
maint_percent = (maintenance_cost / operating_cost) * 100 if operating_cost else 0
fixed_percent = (fixed_cost / operating_cost) * 100 if operating_cost else 0

st.info(f"""
### Key Insights

✅ **Total Fleet Distance:** **{total_km:,.0f} KM**

🚛 **Most Utilized Truck:** **{top_truck}**
covered **{top_km:,.0f} KM**

💰 **Highest Operating Cost/KM:** **{highest_cost_truck}**
at **₹{highest_cost:.2f}/KM**

⛽ Fuel contributes **{fuel_percent:.1f}%**
of total operating cost.

🔧 Maintenance contributes **{maint_percent:.1f}%**
of total operating cost.

🏢 Fixed cost contributes **{fixed_percent:.1f}%**
of total operating cost.

📊 Fleet Average Cost/KM is
**₹{cost_per_km:.2f}**

⛽ Fleet Average Mileage is
**{mileage:.2f} KM/L**
""")
