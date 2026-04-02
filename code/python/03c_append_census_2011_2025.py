from pathlib import Path
import pandas as pd

# -----------------------------
# Paths
# -----------------------------
project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
clean_dir = project_root / "clean"

file_2011_2019 = clean_dir / "census_mn_county_year_2011_2019.csv"
file_2020_2025 = clean_dir / "census_mn_county_year_2020_2025.csv"
out_file = clean_dir / "census_mn_county_year_2011_2025.csv"

# If testing directly with uploaded files, use:
# file_2011_2019 = Path("/mnt/data/census_mn_county_year_2011_2019.csv")
# file_2020_2025 = Path("/mnt/data/census_mn_county_year_2020_2025.csv")
# out_file = Path("/mnt/data/census_mn_county_year_2011_2025.csv")

# -----------------------------
# Load
# -----------------------------
a = pd.read_csv(file_2011_2019)
b = pd.read_csv(file_2020_2025)

print("2011-2019 shape:", a.shape)
print("2020-2025 shape:", b.shape)

# -----------------------------
# Keep common columns / harmonize
# -----------------------------
# Make sure names line up
rename_map_b = {}
if "state_name" not in b.columns and "STNAME" in b.columns:
    rename_map_b["STNAME"] = "state_name"
if "county_name" not in b.columns and "CTYNAME" in b.columns:
    rename_map_b["CTYNAME"] = "county_name"

b = b.rename(columns=rename_map_b)

# Keep the core columns we want
keep_cols = [
    "county_fips",
    "state_name",
    "county_name",
    "year",
    "pop_total",
    "pop_growth_rate"
]

a = a[keep_cols].copy()
b = b[keep_cols].copy()

# Standardize county_fips
for df in [a, b]:
    df["county_fips"] = (
        pd.to_numeric(df["county_fips"], errors="coerce")
        .astype("Int64")
        .astype(str)
        .str.replace("<NA>", "", regex=False)
        .str.zfill(5)
    )
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype(int)

# -----------------------------
# Append
# -----------------------------
full = pd.concat([a, b], ignore_index=True)

# Sort
full = full.sort_values(["county_fips", "year"]).reset_index(drop=True)

# Rebuild pop_growth_rate over the full span
full["pop_growth_rate"] = (
    full.groupby("county_fips")["pop_total"].pct_change() * 100
)

# -----------------------------
# Checks
# -----------------------------
print("\nFull shape:", full.shape)
print("Unique counties:", full["county_fips"].nunique())
print("Years:", full["year"].min(), "-", full["year"].max())
print("Duplicate county-year rows:", full.duplicated(["county_fips", "year"]).sum())
print("\nPreview:")
print(full.head(12))
print("\nTail:")
print(full.tail(12))

# -----------------------------
# Save
# -----------------------------
out_file.parent.mkdir(parents=True, exist_ok=True)
full.to_csv(out_file, index=False)

print(f"\nSaved to: {out_file}")
