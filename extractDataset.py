import pandas as pd

dataFrame = pd.read_csv("default_ev_spec_dataset.csv")

newDataFrame = dataFrame[['brand', 'model', 'range_km', 'efficiency_wh_per_km', 'acceleration_0_100_s', 'fast_charging_power_kw_dc', 'seats', 'cargo_volume_l']]

newDataFrame.to_csv("clean_ev_spec_dataset.csv", index=False)
