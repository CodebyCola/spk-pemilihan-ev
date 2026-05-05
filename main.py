# Import Library yang diperlukan
import pandas as pd
import numpy as np
# import streamlit as st

# Function
def weightNormalization(w):
    w = np.array(w)
    return w / np.sum(w)

# Hitung nilai S
def computeSValue(dataFrame) :
    S = []

    for i in range(len(dataFrame)):
        nilai = 1
        for j, col in enumerate(criteriaColumns):
            nilai *= dataFrame.loc[i, col] ** normalizeWeight[j]
        S.append(nilai)
    
    return S

# Hitung Nilai V (preferensi)
def computeVValue(dataFrame):
    total_S = dataFrame['S'].sum()
    valueV = dataFrame['S'] / total_S
    return valueV
        
# Perankingan
def computeRank(dataFrame):
    dataFrame['Rank'] = dataFrame['V'].rank(ascending=False)
    dataFrameFinal = dataFrame.sort_values('V', ascending=False).reset_index(drop=True)
    
    return dataFrameFinal

# Data Cleaning
data = pd.read_csv('clean_ev_spec_dataset.csv')
print("Jumlah data sebelum cleaning:", len(data))

criteriaColumns = [
    'range_km', #Benefit
    'efficiency_wh_per_km', #Cost
    'acceleration_0_100_s', #Cost
    'fast_charging_power_kw_dc', #Benefit
    'seats', #Cost
    'cargo_volume_l' #Benefit
]


dataNumeric = data[criteriaColumns].apply(pd.to_numeric, errors='coerce')

dataCleaned = data[dataNumeric.notna().all(axis=1)].copy()
dataCleaned[criteriaColumns] = dataNumeric[dataNumeric.notna().all(axis=1)]

dataCleaned = dataCleaned[(dataCleaned[criteriaColumns] != 0).all(axis=1)]

print("Jumlah data setelah cleaning:", len(dataCleaned))

dataFrame = dataCleaned[['brand', 'model'] + criteriaColumns].reset_index(drop=True)

# Normalisasi Bobot
criteriaWeight = np.array([1/6] * 6)
normalizeWeight = weightNormalization(criteriaWeight)
normalizeWeight[[1, 2]] *= -1 #Normalisasi bobot untuk cost

dataFrame["S"] = computeSValue(dataFrame)
print("Nilai S dalam dataframe: ", dataFrame['S'].head())

dataFrame['V'] = computeVValue(dataFrame)
print("Nilai V dalam dataframe: ", dataFrame['V'].head())

finalRank = computeRank(dataFrame)
print(finalRank.head())
