# auto_insights.py — LLM-only (no silent fallback, no debug buffer)
from __future__ import annotations
import os, json
import pandas as pd

# --- OpenAI client (new SDK) -------------------------------------------------
from openai import OpenAI

def _get_client() -> OpenAI:
    raw_key = os.getenv("OPENAI_API_KEY", "")
    api_key = raw_key.strip().strip('"').strip("'")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set.")
    return OpenAI(api_key=api_key)

def is_llm_active() -> bool:
    """True only if a key is present. (Doesn't call the API.)"""
    raw_key = os.getenv("OPENAI_API_KEY", "")
    return bool(raw_key.strip().strip('"').strip("'"))

# -----------------------------------------------------------------------------

PII_LIKE_COLS = {"customer", "email", "phone", "address", "name", "ssn", "dob"}

def _redact_pii_columns(df: pd.DataFrame) -> pd.DataFrame:
    keep = [c for c in df.columns if not any(tok in c.lower() for tok in PII_LIKE_COLS)]
    return df[keep]

def _basic_profile(view: pd.DataFrame) -> dict:
    if view is None or view.empty:
        return {"empty": True}

    weekly = view.groupby("Date", dropna=True)["Sales"].sum().sort_index()
    total = float(weekly.sum())
    weeks = int(weekly.size)
    avg = float(weekly.mean()) if weeks else 0.0
    std = float(weekly.std(ddof=0)) if weeks > 1 else 0.0
    best_date = weekly.idxmax() if weeks else None
    best_val = float(weekly.max()) if weeks else 0.0

    by_dept = view.groupby("Dept")["Sales"].sum().sort_values(ascending=False).head(10)
    by_store = view.groupby("Store")["Sales"].sum().sort_values(ascending=False).head(10)
    by_region = (
        view.groupby("Type")["Sales"].sum().sort_values(ascending=False).head(10)
        if "Type" in view.columns else pd.Series(dtype=float)
    )

    anomalies = []
    if weeks > 3 and std > 0:
        z = (weekly - weekly.mean()) / std
        spikes = z[z.abs() >= 2.0]
        for d, zval in spikes.items():
            anomalies.append({"date": str(d.date()), "z": float(zval), "sales": float(weekly.loc[d])})

    return {
        "empty": False,
        "kpis": {
            "total_sales": total,
            "weeks": weeks,
            "avg_per_week": avg,
            "std_per_week": std,
            "best_week": {"date": str(best_date.date()) if best_date is not None else None, "value": best_val},
        },
        "top_departments": by_dept.reset_index().to_dict(orient="records"),
        "top_stores": by_store.reset_index().to_dict(orient="records"),
        "top_regions": by_region.reset_index().to_dict(orient="records") if len(by_region) else [],
        "anomalies": anomalies,
    }

def _trim_for_tokens(obj: dict, max_chars: int = 8000) -> str:
    s = json.dumps(obj, ensure_ascii=False)
    if len(s) <= max_chars:
        return s
    slim = {
        "kpis": obj.get("kpis", {}),
        "top_departments": obj.get("top_departments", [])[:5],
        "top_stores": obj.get("top_stores", [])[:5],
        "top_regions": obj.get("top_regions", [])[:5],
        "anomalies": obj.get("anomalies", [])[:5],
    }
    return json.dumps(slim, ensure_ascii=False)

_INSIGHTS_SYSTEM_PROMPT = (
    "You are a senior retail analytics copilot. "
    "Given summary stats (JSON) for weekly sales, write concise, plain-English insights.\n"
    "Rules:\n"
    "- Lead with the most important 3–5 findings.\n"
    "- Explain likely drivers (holidays, promos, store type, weather if present).\n"
    "- Call out anomalies/outliers and suggest quick actions.\n"
    "- Keep it under ~180 words. Use bullet points.\n"
)

def _build_user_prompt(summary_json: str, user_question: str | None) -> str:
    q = (user_question or "").strip()
    return (
        f"DATA SUMMARY JSON:\n{summary_json}\n\n"
        f"USER QUESTION (optional): {q if q else 'N/A'}\n\n"
        "Now produce actionable insights."
    )

def get_llm_insights(view: pd.DataFrame, user_question: str | None = None) -> str:
    """
    Returns markdown insights produced by the LLM.
    - No heuristic fallback.
    - Raises RuntimeError with a clear message on any failure.
    """
    if view is None or view.empty:
        raise RuntimeError("No data available for the current filters.")

    client = _get_client()  # may raise if key missing

    # build compact, privacy-aware payload
    safe = _redact_pii_columns(view.copy())
    keep = [c for c in safe.columns if c in {
        "Date", "Sales", "Dept", "Store", "Type", "IsHoliday",
        "Temperature", "Fuel_Price", "CPI", "Unemployment"
    }]
    slim = safe[keep].copy()

    summary = _basic_profile(slim)
    if summary.get("empty"):
        raise RuntimeError("No data available for the current filters.")

    summary_json = _trim_for_tokens(summary)

    try:
        resp = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": _INSIGHTS_SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(summary_json, user_question)},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        # Bubble up as a RuntimeError so the UI can render st.error()
        raise RuntimeError(f"LLM call failed: {e}") from e
