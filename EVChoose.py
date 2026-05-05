# Import Library yang diperlukan
import pandas as pd
import numpy as np
import streamlit as st

# Function
def weightNormalization(w):
    w = np.array(w)
    return w / np.sum(w)

criteriaColumns = [
    'range_km', #Benefit
    'efficiency_wh_per_km', #Cost
    'acceleration_0_100_s', #Cost
    'fast_charging_power_kw_dc', #Benefit
    'seats', #Cost
    'cargo_volume_l' #Benefit
]

# Ekstrak Dataset
dataFrame = pd.read_csv("default_ev_spec_dataset.csv")

newDataFrame = dataFrame[['brand', 'model', 'range_km', 'efficiency_wh_per_km', 'acceleration_0_100_s', 'fast_charging_power_kw_dc', 'seats', 'cargo_volume_l']]

newDataFrame.to_csv("clean_ev_spec_dataset.csv", index=False)

data = pd.read_csv('clean_ev_spec_dataset.csv')
print("Jumlah data sebelum cleaning:", len(data))

dataNumeric = data[criteriaColumns].apply(pd.to_numeric, errors='coerce')

dataCleaned = data[dataNumeric.notna().all(axis=1)].copy()
dataCleaned[criteriaColumns] = dataNumeric[dataNumeric.notna().all(axis=1)]

dataCleaned = dataCleaned[(dataCleaned[criteriaColumns] != 0).all(axis=1)]

print("Jumlah data setelah cleaning:", len(dataCleaned))


dataFrame = dataCleaned[['brand', 'model'] + criteriaColumns].reset_index(drop=True)

def hitung_prioritas(sorted_items):
    bobot_prioritas = {}
    # Normalisasi Bobot
    criteriaWeight = np.array([1/6] * 6)
    # print(criteriaWeight)

    normalizeWeight = weightNormalization(criteriaWeight)
    normalizeWeight[[1, 2]] *= -1 #Normalisasi bobot untuk cost

    return normalizeWeight


# Hitung nilai S
def hitung_S_V(dataFrame, criteriaColumns, normalizeWeight):
    S = []

    for i in range(len(dataFrame)):
        nilai = 1
        for j, col in enumerate(criteriaColumns):
            nilai *= dataFrame.loc[i, col] ** normalizeWeight[j]
        S.append(nilai)

    dataFrame["S"] = S

    total_S = dataFrame['S'].sum()
    dataFrame['V'] = dataFrame['S'] / total_S

    # Hitung Nilai V (preferensi)
    return dataFrame['S'], dataFrame['V']



def ranking(dataFrame):
# Perankingan
    dataFrame['Rank'] = dataFrame['V'].rank(ascending=False)

    dataFrameFinal = dataFrame.sort_values('V', ascending=False).reset_index(drop=True)

    return dataFrameFinal.head()