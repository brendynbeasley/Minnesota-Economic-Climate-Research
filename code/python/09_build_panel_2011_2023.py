from pathlib import Path
import pandas as pd

# -----------------------------
# Paths
# -----------------------------
project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
clean_dir = project_root / "clean"

noaa_file = clean_dir / "noaa_mn_county_year.csv"
fema_file = clean_dir / "fema_mn_counties_clean.csv"
census_file = clean_dir / "census_mn_county_year_2011_2025.csv"

out_file = clean_dir / "mn_county_panel_2011_2023.csv"

# If testing directly with uploaded files:
# census_file = Path("/mnt/data/census_mn_county_year_2011_2025.csv")

# -----------------------------
# Load
# -----------------------------
noaa = pd.read_csv(noaa_file)
fema = pd.read_csv(fema_file)
census = pd.read_csv(census_file)

print("NOAA shape:", noaa.shape)
print("FEMA shape:", fema.shape)
print("Census shape:", census.shape)

# -----------------------------
# Standardize county_fips + year
# -----------------------------
for df in [noaa, fema, census]:
    if "county_fips" in df.columns:
        df["county_fips"] = (
            pd.to_numeric(df["county_fips"], errors="coerce")
            .astype("Int64")
            .astype(str)
            .str.replace("<NA>", "", regex=False)
            .str.zfill(5)
        )

if "year" in noaa.columns:
    noaa["year"] = pd.to_numeric(noaa["year"], errors="coerce").astype(int)
if "year" in census.columns:
    census["year"] = pd.to_numeric(census["year"], errors="coerce").astype(int)

# -----------------------------
# Restrict overlap years: 2011-2023
# -----------------------------
noaa = noaa[noaa["year"].between(2011, 2023)].copy()
census = census[census["year"].between(2011, 2023)].copy()

# -----------------------------
# Merge NOAA + Census
# -----------------------------
panel = noaa.merge(
    census,
    on=["county_fips", "year"],
    how="inner",
    suffixes=("", "_census")
)

# -----------------------------
# Merge FEMA county baseline
# -----------------------------
panel = panel.merge(
    fema,
    on="county_fips",
    how="left",
    suffixes=("", "_fema")
)

# -----------------------------
# Checks
# -----------------------------
print("\nMerged shape:", panel.shape)
print("Unique counties:", panel["county_fips"].nunique())
print("Years:", panel["year"].min(), "-", panel["year"].max())
print("Duplicate county-year rows:", panel.duplicated(["county_fips", "year"]).sum())

# Missingness check on main variables
check_vars = ["temp_avg", "precip_total", "pop_total", "pop_growth_rate"]
for v in check_vars:
    if v in panel.columns:
        print(f"Missing {v}:", panel[v].isna().sum())

print("\nPreview:")
print(panel.head(10))

# -----------------------------
# Save
# -----------------------------
out_file.parent.mkdir(parents=True, exist_ok=True)
panel.to_csv(out_file, index=False)

print(f"\nSaved to: {out_file}")
