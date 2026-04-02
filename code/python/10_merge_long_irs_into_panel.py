from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
clean_dir = project_root / "clean"

panel_file = clean_dir / "mn_county_panel_2011_2023.csv"
irs_file = clean_dir / "irs_mn_county_year_2012_2023.csv"
out_file = clean_dir / "mn_county_panel_2011_2023_plus_irs.csv"

# --------------------------------------------------
# Load
# --------------------------------------------------
panel = pd.read_csv(panel_file)
irs = pd.read_csv(irs_file)

print("Panel shape:", panel.shape)
print("IRS shape:", irs.shape)

# --------------------------------------------------
# Standardize keys
# --------------------------------------------------
for df in [panel, irs]:
    df["county_fips"] = (
        pd.to_numeric(df["county_fips"], errors="coerce")
        .astype("Int64")
        .astype(str)
        .str.replace("<NA>", "", regex=False)
        .str.zfill(5)
    )
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)

# --------------------------------------------------
# Merge
# --------------------------------------------------
merged = panel.merge(
    irs,
    on=["county_fips", "year"],
    how="left"
)

# --------------------------------------------------
# Checks
# --------------------------------------------------
print("\nMerged shape:", merged.shape)
print("Unique counties:", merged["county_fips"].nunique())
print("Years:", merged["year"].min(), "-", merged["year"].max())
print("Duplicate county-year rows:", merged.duplicated(["county_fips", "year"]).sum())

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

print("\nPreview:")
print(merged.head(12))
print("\nTail:")
print(merged.tail(12))

# --------------------------------------------------
# Save
# --------------------------------------------------
out_file.parent.mkdir(parents=True, exist_ok=True)
merged.to_csv(out_file, index=False)

print(f"\nSaved to: {out_file}")
