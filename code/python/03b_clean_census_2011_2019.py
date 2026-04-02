from pathlib import Path
import pandas as pd

# -----------------------------
# Paths
# -----------------------------
project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
raw_file = project_root / "raw" / "census" / "co-est2019-alldata.csv"
out_file = project_root / "clean" / "census_mn_county_year_2011_2019.csv"

# If you are testing with the uploaded file directly, use:
# raw_file = Path("/mnt/data/co-est2019-alldata.csv")
# out_file = Path("/mnt/data/census_mn_county_year_2011_2019.csv")

# -----------------------------
# Load raw Census file
# -----------------------------
df = pd.read_csv(raw_file, encoding="latin1", low_memory=False)

print("Raw shape:", df.shape)
print("First columns:", df.columns[:20].tolist())

# -----------------------------
# Keep Minnesota counties only
# SUMLEV 50 = county
# STATE 27 = Minnesota
# -----------------------------
mn = df[(df["SUMLEV"] == 50) & (df["STATE"] == 27)].copy()

print("Minnesota county rows:", mn.shape[0])

# -----------------------------
# Build 5-digit county FIPS
# -----------------------------
mn["county_fips"] = (
    mn["STATE"].astype(int).astype(str).str.zfill(2) +
    mn["COUNTY"].astype(int).astype(str).str.zfill(3)
)

# -----------------------------
# Keep 2011-2019 population columns
# -----------------------------
pop_cols = [f"POPESTIMATE{y}" for y in range(2011, 2020)]

keep_cols = ["county_fips", "STNAME", "CTYNAME"] + pop_cols
mn = mn[keep_cols].copy()

# -----------------------------
# Reshape to long county-year
# -----------------------------
long_df = mn.melt(
    id_vars=["county_fips", "STNAME", "CTYNAME"],
    value_vars=pop_cols,
    var_name="var",
    value_name="pop_total"
)

long_df["year"] = long_df["var"].str.replace("POPESTIMATE", "", regex=False).astype(int)
long_df = long_df.drop(columns=["var"])

# Rename for consistency
long_df = long_df.rename(columns={
    "STNAME": "state_name",
    "CTYNAME": "county_name"
})

# Sort
long_df = long_df.sort_values(["county_fips", "year"]).reset_index(drop=True)

# -----------------------------
# Create population growth rate
# -----------------------------
long_df["pop_growth_rate"] = (
    long_df.groupby("county_fips")["pop_total"].pct_change() * 100
)

# -----------------------------
# Checks
# -----------------------------
print("\nCleaned shape:", long_df.shape)
print("Unique counties:", long_df["county_fips"].nunique())
print("Years:", long_df["year"].min(), "-", long_df["year"].max())
print("Duplicate county-year rows:", long_df.duplicated(["county_fips", "year"]).sum())
print("\nPreview:")
print(long_df.head(10))

# -----------------------------
# Save
# -----------------------------
out_file.parent.mkdir(parents=True, exist_ok=True)
long_df.to_csv(out_file, index=False)

print(f"\nSaved to: {out_file}")
