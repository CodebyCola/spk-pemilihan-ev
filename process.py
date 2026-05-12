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
df_filtered = df.copy()
if selected_brands:
    df_filtered = df_filtered[df_filtered["brand"].isin(selected_brands)]

filtered_df = dataframe_explorer(df_filtered, case=False)

with st.form(key="priorities_form", enter_to_submit=True):

    st.write("Urutkan bobot prioritas: ")

    sorted_items = sort_items(original_items, 
                              multi_containers=True, 
                              custom_style=simple_style
                              )


    save_clicked = st.form_submit_button(label="Simpan")

# Proses SCPK
if save_clicked:
    df_prioritas = hitung_prioritas(sorted_items)
    bobot_series = df_prioritas.set_index("Kriteria")["Bobot"]

    # raw_weights = [abs(df_prioritas[label]) for label in criteriaLabels]
    # normalizeWeight = weightNormalization(raw_weights)

    # for idx, label in enumerate(criteriaLabels):
    #     if label in cost_criteria:
    #         df_prioritas[label] *= -1

    bobot_display = {
        row["Kriteria"]: f"{row["Bobot"] * 100:.2f}%"
    for _, row in df_prioritas.iterrows()
    }

    bobot_df = pd.DataFrame(list(bobot_display.items()), columns=['Kriteria', 'Bobot'])
    with st.expander("Lihat bobot"):
        st.table(bobot_df)

    weights = [bobot_series[label] for label in criteriaLabels]
    final_df = filtered_df[["brand", "model"] + criteriaColumns.copy()]
    
    final_df["S"] = computeSValue(final_df, criteriaColumns, weights)
    with st.expander("Lihat nilai S"):
        st.dataframe(final_df[["brand", "model", "S"]].sort_values("S", ascending=False).reset_index(drop=True))
    final_df["V"] = computeVValue(final_df)
    with st.expander("Lihat nilai V"):
        st.dataframe(final_df[["brand", "model", "V"]].sort_values("V", ascending=False).reset_index(drop=True))
    
    finalRank = computeRank(final_df)
    st.dataframe(finalRank.head())
    st.toast("Bobot prioritas telah disimpan.")

# Visualisasi Matplotlib
