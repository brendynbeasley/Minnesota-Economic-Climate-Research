from pathlib import Path
import pandas as pd

# -----------------------------------
# Paths
# -----------------------------------
project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
raw_file = project_root / "raw" / "fema" / "NRI_Table_Counties" / "NRI_Table_Counties.csv"
out_file = project_root / "clean" / "fema_mn_counties_clean.csv"

# If you're just testing with the file you uploaded here, use:
# raw_file = Path("/mnt/data/NRI_Table_Counties.csv")
# out_file = Path("/mnt/data/fema_mn_counties_clean.csv")

# -----------------------------------
# Load data
# -----------------------------------
df = pd.read_csv(raw_file, low_memory=False)

print("Rows, cols:", df.shape)
print("First 20 columns:")
print(df.columns[:20].tolist())

# -----------------------------------
# Keep only Minnesota
# -----------------------------------
df_mn = df[df["STATEABBRV"] == "MN"].copy()

print("Minnesota rows:", len(df_mn))
print("Unique counties:", df_mn["COUNTY"].nunique())

# -----------------------------------
# Build/clean county FIPS
# -----------------------------------
# STCOFIPS should already be full county FIPS, but force it to 5-digit string
df_mn["county_fips"] = (
    pd.to_numeric(df_mn["STCOFIPS"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)

# -----------------------------------
# Columns to keep
# -----------------------------------
keep_cols = [
    # identifiers
    "STATE",
    "STATEABBRV",
    "STATEFIPS",
    "COUNTY",
    "COUNTYFIPS",
    "STCOFIPS",
    "county_fips",

    # overall risk
    "RISK_VALUE",
    "RISK_SCORE",
    "RISK_RATNG",
    "EAL_VALT",
    "EAL_SCORE",
    "EAL_RATNG",
    "SOVI_SCORE",
    "SOVI_RATNG",
    "RESL_SCORE",
    "RESL_RATNG",

    # drought
    "DRGT_RISKV",
    "DRGT_RISKS",
    "DRGT_RISKR",

    # inland flooding
    "IFLD_RISKV",
    "IFLD_RISKS",
    "IFLD_RISKR",

    # wildfire
    "WFIR_RISKV",
    "WFIR_RISKS",
    "WFIR_RISKR",

    # heat wave
    "HWAV_RISKV",
    "HWAV_RISKS",
    "HWAV_RISKR",

    # winter weather
    "WNTW_RISKV",
    "WNTW_RISKS",
    "WNTW_RISKR",

    # version
    "NRI_VER",
]

# Keep only columns that actually exist
existing_keep_cols = [c for c in keep_cols if c in df_mn.columns]
missing_cols = [c for c in keep_cols if c not in df_mn.columns]

print("\nMissing columns (if any):")
print(missing_cols)

df_mn = df_mn[existing_keep_cols].copy()

# -----------------------------------
# Optional: rename to nicer names
# -----------------------------------
rename_map = {
    "STATE": "state_name",
    "STATEABBRV": "state_abbr",
    "STATEFIPS": "state_fips",
    "COUNTY": "county_name",
    "COUNTYFIPS": "county_fips_3",
    "STCOFIPS": "county_fips_raw",

    "RISK_VALUE": "risk_value",
    "RISK_SCORE": "risk_score",
    "RISK_RATNG": "risk_rating",

    "EAL_VALT": "eal_value_total",
    "EAL_SCORE": "eal_score",
    "EAL_RATNG": "eal_rating",

    "SOVI_SCORE": "sovi_score",
    "SOVI_RATNG": "sovi_rating",
    "RESL_SCORE": "resl_score",
    "RESL_RATNG": "resl_rating",

    "DRGT_RISKV": "drought_risk_value",
    "DRGT_RISKS": "drought_risk_score",
    "DRGT_RISKR": "drought_risk_rating",

    "IFLD_RISKV": "inland_flood_risk_value",
    "IFLD_RISKS": "inland_flood_risk_score",
    "IFLD_RISKR": "inland_flood_risk_rating",

    "WFIR_RISKV": "wildfire_risk_value",
    "WFIR_RISKS": "wildfire_risk_score",
    "WFIR_RISKR": "wildfire_risk_rating",

    "HWAV_RISKV": "heatwave_risk_value",
    "HWAV_RISKS": "heatwave_risk_score",
    "HWAV_RISKR": "heatwave_risk_rating",

    "WNTW_RISKV": "winter_weather_risk_value",
    "WNTW_RISKS": "winter_weather_risk_score",
    "WNTW_RISKR": "winter_weather_risk_rating",

    "NRI_VER": "nri_version",
}

df_mn = df_mn.rename(columns={k: v for k, v in rename_map.items() if k in df_mn.columns})

# -----------------------------------
# Quality checks
# -----------------------------------
print("\nPreview:")
print(df_mn.head())

print("\nUnique county_fips:", df_mn["county_fips"].nunique())
print("Any duplicate county_fips?:", df_mn["county_fips"].duplicated().any())

print("\nMissing values by column:")
print(df_mn.isna().sum().sort_values(ascending=False).head(15))

# -----------------------------------
# Save
# -----------------------------------
out_file.parent.mkdir(parents=True, exist_ok=True)
df_mn.to_csv(out_file, index=False)

print(f"\nSaved cleaned FEMA Minnesota file to:\n{out_file}")
