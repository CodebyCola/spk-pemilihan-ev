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
criteriaLabels = [label for label, _ in criteria_map]
criteriaColumns = [column for _, column in criteria_map]

# Function
def weightNormalization(w):
    w = np.array(w)
    return w / np.sum(w)

def hitung_prioritas(sorted_items):
    #Perhitungan bobot berdasarkan prioritas
    items = sorted_items[0]['items']
    total_bobot = sum(range(1, len(items) + 1))
    bobot_prioritas = {}

    for idx, item in enumerate(items):
        nilai_prioritas = len(items) - idx
        bobot = nilai_prioritas / total_bobot

        if item in cost_criteria:
            bobot *= -1

        bobot_prioritas[item] = bobot

    return bobot_prioritas

# Hitung nilai S
def computeSValue(dataFrame, criteriaColumns, normalizeWeight):
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
        'seats', #Cost
        'cargo_volume_l' #Benefit
    ]

    dataNumeric = data[criteriaColumns].apply(pd.to_numeric, errors='coerce')

    dataCleaned = data[dataNumeric.notna().all(axis=1)].copy()
    dataCleaned[criteriaColumns] = dataNumeric[dataNumeric.notna().all(axis=1)]

    dataCleaned = dataCleaned[(dataCleaned[criteriaColumns] != 0).all(axis=1)]

    dataFrame = dataCleaned[['brand', 'model'] + criteriaColumns].reset_index(drop=True)
    return dataFrame, criteriaColumns


if __name__ == '__main__':
    df, criteriaColumns = prepare_data()
    print("Jumlah data setelah cleaning:", len(df))

    # # Normalisasi Bobot
    # criteriaWeight = np.array([1/6] * len(criteriaColumns))
    # normalizeWeight = weightNormalization(criteriaWeight)
    # # mark cost criteria as negative (same indices as original script)
    # normalizeWeight[[1, 2]] *= -1

    normalizeWeight = hitung_prioritas()

    df["S"] = computeSValue(df, criteriaColumns, normalizeWeight)
    print("Nilai S dalam dataframe: ", df['S'].head())

    df['V'] = computeVValue(df)
    print("Nilai V dalam dataframe: ", df['V'].head())

    finalRank = computeRank(df)
    print(finalRank.head())
