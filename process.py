import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from streamlit_extras.dataframe_explorer import dataframe_explorer
from EVChoose import (
    criteriaLabels,
    criteriaColumns,
    cost_criteria,
    prepare_data,
    computeSValue,
    computeVValue,
    computeRank,
    hitung_prioritas,
)
from streamlit_sortables import sort_items


df, criteriaColumns = prepare_data()

original_items = [
    {'items': criteriaLabels}
]

# Helper: normalisasi bobot dari input slider sama input manual
def _manual_to_prioritas_df(raw: dict) -> pd.DataFrame:
    total = sum(raw.values()) or 1
    rows = []
    for label in criteriaLabels:
        w = raw[label] / total
        if label in cost_criteria:
            w *= -1
        rows.append({"Kriteria": label, "Bobot": w})
    return pd.DataFrame(rows)

def apply_dark_theme(ax, fig):
    fig.patch.set_facecolor("#0E1117")
    ax.set_facecolor("#0E1117")

    ax.tick_params(colors="white")

    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")

    ax.title.set_color("white")

    for spine in ax.spines.values():
        spine.set_color("white")

    ax.grid(color="gray", linestyle="--", linewidth=0.5, alpha=0.3)


simple_style = """
.sortable-component {
    background-color: black;
    font-size: 16px;
    counter-reset: item;
}
.sortable-item {
    background-color: black;
    color: white;
}
"""

df['brand'] = df['brand'].astype(str)

brand_options = sorted(df["brand"].dropna().unique())

selected_brands = st.multiselect(
    "Filter brand",
    options=brand_options,
    default=[]
)
df_filter_brand= df.copy()

if selected_brands:
    df_filter_brand = df_filter_brand[df_filter_brand["brand"].isin(selected_brands)]

df_filter_brand = df_filter_brand.reset_index(drop=True) # reset index agar balik semua ke 0..1.. dst 

df_numeric_only = df_filter_brand.select_dtypes(include=['number']) # memilih kolom yang berisi numeric saja sehingga kolom brand & model (string) tidak masuk ke explorer

df_filter_numeric = dataframe_explorer(df_numeric_only, case=False) # memfilter rentang min max ranges pada input data frame on untuk setiap kolom numerik

mask = df_filter_brand.index.isin(df_filter_numeric.index) # menambahkan kembali index brand dan model yang sebelumnya difilter
filtered_df = df_filter_brand[mask].reset_index(drop=True)
 
 # Pilih metode input bobot
input_method = st.selectbox(
    "Pilih metode input bobot:",
    options=["Drag & Drop Prioritas", "Slider", "Number Input"],
    help="Pilih cara Anda ingin menentukan bobot kriteria"
)
 
with st.form(key="priorities_form", enter_to_submit=True):
    
 
    st.write("Atur bobot prioritas kriteria:")
 
    # Input method 1: Drag & Drop
    if input_method == "Drag & Drop Prioritas":
        st.caption("Seret kriteria untuk mengurutkan prioritas (atas = prioritas tertinggi).")
        sorted_items = sort_items(original_items, multi_containers=True, custom_style=simple_style)
        slider_weights  = None
        number_weights  = None
 
    # Input method 2: Slider
    elif input_method == "Slider":
        st.caption("Geser slider untuk menentukan bobot tiap kriteria (0–100). Bobot akan dinormalisasi otomatis.")
        slider_weights = {}
        cols = st.columns(2)
        for i, label in enumerate(criteriaLabels):
            with cols[i % 2]:
                slider_weights[label] = st.slider(
                    label,
                    min_value=0,
                    max_value=100,
                    value=50,
                    step=1,
                    key=f"slider_{label}"
                )
        sorted_items   = None
        number_weights = None
 
    # Input method 3: Number Input
    else:
        st.caption("Masukkan bobot untuk tiap kriteria (0.0–1.0). Bobot akan dinormalisasi otomatis.")
        number_weights = {}
        cols = st.columns(2)
        for i, label in enumerate(criteriaLabels):
            with cols[i % 2]:
                number_weights[label] = st.number_input(
                    label,
                    min_value=0.0,
                    max_value=1.0,
                    value=round(1 / len(criteriaLabels), 2),
                    step=0.05,
                    format="%.2f",
                    key=f"num_{label}"
                )
        sorted_items  = None
        slider_weights = None
 
    run_clicked = st.form_submit_button(label="Jalankan Proses SPK")

# Proses SCPK
if run_clicked:
    # cek input if valid -> run perhitungan
    if input_method == "Drag & Drop Prioritas":
        if sorted_items is None:
            st.error("Gagal membaca urutan prioritas. Silakan coba lagi.")
            st.stop()
        df_prioritas = hitung_prioritas(sorted_items)
        
    elif input_method == "Slider":
        if slider_weights is None or sum(slider_weights.values()) == 0:
            st.error("Semua bobot slider bernilai 0. Sesuaikan minimal satu slider.")
            st.stop()
        df_prioritas = _manual_to_prioritas_df(slider_weights)
        
    else:
        if number_weights is None or sum(number_weights.values()) == 0:
            st.error("Semua bobot bernilai 0. Masukkan setidaknya satu bobot.")
            st.stop()
        df_prioritas = _manual_to_prioritas_df(number_weights)
        
    
    bobot_series = df_prioritas.set_index("Kriteria")["Bobot"]
    weights = [bobot_series[label] for label in criteriaLabels]
    final_df = filtered_df[["brand", "model"] + criteriaColumns.copy()]
    
    bobot_display = {
        row["Kriteria"]: f"{abs(row['Bobot']) * 100:.2f}%"
    for _, row in df_prioritas.iterrows()
    }

    # Visualisasi Matplotlib
    # visualisasi bobot
    bobot_df = pd.DataFrame(list(bobot_display.items()), columns=['Kriteria', 'Bobot'])
    with st.expander("Lihat bobot"):
        st.table(bobot_df)
        fig, ax = plt.subplots(figsize=(8, 4))
        
        bobot_abs = df_prioritas['Bobot'].abs() * 100
        bars = ax.bar(df_prioritas["Kriteria"], bobot_abs, color="#FF4B4B")
        ax.bar_label(bars, fmt='%.1f%%', padding=3, label_type='center', color='white')
        
        ax.set_title("Bobot Prioritas Kriteria")
        ax.set_ylabel("Persentase (%)")

        apply_dark_theme(ax, fig)
        st.pyplot(fig)
        plt.close(fig)
        
    if final_df.empty:
        st.warning("Tidak ada data yang memenuhi kriteria filter.")
    else:
        final_df = final_df.reset_index(drop=True)
        final_df["S"] = computeSValue(final_df, criteriaColumns, weights) #hitung nilai s
        
        # visualisasi tabel nilai s
        with st.expander("Lihat nilai S"):
            dataframe_s_value = final_df[["brand", "model", "S"]].sort_values("S", ascending=False).reset_index(drop=True)
            dataframe_s_value = dataframe_s_value.set_index("brand")
            st.dataframe(dataframe_s_value)
            top_s = (final_df[["model", "S"]].sort_values("S", ascending=False).head(10))

            fig, ax = plt.subplots(figsize=(8, 5))

            ax.plot(top_s["model"],top_s["S"],marker="o",linewidth=2,color="#FF4B4B")

            ax.set_title("Perbandingan Top 10 Nilai S")
            ax.set_xlabel("Model EV")
            ax.set_ylabel("Nilai S")

            plt.xticks(rotation=30)

            apply_dark_theme(ax, fig)

            st.pyplot(fig)
            plt.close(fig)
            
        # visualisasi tabel nilai v
        final_df["V"] = computeVValue(final_df)
        with st.expander("Lihat nilai V"):
            dataframe_v_value = final_df[["brand", "model", "V"]].sort_values("V", ascending=False).reset_index(drop=True)
            dataframe_v_value = dataframe_v_value.set_index("brand")
            st.dataframe(dataframe_v_value)
        
        # Perankingan
        finalRank = computeRank(final_df)
        ranking_chart = finalRank.head(10)
        st.dataframe(
            finalRank
            .head(10)
            .astype({"Rank": int})
            .set_index("Rank")
        )
        st.toast("Bobot prioritas telah disimpan.")
        
        # Grafik untuk ranking 
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.barh(ranking_chart["model"],ranking_chart["V"],color="#3B82F6")
        ax.bar_label(
                    bars,
                    fmt='%.4f',
                    padding=5,
                    label_type='center',
                    color='white')
        
        ax.set_title("Top 10 Ranking EV")
        ax.set_xlabel("Nilai V")
        ax.invert_yaxis()
        
        apply_dark_theme(ax, fig)
        
        st.pyplot(fig)
        plt.close(fig)
        
