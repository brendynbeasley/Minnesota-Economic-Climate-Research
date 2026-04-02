from pathlib import Path
import pandas as pd

project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
clean_dir = project_root / "clean"

panel = pd.read_csv(clean_dir / "mn_county_panel_2020_2023.csv")
irs = pd.read_csv(clean_dir / "irs_mn_county_year_2023.csv")

# Standardize county_fips
panel["county_fips"] = (
    pd.to_numeric(panel["county_fips"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)

irs["county_fips"] = (
    pd.to_numeric(irs["county_fips"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)

# Year numeric
panel["year"] = pd.to_numeric(panel["year"], errors="coerce")
irs["year"] = pd.to_numeric(irs["year"], errors="coerce")

# Merge
merged = panel.merge(
    irs,
    on=["county_fips", "year"],
    how="left"
)

print("Merged shape:", merged.shape)
print("Unique counties:", merged["county_fips"].nunique())
print("Years:", merged["year"].min(), "-", merged["year"].max())
print("Duplicate county-year rows:", merged.duplicated(["county_fips", "year"]).sum())

# Check IRS coverage
for col in [
    "inflow_returns",
    "inflow_exemptions",
    "outflow_returns",
    "outflow_exemptions",
    "net_migration_returns",
    "net_migration_exemptions"
]:
    if col in merged.columns:
        print(f"Non-missing {col}:", merged[col].notna().sum())

print(merged.head())

merged.to_csv(clean_dir / "mn_county_panel_2020_2023_plus_irs.csv", index=False)
print("Saved:", clean_dir / "mn_county_panel_2020_2023_plus_irs.csv")
