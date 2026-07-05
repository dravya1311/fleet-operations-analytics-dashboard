
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Fleet Management Dashboard", layout="wide")

@st.cache_data
def load():
    df=pd.read_csv("transport data.csv")
    df.columns=df.columns.str.strip().str.lower()
    df=df.drop_duplicates()
    for c in df.select_dtypes(include='object').columns:
        df[c]=df[c].astype(str).str.strip().str.lower()
    for c in ['delivery_cost','delivery_rating','package_weight_kg','delivery_time_hours','expected_time_hours']:
        if c in df.columns:
            df[c]=pd.to_numeric(df[c],errors='coerce')
    df=df.dropna()
    df['revenue']=df['delivery_cost']
    df['weight_category']=np.where(df['package_weight_kg']>20,'light','heavy')
    return df

df=load()

for f in ['region','vehicle_type','delivery_mode','weather_condition','package_type']:
    if f in df.columns:
        vals=st.sidebar.multiselect(f.title(),sorted(df[f].unique()),default=sorted(df[f].unique()))
        df=df[df[f].isin(vals)]

c1,c2,c3,c4=st.columns(4)
c1.metric("Deliveries",len(df))
c2.metric("Revenue",f"{df['revenue'].sum():,.0f}")
c3.metric("Avg Rating",round(df['delivery_rating'].mean(),2))
delay=(df['delayed'].eq('yes').mean()*100) if 'delayed' in df.columns else 0
c4.metric("Delayed %",f"{delay:.1f}%")

charts=[
('Avg Revenue by Region',px.bar(df.groupby('region',as_index=False)['revenue'].mean(),x='region',y='revenue')),
('Avg Rating by Delivery Mode',px.bar(df.groupby('delivery_mode',as_index=False)['delivery_rating'].mean(),x='delivery_mode',y='delivery_rating')),
('Revenue by Vehicle Type',px.bar(df.groupby('vehicle_type',as_index=False)['revenue'].sum(),x='vehicle_type',y='revenue')),
('Revenue by Delivery Partner',px.bar(df.groupby('delivery_partner',as_index=False)['revenue'].sum(),x='delivery_partner',y='revenue')),
('Delivery Status',px.pie(df,names='delivery_status'))
]
for i,(t,fig) in enumerate(charts):
    st.subheader(t); st.plotly_chart(fig,use_container_width=True)

st.subheader("Failure % by Delivery Mode")
fail=df.groupby('delivery_mode').apply(lambda x:(x['delivery_status'].eq('failed').mean()*100)).reset_index(name='failure_pct')
st.plotly_chart(px.bar(fail,x='delivery_mode',y='failure_pct'),use_container_width=True)

st.subheader("Delay % by Weather & Package")
heat=df.groupby(['weather_condition','package_type']).apply(lambda x:x['delayed'].eq('yes').mean()*100).reset_index(name='delay_pct')
st.plotly_chart(px.density_heatmap(heat,x='weather_condition',y='package_type',z='delay_pct'),use_container_width=True)

st.download_button("Download Filtered Data",df.to_csv(index=False),"filtered_data.csv")
