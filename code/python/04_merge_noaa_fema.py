from pathlib import Path
import pandas as pd

project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
clean_dir = project_root / "clean"

noaa = pd.read_csv(clean_dir / "noaa_mn_county_year.csv")
fema = pd.read_csv(clean_dir / "fema_mn_counties_clean.csv")

# Force county_fips to 5-digit strings in both files
noaa["county_fips"] = (
    pd.to_numeric(noaa["county_fips"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)

fema["county_fips"] = (
    pd.to_numeric(fema["county_fips"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)

# Merge
merged = noaa.merge(
    fema,
    on="county_fips",
    how="left",
    suffixes=("", "_fema")
)

print("Merged shape:", merged.shape)
print("Unique counties:", merged["county_fips"].nunique())
print("Years:", merged["year"].min(), "-", merged["year"].max())
print("Missing FEMA matches:", merged["risk_value"].isna().sum() if "risk_value" in merged.columns else "check FEMA col names")
print(merged.head())

merged.to_csv(clean_dir / "mn_county_panel_climate_fema.csv", index=False)
print(f"Saved to: {clean_dir / 'mn_county_panel_climate_fema.csv'}")
