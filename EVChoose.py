# Import Library yang diperlukan
import pandas as pd
import numpy as np

criteria_map = [
    ("Range", "range_km"),
    ("Efficiency", "efficiency_wh_per_km"),
    ("Acceleration", "acceleration_0_100_s"),
    ("Charging Time", "fast_charging_power_kw_dc"),
    ("Seats", "seats"),
    ("Cargo Space", "cargo_volume_l"),
]

cost_criteria = {"Efficiency", "Acceleration"}
criteriaLabels = [label for label, _ in criteria_map] #ambil criteria_map [(0, _)]
criteriaColumns = [column for _, column in criteria_map] #ambil criteria_map [(_, 0)]
criteriaDisplayMap = {column: label for label, column in criteria_map}

def hitung_prioritas(sorted_items, cost_criteria_set=None):
    #Perhitungan bobot berdasarkan prioritas
    items = sorted_items[0]['items']
    total_bobot = sum(range(1, len(items) + 1))
    bobot_prioritas = []
    active_cost_criteria = cost_criteria if cost_criteria_set is None else set(cost_criteria_set)

    for idx, item in enumerate(items):
        nilai_prioritas = len(items) - idx
        bobot = nilai_prioritas / total_bobot

        if item in active_cost_criteria:
            bobot *= -1

        bobot_prioritas.append({
            "Kriteria": item,
            "Bobot": bobot
        })

    return pd.DataFrame(bobot_prioritas)

# Hitung nilai S
def computeSValue(dataFrame, criteriaColumns, normalizeWeight):
    S = []

    for i in range(len(dataFrame)):
        nilai = 1
        for j, col in enumerate(criteriaColumns):
            nilai *= dataFrame.iloc[i][col] ** normalizeWeight[j]
        S.append(nilai)
    
    return pd.Series(S, name='S')

# Hitung Nilai V (preferensi)
def computeVValue(dataFrame):
    total_S = dataFrame['S'].sum()
    if total_S == 0:
        raise ValueError("Total nilai S tidak boleh 0")
    valueV = dataFrame['S'] / total_S
    return pd.Series(valueV, name='V')
        
# Perankingan
def computeRank(dataFrame):
    dataFrame['Rank'] = dataFrame['V'].rank(ascending=False)
    dataFrameFinal = dataFrame.sort_values('V', ascending=False).reset_index(drop=True)
    
    return pd.DataFrame(dataFrameFinal)


def prepare_data(clean_csv='clean_ev_spec_dataset.csv'):
    """Load and clean dataset, return dataframe ready for scoring.

    Returns a dataframe with columns ['brand','model'] + criteriaColumns.
    """
    data = pd.read_csv(clean_csv)

    criteriaColumns = [
        'range_km', #Benefit
        'efficiency_wh_per_km', #Cost
        'acceleration_0_100_s', #Cost
        'fast_charging_power_kw_dc', #Benefit
        'seats', #Benefit
        'cargo_volume_l' #Benefit
    ]

#  Clean data
    dataNumeric = data[criteriaColumns].apply(pd.to_numeric, errors='coerce')

    dataCleaned = data[dataNumeric.notna().all(axis=1)].copy()
    dataCleaned[criteriaColumns] = dataNumeric[dataNumeric.notna().all(axis=1)]

    dataCleaned = dataCleaned[(dataCleaned[criteriaColumns] != 0).all(axis=1)]

    dataFrame = dataCleaned[['brand', 'model'] + criteriaColumns].reset_index(drop=True)
    return dataFrame, criteriaColumns