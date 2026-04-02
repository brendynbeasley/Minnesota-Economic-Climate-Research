from pathlib import Path
import pandas as pd

project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
raw_dir = project_root / "raw" / "irs"
clean_dir = project_root / "clean"

def read_csv_fallback(path):
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1", low_memory=False)

inflow = read_csv_fallback(raw_dir / "countyinflow2223.csv")
outflow = read_csv_fallback(raw_dir / "countyoutflow2223.csv")

print("INFLOW COLUMNS:")
print(inflow.columns.tolist())
print("\nOUTFLOW COLUMNS:")
print(outflow.columns.tolist())

# -----------------------------
# Helper to find likely columns
# -----------------------------
def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

# Try common IRS names
state_col_in = pick_col(inflow, ["y1_statefips", "statefips", "state_fips", "STATEFIPS", "y2_statefips"])
county_col_in = pick_col(inflow, ["y1_countyfips", "countyfips", "county_fips", "COUNTYFIPS", "y2_countyfips"])
returns_col_in = pick_col(inflow, ["n1", "N1", "returns"])
exempt_col_in = pick_col(inflow, ["n2", "N2", " exemptions", "exemptions"])

state_col_out = pick_col(outflow, ["y1_statefips", "statefips", "state_fips", "STATEFIPS", "y2_statefips"])
county_col_out = pick_col(outflow, ["y1_countyfips", "countyfips", "county_fips", "COUNTYFIPS", "y2_countyfips"])
returns_col_out = pick_col(outflow, ["n1", "N1", "returns"])
exempt_col_out = pick_col(outflow, ["n2", "N2", " exemptions", "exemptions"])

print("\nChosen inflow cols:", state_col_in, county_col_in, returns_col_in, exempt_col_in)
print("Chosen outflow cols:", state_col_out, county_col_out, returns_col_out, exempt_col_out)

# -----------------------------
# Keep Minnesota destination/origin county totals
# For now, we assume y2 = destination on inflow and y1 = origin on outflow if present.
# If your columns differ, the prints above will show us.
# -----------------------------
if "y2_statefips" in inflow.columns and "y2_countyfips" in inflow.columns:
    inflow["county_fips"] = (
        inflow["y2_statefips"].astype(str).str.zfill(2) +
        inflow["y2_countyfips"].astype(str).str.zfill(3)
    )
    inflow_mn = inflow[inflow["y2_statefips"].astype(str).str.zfill(2) == "27"].copy()
elif state_col_in and county_col_in:
    inflow["county_fips"] = (
        inflow[state_col_in].astype(str).str.zfill(2) +
        inflow[county_col_in].astype(str).str.zfill(3)
    )
    inflow_mn = inflow[inflow[state_col_in].astype(str).str.zfill(2) == "27"].copy()
else:
    raise ValueError("Could not identify Minnesota county columns in inflow file.")

if "y1_statefips" in outflow.columns and "y1_countyfips" in outflow.columns:
    outflow["county_fips"] = (
        outflow["y1_statefips"].astype(str).str.zfill(2) +
        outflow["y1_countyfips"].astype(str).str.zfill(3)
    )
    outflow_mn = outflow[outflow["y1_statefips"].astype(str).str.zfill(2) == "27"].copy()
elif state_col_out and county_col_out:
    outflow["county_fips"] = (
        outflow[state_col_out].astype(str).str.zfill(2) +
        outflow[county_col_out].astype(str).str.zfill(3)
    )
    outflow_mn = outflow[outflow[state_col_out].astype(str).str.zfill(2) == "27"].copy()
else:
    raise ValueError("Could not identify Minnesota county columns in outflow file.")

# -----------------------------
# Collapse to county totals
# -----------------------------
inflow_agg = inflow_mn.groupby("county_fips", as_index=False).agg(
    inflow_returns=(returns_col_in, "sum"),
    inflow_exemptions=(exempt_col_in, "sum"),
)

outflow_agg = outflow_mn.groupby("county_fips", as_index=False).agg(
    outflow_returns=(returns_col_out, "sum"),
    outflow_exemptions=(exempt_col_out, "sum"),
)

irs = inflow_agg.merge(outflow_agg, on="county_fips", how="outer").fillna(0)

irs["year"] = 2023
irs["net_migration_returns"] = irs["inflow_returns"] - irs["outflow_returns"]
irs["net_migration_exemptions"] = irs["inflow_exemptions"] - irs["outflow_exemptions"]

print("\nIRS cleaned shape:", irs.shape)
print("Unique counties:", irs["county_fips"].nunique())
print(irs.head())

irs.to_csv(clean_dir / "irs_mn_county_year_2023.csv", index=False)
print("\nSaved:", clean_dir / "irs_mn_county_year_2023.csv")
