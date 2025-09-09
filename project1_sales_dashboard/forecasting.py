# forecasting.py
import streamlit as st
import plotly.express as px
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

def render_forecast(view: pd.DataFrame, periods: int = 12) -> None:
    st.subheader(f"{periods}-Week Forecast (Holt-Winters)")

    weekly = view.groupby("Date")["Sales"].sum().sort_index()
    if len(weekly) < 60:  # need enough history for seasonality=52
        st.info("Not enough historical data to fit a seasonal HW model (needs ~60+ points). Try broadening filters.")
        return

    try:
        model = ExponentialSmoothing(weekly, trend="add", seasonal="add", seasonal_periods=52)
        fit = model.fit()
        fc = fit.forecast(periods)

        # Base chart = historical line
        hist_fig = px.line(
            weekly.reset_index(),
            x="Date",
            y="Sales",
            title="Historical + Forecast"
        )

        # Forecast line
        hist_fig.add_scatter(
            x=fc.index,
            y=fc.values,
            mode="lines+markers",
            name="Forecast"
        )

        # Currency formatting: hovers + axis
        # Trace 0: historical
        hist_fig.data[0].hovertemplate = "Date=%{x|%Y-%m-%d}<br>Sales=$%{y:,.0f}"
        # Trace 1: forecast
        hist_fig.data[1].hovertemplate = "Date=%{x|%Y-%m-%d}<br>Forecast=$%{y:,.0f}"

        hist_fig.update_yaxes(tickprefix="$", separatethousands=True)
        st.plotly_chart(hist_fig, use_container_width=True)

    except Exception as e:
        st.error(f"Forecast failed: {e}")
