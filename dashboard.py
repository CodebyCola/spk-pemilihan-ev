import streamlit as st
import pandas as pd
from EVChoose import prepare_data
from EVChoose import criteriaDisplayMap
st.header("Sistem Cerdas Pemilihan Kendaraan Listrik")
st.write("Sistem Pendukung Keputusan (SPK) ini digunakan untuk membantu pengguna " 
        "dalam memilih kendaraan listrik (EV) terbaik dari beberapa alternatif " \
        "yang tersedia.")

data_raw = pd.read_csv('clean_ev_spec_dataset.csv')
df_unfiltered = prepare_data()[0]

st.subheader("Data Quality Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.metric(label="📊 Total Data Asli", value=f"{len(data_raw)} Baris")
        st.caption("Jumlah total data yang diunggah ke sistem.")

with col2:
    with st.container(border=True):
        st.metric(label="✅ Data Bersih", value=f"{len(df_unfiltered)} Baris")
        st.caption("Data siap proses (Nilai kriteria > 0).")

with col3:
    with st.container(border=True):
        jumlah_cacat = len(data_raw) - len(df_unfiltered)
        st.metric(label="⚠️ Data Cacat (Nilai 0)", value=f"{jumlah_cacat} Baris")
        st.caption("Data otomatis dieliminasi dari perhitungan WP.")

st.divider()

st.subheader("Galeri Eksplorasi Data Mentah")
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
st.dataframe(df_show.rename(columns=criteriaDisplayMap), width="stretch")
