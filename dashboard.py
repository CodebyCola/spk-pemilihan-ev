import streamlit as st
import pandas as pd
from EVChoose import prepare_data
st.header("Sistem Cerdas Pemilihan Kendaraan Listrik")

df_unfiltered = prepare_data()[0]

filter_user = st.multiselect(
    "Pilih brand yang ingin ditampilkan:",
    options=df_unfiltered["brand"].unique(),
    default=[],
    key="brand_filter",
)

df_show = df_unfiltered.copy()

if filter_user:
    df_show = df_unfiltered[df_unfiltered["brand"].isin(filter_user)]

st.write(f"Menampilkan {len(df_show)} data:")
st.dataframe(df_show, width="stretch")
