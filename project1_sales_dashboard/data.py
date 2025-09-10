# data.py  — drop-in replacement
from pathlib import Path
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).parent / "data"

@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    # --- Read source CSVs (robust for mixed dtypes) ---
    sales = pd.read_csv(
        DATA_DIR / "sales.csv",
        low_memory=False,
    )
    features = pd.read_csv(
        DATA_DIR / "features.csv",
        low_memory=False,
    )
    stores = pd.read_csv(
        DATA_DIR / "stores.csv",
        low_memory=False,
    )

    # --- Normalize column names (spaces -> underscores) ---
    for df in (sales, features, stores):
        df.columns = [c.strip().replace(" ", "_") for c in df.columns]

    # --- Parse dates (day-first like your app) ---
    sales["Date"] = pd.to_datetime(sales["Date"], errors="coerce", dayfirst=True)
    features["Date"] = pd.to_datetime(features["Date"], errors="coerce", dayfirst=True)

    # --- Optional: common dtypes (helps memory & joins) ---
    for col in ("Store", "Dept"):
        if col in sales.columns:
            sales[col] = pd.to_numeric(sales[col], errors="coerce").astype("Int64")
        if col in features.columns:
            features[col] = pd.to_numeric(features[col], errors="coerce").astype("Int64")
        if col in stores.columns:
            stores[col] = pd.to_numeric(stores[col], errors="coerce").astype("Int64")

    # --- Merge datasets; rename Weekly_Sales -> Sales if present ---
    if "Weekly_Sales" in sales.columns and "Sales" not in sales.columns:
        sales = sales.rename(columns={"Weekly_Sales": "Sales"})

    base = (
        sales.merge(features, on=["Store", "Date"], how="left")
             .merge(stores, on="Store", how="left")
    )

    # --- Coalesce any IsHoliday* columns into a single boolean IsHoliday ---
    holiday_cols = [c for c in base.columns if c.lower().startswith("isholiday")]
    if holiday_cols:
        tmp = base[holiday_cols].apply(
            lambda col: col.astype(str).str.strip().str.lower().isin(["1", "true", "t", "yes"])
        )
        base["IsHoliday"] = tmp.any(axis=1)
        drop_cols = [c for c in holiday_cols if c != "IsHoliday"]
        base = base.drop(columns=drop_cols, errors="ignore")
    else:
        base["IsHoliday"] = False

    # --- Light memory optimization on string columns used for groupby/filters ---
    for cat_col in ("Type", "Department", "Region", "Store_Type"):
        if cat_col in base.columns:
            base[cat_col] = base[cat_col].astype("category")

    # --- Keep rows with valid dates and sort ---
    base = base.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)

    return base
