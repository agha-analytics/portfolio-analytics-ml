# project1_sales_dashboard/launch.py
import streamlit as st, traceback

try:
    import app as application  # imports project1_sales_dashboard/app.py as a module
except Exception:
    st.title("Import error in app.py")
    st.code("".join(traceback.format_exc()))
else:
    try:
        application.main()
    except Exception:
        st.title("Runtime error while running main()")
        st.code("".join(traceback.format_exc()))
