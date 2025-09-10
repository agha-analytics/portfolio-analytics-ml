import traceback
import streamlit as st

st.set_page_config(page_title="Sales Dashboard", layout="wide")

try:
    # import only when needed so import-time errors are caught
    import app as sales_app

    # put heavy work behind a function (if your app has `main()`, call that)
    if hasattr(sales_app, "main"):
        sales_app.main()
    else:
        # last-resort: run the module's top-level code
        # (import already executed above)
        pass

except Exception:
    st.error("The app crashed while starting. Full traceback below:")
    st.code(traceback.format_exc())
