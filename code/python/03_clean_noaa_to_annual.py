from pathlib import Path
import pandas as pd

project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
clean_dir = project_root / "clean"

temp = pd.read_csv(clean_dir / "noaa_mn_temp_clean.csv")
precip = pd.read_csv(clean_dir / "noaa_mn_precip_clean.csv")

# Make sure year is numeric
temp["year"] = pd.to_numeric(temp["year"], errors="coerce")
precip["year"] = pd.to_numeric(precip["year"], errors="coerce")

# Build annual county-year temperature: mean over months
temp_annual = (
    temp.groupby(["county_code", "county_name", "year"], as_index=False)
        .agg(temp_avg=("temp_avg", "mean"))
)

# Build annual county-year precipitation: sum over months
precip_annual = (
    precip.groupby(["county_code", "county_name", "year"], as_index=False)
          .agg(precip_total=("precip_total", "sum"))
)

# Merge together
noaa_annual = temp_annual.merge(
    precip_annual,
    on=["county_code", "county_name", "year"],
    how="inner"
)

# Create county_fips in the same style as FEMA
noaa_annual["county_fips"] = noaa_annual["county_code"].str.replace("MN-", "27", regex=False)

# Optional reorder
noaa_annual = noaa_annual[
    ["county_fips", "county_code", "county_name", "year", "temp_avg", "precip_total"]
].copy()

# Checks
print("Temp annual shape:", temp_annual.shape)
print("Precip annual shape:", precip_annual.shape)
print("Merged annual NOAA shape:", noaa_annual.shape)
print("Unique counties:", noaa_annual["county_code"].nunique())
print("Years:", noaa_annual["year"].min(), "-", noaa_annual["year"].max())
print("Duplicates county-year:", noaa_annual.duplicated(["county_code", "year"]).sum())
print(noaa_annual.head())

# Save
noaa_annual.to_csv(clean_dir / "noaa_mn_county_year.csv", index=False)
print(f"Saved to: {clean_dir / 'noaa_mn_county_year.csv'}")
