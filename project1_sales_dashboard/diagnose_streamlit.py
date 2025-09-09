import streamlit as st
import sys
import os
import pathlib
import traceback
import pandas as pd

st.title('🔎 Streamlit Cloud Diagnostic')
st.write('Python:', sys.version)
st.write('CWD:', os.getcwd())

repo_root = pathlib.Path(__file__).resolve().parents[1]
app_dir   = pathlib.Path(__file__).resolve().parent
data_dir  = app_dir / 'data'

st.subheader('Folders')
st.write('Repo root:', repo_root)
st.write('App dir:', app_dir)
st.write('Data dir:', data_dir)

st.subheader('Dir listing (app dir)')
st.code('\n'.join(sorted(p.name for p in app_dir.iterdir())))

if data_dir.exists():
    st.subheader('Dir listing (data dir)')
    st.code('\n'.join(sorted(p.name for p in data_dir.iterdir())))
else:
    st.error('❌ data/ folder not found next to app.')

def try_read(name):
    p = data_dir / name
    st.write(f'Trying to read: {p}')
    try:
        df = pd.read_csv(p)
        st.success(f'✅ Loaded {name} — shape={df.shape}')
        st.dataframe(df.head(3))
    except Exception as e:
        st.error(f'❌ Failed to read {name}: {type(e).__name__}: {e}')
        st.code(traceback.format_exc())

st.subheader('CSV read checks')
for fname in ['sales.csv','stores.csv','features.csv',
              'sales data-set.csv','stores data-set.csv','Features data set.csv']:
    try_read(fname)
