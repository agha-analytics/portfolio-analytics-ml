# ui_filters.py
import streamlit as st
import pandas as pd
from dataclasses import dataclass

# ---- Widget keys ----
K_STORE = "f_store"
K_DEPT = "f_dept"
K_REGION = "f_region"
K_HOLIDAYS = "f_holidays"
K_START = "f_start"
K_END = "f_end"

@dataclass
class Filters:
    store: str
    dept: str
    region: str
    only_holidays: bool
    start_date: pd.Timestamp
    end_date: pd.Timestamp

# ----------------- Helpers -----------------
def _coerce_date_column(df: pd.DataFrame, col: str = "Date") -> pd.DataFrame:
    if col not in df.columns:
        st.error(f"Expected a '{col}' column in the dataset for date filtering.")
        st.stop()
    if not pd.api.types.is_datetime64_any_dtype(df[col]):
        df = df.copy()
        df[col] = pd.to_datetime(df[col], errors="coerce")
    if df[col].isna().all():
        st.error("All values in 'Date' became NaT after conversion. Please check your data format.")
        st.stop()
    return df

def _init_defaults(store_list, dept_list, region_list, min_date, max_date):
    if K_STORE not in st.session_state:
        st.session_state[K_STORE] = store_list[0]
    if K_DEPT not in st.session_state:
        st.session_state[K_DEPT] = dept_list[0]
    if K_REGION not in st.session_state:
        st.session_state[K_REGION] = region_list[0]
    if K_HOLIDAYS not in st.session_state:
        st.session_state[K_HOLIDAYS] = False
    if K_START not in st.session_state:
        st.session_state[K_START] = min_date.date()
    if K_END not in st.session_state:
        st.session_state[K_END] = max_date.date()

def _reset_to_defaults(store_list, dept_list, region_list, min_date, max_date):
    st.session_state[K_STORE] = store_list[0]
    st.session_state[K_DEPT] = dept_list[0]
    st.session_state[K_REGION] = region_list[0]
    st.session_state[K_HOLIDAYS] = False
    st.session_state[K_START] = min_date.date()
    st.session_state[K_END] = max_date.date()
    st.rerun()

# ----------------- Public API -----------------
def sidebar_filters(df: pd.DataFrame) -> Filters:
    df = _coerce_date_column(df, "Date")

    # Build lists AS STRINGS so UI and filtering use the same type
    store_list  = ["All Stores"] + sorted(df["Store"].dropna().astype(str).unique().tolist()) if "Store" in df.columns else ["All Stores"]
    dept_list   = ["All Departments"] + sorted(df["Dept"].dropna().astype(str).unique().tolist()) if "Dept" in df.columns else ["All Departments"]
    region_list = ["All Regions"] + sorted(df["Type"].dropna().astype(str).unique().tolist()) if "Type" in df.columns else ["All Regions"]

    # Date bounds
    min_date: pd.Timestamp = pd.to_datetime(df["Date"].min()).normalize()
    max_date: pd.Timestamp = pd.to_datetime(df["Date"].max()).normalize()

    _init_defaults(store_list, dept_list, region_list, min_date, max_date)

    st.sidebar.markdown("### Filters")

    if st.sidebar.button("Reset filters", type="secondary", help="Restore all filters to default values"):
        _reset_to_defaults(store_list, dept_list, region_list, min_date, max_date)

    # indices from state
    store_idx = store_list.index(st.session_state[K_STORE]) if st.session_state[K_STORE] in store_list else 0
    dept_idx = dept_list.index(st.session_state[K_DEPT]) if st.session_state[K_DEPT] in dept_list else 0
    region_idx = region_list.index(st.session_state[K_REGION]) if st.session_state[K_REGION] in region_list else 0

    store = st.sidebar.selectbox("Store", store_list, index=store_idx, key=K_STORE)
    dept = st.sidebar.selectbox("Department", dept_list, index=dept_idx, key=K_DEPT)
    region = st.sidebar.selectbox("Region", region_list, index=region_idx, key=K_REGION)
    only_holidays = st.sidebar.checkbox("Only holiday weeks?", key=K_HOLIDAYS)

    st.sidebar.markdown("### Date Range")
    start_date_input = st.sidebar.date_input(
        "Start Date",
        min_value=min_date.date(),
        max_value=max_date.date(),
        format="YYYY-MM-DD",
        key=K_START,
        help="Select the first date to include."
    )
    end_date_input = st.sidebar.date_input(
        "End Date",
        min_value=min_date.date(),
        max_value=max_date.date(),
        format="YYYY-MM-DD",
        key=K_END,
        help="Select the last date to include."
    )

    start_ts = pd.to_datetime(start_date_input)
    end_ts = pd.to_datetime(end_date_input)
    if end_ts < start_ts:
        st.sidebar.error("End Date must be on or after Start Date.")
        st.stop()

    st.sidebar.caption(
        f"Showing **{store} / {dept} / {region}** from **{start_ts.date()}** to **{end_ts.date()}**."
    )

    return Filters(
        store=store, dept=dept, region=region,
        only_holidays=only_holidays,
        start_date=start_ts, end_date=end_ts,
    )

def apply_filters(df: pd.DataFrame, f: Filters) -> pd.DataFrame:
    df = _coerce_date_column(df, "Date")
    view = df.copy()

    # Compare as strings to avoid type mismatches
    if f.store != "All Stores" and "Store" in view.columns:
        view = view[view["Store"].astype(str) == str(f.store)]
    if f.dept != "All Departments" and "Dept" in view.columns:
        view = view[view["Dept"].astype(str) == str(f.dept)]
    if f.region != "All Regions" and "Type" in view.columns:
        view = view[view["Type"].astype(str) == str(f.region)]
    if f.only_holidays and "IsHoliday" in view.columns:
        view = view[view["IsHoliday"] == True]

    view = view[(view["Date"] >= f.start_date) & (view["Date"] <= f.end_date)]
    return view
