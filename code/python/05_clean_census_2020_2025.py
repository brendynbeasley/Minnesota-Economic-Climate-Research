from pathlib import Path
import pandas as pd

project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
raw_dir = project_root / "raw" / "census"
clean_dir = project_root / "clean"

census = pd.read_csv(
    raw_dir / "co-est2025-alldata.csv",
    encoding="latin1",
    low_memory=False
)

# Keep only county-level Minnesota rows
# SUMLEV 50 = county
mn = census[(census["SUMLEV"] == 50) & (census["STATE"] == 27)].copy()

# Build county_fips
mn["county_fips"] = (
    mn["STATE"].astype(int).astype(str).str.zfill(2) +
    mn["COUNTY"].astype(int).astype(str).str.zfill(3)
)

# Keep needed columns
keep_cols = [
    "county_fips",
    "STNAME",
    "CTYNAME",
    "POPESTIMATE2020",
    "POPESTIMATE2021",
    "POPESTIMATE2022",
    "POPESTIMATE2023",
    "POPESTIMATE2024",
    "POPESTIMATE2025",
    "NPOPCHG2020",
    "NPOPCHG2021",
    "NPOPCHG2022",
    "NPOPCHG2023",
    "NPOPCHG2024",
    "NPOPCHG2025",
    "NETMIG2020",
    "NETMIG2021",
    "NETMIG2022",
    "NETMIG2023",
    "NETMIG2024",
    "NETMIG2025",
]

mn = mn[keep_cols].copy()

# Reshape population
pop_cols = [c for c in mn.columns if c.startswith("POPESTIMATE")]
pop_long = mn.melt(
    id_vars=["county_fips", "STNAME", "CTYNAME"],
    value_vars=pop_cols,
    var_name="var",
    value_name="pop_total"
)
pop_long["year"] = pop_long["var"].str.replace("POPESTIMATE", "", regex=False).astype(int)
pop_long = pop_long.drop(columns="var")

# Reshape net population change
chg_cols = [c for c in mn.columns if c.startswith("NPOPCHG")]
chg_long = mn.melt(
    id_vars=["county_fips", "STNAME", "CTYNAME"],
    value_vars=chg_cols,
    var_name="var",
    value_name="npopchg"
)
chg_long["year"] = chg_long["var"].str.replace("NPOPCHG", "", regex=False).astype(int)
chg_long = chg_long.drop(columns="var")

# Reshape net migration
mig_cols = [c for c in mn.columns if c.startswith("NETMIG")]
mig_long = mn.melt(
    id_vars=["county_fips", "STNAME", "CTYNAME"],
    value_vars=mig_cols,
    var_name="var",
    value_name="net_mig_census"
)
mig_long["year"] = mig_long["var"].str.replace("NETMIG", "", regex=False).astype(int)
mig_long = mig_long.drop(columns="var")

# Merge together
census_long = pop_long.merge(
    chg_long,
    on=["county_fips", "STNAME", "CTYNAME", "year"],
    how="left"
).merge(
    mig_long,
    on=["county_fips", "STNAME", "CTYNAME", "year"],
    how="left"
)

# Rename
census_long = census_long.rename(columns={
    "STNAME": "state_name",
    "CTYNAME": "county_name"
})

# Sort
census_long = census_long.sort_values(["county_fips", "year"]).reset_index(drop=True)

# Add population growth rate
census_long["pop_growth_rate"] = (
    census_long.groupby("county_fips")["pop_total"].pct_change() * 100
)

print("Shape:", census_long.shape)
print("Unique counties:", census_long["county_fips"].nunique())
print("Years:", census_long["year"].min(), "-", census_long["year"].max())
print("Duplicate county-year rows:", census_long.duplicated(["county_fips", "year"]).sum())
print(census_long.head())

census_long.to_csv(clean_dir / "census_mn_county_year_2020_2025.csv", index=False)
print("Saved:", clean_dir / "census_mn_county_year_2020_2025.csv")
