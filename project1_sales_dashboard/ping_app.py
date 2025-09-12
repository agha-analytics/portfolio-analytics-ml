# project1_sales_dashboard/ping_app.py
import streamlit as st
st.set_page_config(page_title="Ping", layout="centered")

st.title("✅ Cloud smoke test")
st.write("If you can see this, the infra is fine and the crash is in the real app code.")

# keep the process alive for a while so the health check passes
st.write("App is running. Timestamp (server):")
import datetime as _dt
st.code(str(_dt.datetime.utcnow()) + "Z")
