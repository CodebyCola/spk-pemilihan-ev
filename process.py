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

def data_prioritas(normalizeWeight):
    data = {
        'Kriteria': criteriaLabels,
        'Bobot': normalizeWeight
    }
    return pd.DataFrame(data)

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

df_filter_brand = df_filter_brand.reset_index(drop=True)
df_numeric_only = df_filter_brand.select_dtypes(include=['number'])

df_filter_numeric = dataframe_explorer(df_numeric_only, case=False)

filtered_df =  df_filter_brand.loc[df_filter_numeric.index]


with st.form(key="priorities_form", enter_to_submit=True):

    st.write("Urutkan bobot prioritas: ")

    sorted_items = sort_items(original_items, multi_containers=True, custom_style=simple_style)

    run_clicked = st.form_submit_button(label="Jalankan Proses SPK")

# Proses SCPK
if run_clicked:
    df_prioritas = hitung_prioritas(sorted_items)
    bobot_series = df_prioritas.set_index("Kriteria")["Bobot"]
    weights = [bobot_series[label] for label in criteriaLabels]
    final_df = filtered_df[["brand", "model"] + criteriaColumns.copy()]
    
    bobot_display = {
        row["Kriteria"]: f"{row['Bobot'] * 100:.2f}%"
    for _, row in df_prioritas.iterrows()
    }

    # Visualisasi Matplotlib
    # visualisasi bobot
    bobot_df = pd.DataFrame(list(bobot_display.items()), columns=['Kriteria', 'Bobot'])
    with st.expander("Lihat bobot"):
        st.table(bobot_df)
        fig, ax = plt.subplots(figsize=(8, 4))
        bobot_df_grafik = df_prioritas['Bobot'].abs() * 100
        bars = ax.bar(bobot_df["Kriteria"],
                      bobot_df_grafik,
                      color="#FF4B4B")
        
        
        ax.bar_label(bars,fmt='%.1f%%',
                     padding=3,
                     label_type='center',
                     color='white')
        
        ax.set_title("Bobot Prioritas Kriteria")
        ax.set_ylabel("Persentase (%)")

        apply_dark_theme(ax, fig)
        st.pyplot(fig)
        
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
            
            
        # visualisasi tabel nilai v
        final_df["V"] = computeVValue(final_df)
        with st.expander("Lihat nilai V"):
            dataframe_v_value = final_df[["brand", "model", "V"]].sort_values("V", ascending=False).reset_index(drop=True)
            dataframe_v_value = dataframe_v_value.set_index("brand")
            st.dataframe(dataframe_v_value)
        
        # Perankingan
        finalRank = computeRank(final_df)
        ranking_chart = finalRank.head(10)
        finalRank = finalRank.set_index(["brand", "model"])
        st.dataframe(finalRank.head(10))
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
        
