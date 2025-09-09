# segmentation.py
import streamlit as st
import plotly.express as px

def render_segments(view):
    st.subheader("Treemap of Sales by Department")
    treemap = px.treemap(view, path=["Dept"], values="Sales", title="Sales by Department")
    treemap.update_traces(hovertemplate="Dept=%{label}<br>Sales=$%{value:,.0f}")
    st.plotly_chart(treemap, use_container_width=True)

    st.subheader("Top & Bottom Stores")
    store_rank = (
        view.groupby("Store")["Sales"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    bar_chart = px.bar(
        store_rank,
        x="Store",
        y="Sales",
        title="Store Ranking",
        text="Sales"  # show labels on bars
    )

    # Format hover + labels + y-axis
    bar_chart.update_traces(
        hovertemplate="Store=%{x}<br>Sales=$%{y:,.0f}",
        texttemplate="$%{y:,.0f}",
        textposition="outside"
    )
    bar_chart.update_yaxes(tickprefix="$", separatethousands=True)

    st.plotly_chart(bar_chart, use_container_width=True)
