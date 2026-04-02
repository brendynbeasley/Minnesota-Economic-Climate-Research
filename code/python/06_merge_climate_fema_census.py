from pathlib import Path
import pandas as pd

project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
clean_dir = project_root / "clean"

clim = pd.read_csv(clean_dir / "mn_county_panel_climate_fema.csv")
census = pd.read_csv(clean_dir / "census_mn_county_year_2020_2025.csv")

# Standardize county_fips
clim["county_fips"] = (
    pd.to_numeric(clim["county_fips"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)

census["county_fips"] = (
    pd.to_numeric(census["county_fips"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)

# Keep overlapping years only
clim = clim[clim["year"].between(2020, 2023)].copy()
census = census[census["year"].between(2020, 2023)].copy()

# Merge
panel = clim.merge(
    census,
    on=["county_fips", "year"],
    how="left",
    suffixes=("", "_census")
)

print("Merged shape:", panel.shape)
print("Unique counties:", panel["county_fips"].nunique())
print("Years:", panel["year"].min(), "-", panel["year"].max())
print("Duplicate county-year rows:", panel.duplicated(["county_fips", "year"]).sum())

# Check Census merge success
for col in ["pop_total", "npopchg", "net_mig_census"]:
    if col in panel.columns:
        print(f"Missing {col}:", panel[col].isna().sum())

print(panel.head())

panel.to_csv(clean_dir / "mn_county_panel_2020_2023.csv", index=False)
print("Saved:", clean_dir / "mn_county_panel_2020_2023.csv")
