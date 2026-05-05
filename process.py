import streamlit as st
import pandas as pd
import numpy as np
from EVChoose import (
    criteriaLabels,
    criteriaColumns,
    cost_criteria,
    prepare_data,
    weightNormalization,
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
    font-size: 8px;
    counter-reset: item;
}
.sortable-item {
    background-color: black;
    color: white;
}
"""

with st.form(key="priorities_form", enter_to_submit=True):
    st.write("Urutkan bobot prioritas: ")

    sorted_items = sort_items(original_items, 
                              multi_containers=True, 
                              custom_style=simple_style
                              )

    # st.write(f"Bobot prioritas saat ini: {sorted_items[0]['items']}")

    save_clicked = st.form_submit_button(label="Simpan")

if save_clicked:
    df_prioritas = hitung_prioritas(sorted_items)

    raw_weights = [abs(df_prioritas[label]) for label in criteriaLabels]
    normalizeWeight = weightNormalization(raw_weights)

    for idx, label in enumerate(criteriaLabels):
        if label in cost_criteria:
            normalizeWeight[idx] *= -1

    df["S"] = computeSValue(df, criteriaColumns, normalizeWeight)
    df["V"] = computeVValue(df)
    finalRank = computeRank(df)

    # bobot_display = {item: f"{bobot * 100:.2f}%" for item, bobot in df_prioritas.items()}
    # st.write(f"Bobot prioritas: {bobot_display}")
    st.write(finalRank.head())
    st.toast("Bobot prioritas telah disimpan.")

# Proses SCPK


# Visualisasi Matplotlib
