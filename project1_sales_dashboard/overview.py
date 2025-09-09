# overview.py
import streamlit as st
import plotly.express as px
import pandas as pd

def render_overview(view: pd.DataFrame) -> None:
    st.header("Overview")
    st.write("Interactive view of sales trends, segments, and KPIs (Walmart retail dataset).")

    total_sales = float(view["Sales"].sum())
    avg_sales = float(view["Sales"].mean()) if len(view) else 0.0
    weeks = int(view["Date"].nunique())
    best_week = float(view.groupby("Date")["Sales"].sum().max()) if weeks else 0.0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("💰 Total Sales", f"${total_sales:,.0f}")
    kpi2.metric("📅 Average / Week", f"${avg_sales:,.0f}")
    kpi3.metric("🗓 Weeks in View", weeks)
    kpi4.metric("🏆 Best Week", f"${best_week:,.0f}")

    st.subheader("Sales Over Time (All Stores in Filter)")
    if view.empty:
        st.info("No data for current filters.")
        return

    series = (view.groupby("Date")["Sales"]
                   .sum()
                   .reset_index()
                   .sort_values("Date"))

    fig = px.line(series, x="Date", y="Sales", markers=True, title="Total Sales Over Time")
    # Currency: hover + y-axis
    fig.update_traces(hovertemplate="Date=%{x|%Y-%m-%d}<br>Sales=$%{y:,.0f}")
    fig.update_yaxes(tickprefix="$", separatethousands=True)
    st.plotly_chart(fig, use_container_width=True)
