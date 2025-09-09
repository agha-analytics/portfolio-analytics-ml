# app.py (optimized)
import requests
import os
from datetime import datetime
import streamlit as st
import json
import pandas as pd
import os
import pandas as pd
import plotly.express as px

from ui_filters import sidebar_filters, apply_filters

# ----------------------------- Money formatting helpers -----------------------------
def fmt_money(x, decimals: int = 0) -> str:
    """Format numbers like $12,345 (or with decimals if decimals>0)."""
    try:
        if x is None:
            return "$0"
        return f"${x:,.{decimals}f}"
    except Exception:
        return "$0"

def apply_money_format_bar(fig):
    """For px.bar: nice $ labels, hover, and axis."""
    fig.update_traces(
        texttemplate="$%{y:,.0f}",
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Weekly Sales: $%{y:,.0f}<extra></extra>"
    )
    fig.update_yaxes(tickprefix="$", separatethousands=True)

def apply_money_format_treemap(fig):
    """For px.treemap: $ hover + optional on-tile value text."""
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Sales: $%{value:,.0f}<extra></extra>",
        texttemplate="$%{value:,.0f}"
    )

def apply_money_format_line(fig):
    """For px.line: $ hover + axis."""
    fig.update_traces(
        hovertemplate="Date: %{x|%Y-%m-%d}<br>Weekly Sales: $%{y:,.0f}<extra></extra>"
    )
    fig.update_yaxes(tickprefix="$", separatethousands=True)


# ----------------------------- Utilities -----------------------------
def _abs_path(*parts) -> str:
    return os.path.join(os.path.dirname(__file__), *parts)

def _verify_file(path: str, label: str) -> None:
    if not os.path.exists(path):
        data_dir = os.path.dirname(path)
        try:
            listing = sorted(os.listdir(data_dir))
        except Exception:
            listing = []
        msg = (
            f"Could not find {label} at:\n\n`{path}`\n\n"
            + ("Files found in the data folder:\n\n- " + "\n- ".join(listing)
               if listing else "The data folder is empty or not accessible.")
        )
        st.error(msg)
        st.stop()

@st.cache_data(show_spinner=False)
def _load_csv(path: str, label: str) -> pd.DataFrame:
    """Read CSV once and cache; safely parse 'Date' only if present."""
    _verify_file(path, label)
    try:
        return pd.read_csv(path, parse_dates=["Date"])
    except Exception:
        df = pd.read_csv(path)
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        return df

@st.cache_data(show_spinner=False)
def _merged_frame(sales_path: str, stores_path: str, features_path: str) -> pd.DataFrame:
    """Load the three CSVs and return one merged frame."""
    sales = _load_csv(sales_path, "Sales data")
    stores = _load_csv(stores_path, "Stores data")
    features = _load_csv(features_path, "Features data")

    # Ensure Date is datetime where present
    if "Date" in sales.columns:
        sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce")
    if "Date" in features.columns:
        features["Date"] = pd.to_datetime(features["Date"], errors="coerce")

    # Standard Walmart schema merge: sales -> stores; then join features on Store+Date
    df = sales.merge(stores, on="Store", how="left").merge(features, on=["Store", "Date"], how="left")
    return df

# ----------------------------- Top bar -----------------------------
def render_topbar(name_role: str = "Agha Alagha - Data Analyst") -> None:
    left, right = st.columns([3, 1])
    with left:
        st.markdown(f"### {name_role}")
    with right:
        today = datetime.now().strftime("%A, %b %d, %Y")
        st.markdown(f"<div style='text-align:right; opacity:0.8'>{today}</div>", unsafe_allow_html=True)
    st.markdown("---")


# ------------------------- Adaptive chart helpers -------------------------
def render_dept_view(view: pd.DataFrame) -> None:
    """Treemap if >1 dept and not too many categories, else a weekly trend line."""
    if view.empty:
        st.info("No data for current filters.")
        return

    n_depts = view["Dept"].astype(str).nunique()

    # Avoid huge treemaps (render time balloons with 300+ tiles)
    if n_depts > 1 and n_depts <= 150:
        agg = (
            view.assign(Dept=view["Dept"].astype(str))
            .groupby("Dept", as_index=False)["Weekly_Sales"]
            .sum()
        )
        fig = px.treemap(agg, path=["Dept"], values="Weekly_Sales", title="Sales by Department")
        apply_money_format_treemap(fig)
        st.plotly_chart(fig, use_container_width=True)
    elif n_depts > 150:
        st.info("Too many departments to show a treemap clearly; showing trend instead.")
        s = (view.groupby("Date", as_index=False)["Weekly_Sales"].sum().sort_values("Date"))
        fig = px.line(s, x="Date", y="Weekly_Sales", title="Weekly Sales (All Departments)")
        apply_money_format_line(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        s = (view.groupby("Date", as_index=False)["Weekly_Sales"].sum().sort_values("Date"))
        dept_label = view["Dept"].astype(str).iloc[0]
        fig = px.line(s, x="Date", y="Weekly_Sales", title=f"Weekly Sales – Dept {dept_label}")
        apply_money_format_line(fig)
        st.plotly_chart(fig, use_container_width=True)

def render_store_ranking(view: pd.DataFrame, store_filter_label: str) -> None:
    """Ranking when multiple stores; otherwise a KPI for the single store."""
    if view.empty:
        st.info("No data for current filters.")
        return

    n_stores = view["Store"].astype(str).nunique()
    if n_stores > 1 and store_filter_label == "All Stores":
        agg = (
            view.assign(Store=view["Store"].astype(str))
            .groupby("Store", as_index=False)["Weekly_Sales"]
            .sum()
            .sort_values("Weekly_Sales", ascending=False)
        )
        fig = px.bar(agg, x="Store", y="Weekly_Sales", title="Store Ranking (Total Sales)")
        apply_money_format_bar(fig)
        st.plotly_chart(fig, use_container_width=True)
    else:
        total = float(view["Weekly_Sales"].sum())
        weeks = int(view["Date"].nunique()) if "Date" in view.columns else None
        st.metric("Total Sales (Current Store)", fmt_money(total), delta=f"{weeks} weeks" if weeks else None)

def render_simple_forecast(view: pd.DataFrame, window: int = 8, horizon: int = 12) -> None:
    """
    Lightweight 'forecast': plot weekly sales + moving average and extend the last MA
    as a naive projection for `horizon` future periods. No external libs required.
    """
    if view.empty:
        st.info("No data to forecast for current filters.")
        return

    # Aggregate to weekly series
    s = (
        view.groupby("Date", as_index=False)["Weekly_Sales"]
        .sum()
        .sort_values("Date")
        .reset_index(drop=True)
    )

    if len(s) < window + 2:
        st.info("Not enough history to show a moving-average forecast.")
        fig = px.line(s, x="Date", y="Weekly_Sales", title="Weekly Sales")
        apply_money_format_line(fig)
        st.plotly_chart(fig, use_container_width=True)
        return

    # Moving average
    s["MA"] = s["Weekly_Sales"].rolling(window=window, min_periods=1).mean()

    # --- Build future frame with EXACTLY `horizon` rows ---
    last_date = pd.to_datetime(s["Date"].iloc[-1])
    inferred = pd.infer_freq(pd.to_datetime(s["Date"]))
    freq = inferred if inferred is not None else "W"   # default to weekly

    first_future = last_date + pd.tseries.frequencies.to_offset(freq)
    future_dates = pd.date_range(first_future, periods=horizon, freq=freq)

    future = pd.DataFrame({
        "Date": future_dates,
        "Weekly_Sales": [None] * horizon,          # no actuals yet
        "MA": [float(s["MA"].iloc[-1])] * horizon  # hold last MA flat
    })

    plot_df = pd.concat([s, future], ignore_index=True)

    fig = px.line(
        plot_df, x="Date", y=["Weekly_Sales", "MA"],
        labels={"value": "Sales", "variable": "Series"},
        title=f"Weekly Sales (moving average={window}) with naive {horizon}-period projection",
    )
    apply_money_format_line(fig)
    st.plotly_chart(fig, use_container_width=True)


# --------------------------------- App ---------------------------------
def _get_api_key() -> str | None:
    """
    Return the OpenAI API key from Streamlit secrets or env var.
    Put your key in .streamlit/secrets.toml as:
      OPENAI_API_KEY="sk-..."
    or in the environment.
    """
    return st.secrets.get("OPENAI_API_KEY", None) if hasattr(st, "secrets") else os.getenv("OPENAI_API_KEY")


def _frame_context(view: pd.DataFrame, max_rows: int = 200, max_chars: int = 6000) -> str:
    """
    Build a compact JSON context from the filtered dataframe without creating
    invalid JSON. We shrink by reducing sample size, not by truncating strings.
    """
    if view.empty:
        return json.dumps({"note": "No rows in the current filtered view."})

    # Basic schema + range
    schema = {c: str(view[c].dtype) for c in view.columns}
    start = str(pd.to_datetime(view["Date"].min()).date()) if "Date" in view.columns else "n/a"
    end   = str(pd.to_datetime(view["Date"].max()).date()) if "Date" in view.columns else "n/a"
    rows  = int(len(view))

    # Keep a few useful columns if present
    keep_cols = [c for c in ["Date", "Store", "Dept", "Type", "Weekly_Sales", "IsHoliday"] if c in view.columns]
    samp = view[keep_cols].copy() if keep_cols else view.copy()

    # Make JSON-friendly
    if "Date" in samp.columns:
        samp["Date"] = pd.to_datetime(samp["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
    for col in samp.select_dtypes(include=["float", "float64", "float32"]).columns:
        samp[col] = samp[col].round(2)

    # Start with up to max_rows records; shrink if needed to meet max_chars
    hi = min(max_rows, len(samp))
    lo = 1
    best_json = None
    best_records = []

    # Binary search number of rows that fits under max_chars
    while lo <= hi:
        mid = (lo + hi) // 2
        records = samp.head(mid).to_dict(orient="records")

        ctx_obj = {
            "schema": schema,
            "date_range": {"start": start, "end": end},
            "rows_in_view": rows,
            "sample_rows": len(records),
            "sample_records": records,
            "notes": "Sample of current filtered view; do not infer totals from sample."
        }
        s = json.dumps(ctx_obj, ensure_ascii=False)

        if len(s) <= max_chars:
            best_records = records
            best_json = s
            lo = mid + 1
        else:
            hi = mid - 1

    # If even 1 row is too big, drop the sample entirely
    if not best_records:
        ctx_obj = {
            "schema": schema,
            "date_range": {"start": start, "end": end},
            "rows_in_view": rows,
            "sample_rows": 0,
            "sample_records": [],
            "notes": "Context too large; sample omitted."
        }
        return json.dumps(ctx_obj, ensure_ascii=False)

    # Return the last valid JSON we computed
    return best_json

def main() -> None:
    st.set_page_config(page_title="Sales & Customer Analytics Dashboard", layout="wide")

    # ---- Top bar (name + date) ----
    render_topbar("Agha Alagha - Data Analyst")

    st.title("📊 Sales & Customer Analytics Dashboard")
    st.caption("Interactive view of sales trends, segments, and KPIs (Walmart retail dataset).")

    # ---- Cached load & merge ----
    sales_fp    = _abs_path("data", "sales.csv")
    stores_fp   = _abs_path("data", "stores.csv")
    features_fp = _abs_path("data", "features.csv")




    with st.spinner("Loading data..."):
        df = _merged_frame(sales_fp, stores_fp, features_fp)

    # ---- Sidebar filters ----
    f = sidebar_filters(df)
    view = apply_filters(df, f)

    # --------------------------- Tabs ---------------------------
    tab_overview, tab_segments, tab_ai = st.tabs(["Overview", "Segments & Forecast", "AI Insights"])

    # -------- Overview tab (compute only what we need) --------
    with tab_overview:
        st.header("Overview")
        if view.empty:
            st.info("No data for current filters.")
        else:
            total_sales = float(view["Weekly_Sales"].sum())
            avg_week    = float(view["Weekly_Sales"].mean())
            weeks       = int(view["Date"].nunique())

            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sales", fmt_money(total_sales))
            c2.metric("Average / Week", fmt_money(avg_week))
            c3.metric("Weeks in View", weeks)

            st.subheader("Treemap of Sales by Department")
            render_dept_view(view)

            st.subheader("Top & Bottom Stores")
            render_store_ranking(view, store_filter_label=f.store)

    # -------- Segments & Forecast tab --------
    with tab_segments:
        st.header("Segments & Forecast")

        if not view.empty and {"Type", "Weekly_Sales"}.issubset(view.columns):
            seg = (
                view.assign(Type=view["Type"].astype(str))
                .groupby("Type", as_index=False)["Weekly_Sales"]
                .sum()
                .sort_values("Weekly_Sales", ascending=False)
            )
            if len(seg) > 0:
                fig = px.bar(seg, x="Type", y="Weekly_Sales", title="Sales by Store Type")
                apply_money_format_bar(fig)
                st.plotly_chart(fig, use_container_width=True)

        st.subheader("Forecast (simple moving-average projection)")
        render_simple_forecast(view, window=8, horizon=12)

       # -------- AI Insights tab --------
    with tab_ai:
        st.header("AI Insights")

        # --- automatic summary (kept from your current version) ---
        if view.empty:
            st.info("No data for current filters.")
        else:
            total = float(view["Weekly_Sales"].sum())
            weeks = int(view["Date"].nunique())
            per_week = total / weeks if weeks else 0

            top_dept = view.groupby("Dept")["Weekly_Sales"].sum().sort_values(ascending=False).head(1)
            top_store = view.groupby("Store")["Weekly_Sales"].sum().sort_values(ascending=False).head(1)

            st.markdown("**Summary**")
            st.markdown(
                f"- Total sales in the selected period: **{fmt_money(total)}** over **{weeks}** weeks "
                f"(~ **{fmt_money(per_week)}** per week)."
            )
            if len(top_dept) > 0:
                td_name = str(top_dept.index[0]); td_val = float(top_dept.iloc[0])
                st.markdown(f"- Top department: **{td_name}** ({fmt_money(td_val)}).")
            if len(top_store) > 0:
                ts_name = str(top_store.index[0]); ts_val = float(top_store.iloc[0])
                st.markdown(f"- Top store: **{ts_name}** ({fmt_money(ts_val)}).")

            ts = view.groupby("Date", as_index=False)["Weekly_Sales"].sum().sort_values("Date")
            if len(ts) >= 8:
                last4 = ts["Weekly_Sales"].tail(4).mean()
                prev4 = ts["Weekly_Sales"].tail(8).head(4).mean()
                delta = last4 - prev4
                pct = (delta / prev4 * 100) if prev4 else 0
                direction = "up" if delta >= 0 else "down"
                st.markdown(
                    f"- Recent momentum: average of last 4 weeks is **{fmt_money(last4)}** "
                    f"({direction} **{pct:,.1f}%** vs prior 4 weeks)."
                )

        st.markdown("---")

        # --- Ask a specific question (OpenAI) ---
        st.subheader("Ask a specific question")
        api_key = _get_api_key()
        if not api_key:
            st.warning("Add your OpenAI API key to **.streamlit/secrets.toml** as `OPENAI_API_KEY` (or set the environment variable) to enable this feature.")
        else:
            col1, col2 = st.columns([3, 1])
            with col1:
                user_q = st.text_input("Ask the AI any Question about your data", placeholder="e.g., Which store types grew fastest in the last quarter?")

            if st.button("Generate Insights", type="primary", use_container_width=False):
                if not user_q.strip():
                    st.info("Please type a question first.")
                elif view.empty:
                    st.info("No data in the current filters to analyze.")
                else:
                    context = _frame_context(view)
                    import requests
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    }
                    # NOTE: Keep behavior same; define a default model to avoid NameError if not set elsewhere
                    model = "gpt-4o-mini"

                    payload = {
                        "model": model,
                        "messages": [
                            {"role": "system",
                             "content": (
                                 "You are a helpful retail analytics assistant. "
                                 "Use the provided JSON context to answer the user's question with numbers, "
                                 "short bullet points, and avoid inventing data that is not present."
                             )},
                            {"role": "user",
                             "content": f"DATA CONTEXT (JSON):\n{context}\n\nQUESTION:\n{user_q}"}
                        ],
                        "temperature": 0.2,
                    }
                    with st.spinner("Thinking..."):
                        try:
                            resp = requests.post("https://api.openai.com/v1/chat/completions",
                                                 headers=headers, json=payload, timeout=60)
                            resp.raise_for_status()
                            content = resp.json()["choices"][0]["message"]["content"]
                            st.markdown("#### AI Answer")
                            st.write(content)
                        except Exception as e:
                            st.error(f"OpenAI request failed: {e}")

# ---------------------------- runner ----------------------------
def _run_app():
    # Paint something immediately and catch any errors so you don't see a blank page
    st.markdown("<div style='height:1px'></div>", unsafe_allow_html=True)
    try:
        main()
    except Exception as e:
        st.error("The app crashed while rendering. See details below:")
        st.exception(e)

if __name__ == "__main__":
    _run_app()
