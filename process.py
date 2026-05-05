import streamlit as st
# from EVChoose import *
from streamlit_extras import dataframe_explorer
from streamlit_sortables import sort_items

st.write("Dashboard is working!")

criteria_names = [
    "Range",
    "Efficiency",
    "Acceleration",
    "Charging Time",
    "Seating Capacity",
    "Cargo Space"
]

original_items = [
    {'items': criteria_names}
]

def hitung_prioritas(sorted_items):
    #Perhitungan bobot berdasarkan prioritas
    bobot_prioritas = {}
    for idx, item in enumerate(sorted_items[0]['items']):
        nilai_max = len(sorted_items[0]['items']) - idx
        bobot_prioritas[item] = 0
        for i in range(1, nilai_max + 1):
            bobot_prioritas[item] += i / sum(range(1, len(sorted_items[0]['items']) + 1))
    
    return bobot_prioritas

simple_style = """
.sortable-component {
    background-color:rgb(0, 225, 255);
    font-size: 8px;
    counter-reset: item;
}
.sortable-item {
    background-color: rgb(22, 41, 102);
    color: white;
}
"""

with st.form(key="priorities_form", enter_to_submit=True):
    st.write("Urutkan bobot prioritas: ")


    sorted_items = sort_items(original_items, 
                              multi_containers=True, 
                              custom_style=simple_style
                              )


    save_clicked = st.form_submit_button(label="Simpan")

if save_clicked:
    df_prioritas = hitung_prioritas(sorted_items)
    st.write(f"Bobot prioritas: {df_prioritas}")
    st.success("Bobot prioritas telah disimpan.")

# Proses SCPK


# Visualisasi Matplotlib
