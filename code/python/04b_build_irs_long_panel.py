from pathlib import Path
import pandas as pd

# --------------------------------------------------
# Paths
# --------------------------------------------------
project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
raw_dir = project_root / "raw" / "irs"
clean_dir = project_root / "clean"
clean_dir.mkdir(parents=True, exist_ok=True)

out_file = clean_dir / "irs_mn_county_year_2012_2023.csv"

# --------------------------------------------------
# Year-pair definitions
# pair "1112" means 2011->2012, and output year = 2012
# --------------------------------------------------
pairs = [
    ("1112", 2012),
    ("1213", 2013),
    ("1314", 2014),
    ("1415", 2015),
    ("1516", 2016),
    ("1617", 2017),
    ("1718", 2018),
    ("1819", 2019),
    ("1920", 2020),
    ("2021", 2021),
    ("2122", 2022),
    ("2223", 2023),
]

# --------------------------------------------------
# Helper
# --------------------------------------------------
def pick_col(df, candidates):
    for c in candidates:
        if c in df.columns:
            return c
    return None

def read_csv_fallback(path):
    try:
        return pd.read_csv(path, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="latin1", low_memory=False)

def clean_pair(pair_code: str, out_year: int) -> pd.DataFrame:
    inflow_file = raw_dir / f"countyinflow{pair_code}.csv"
    outflow_file = raw_dir / f"countyoutflow{pair_code}.csv"

    inflow = read_csv_fallback(inflow_file)
    outflow = read_csv_fallback(outflow_file)

    print(f"\n--- Cleaning pair {pair_code} -> year {out_year} ---")
    print("Inflow shape:", inflow.shape)
    print("Outflow shape:", outflow.shape)

    # Common IRS field names
    returns_col_in = pick_col(inflow, ["n1", "N1", "returns"])
    exempt_col_in = pick_col(inflow, ["n2", "N2", " exemptions", "exemptions"])
    returns_col_out = pick_col(outflow, ["n1", "N1", "returns"])
    exempt_col_out = pick_col(outflow, ["n2", "N2", " exemptions", "exemptions"])

    # Prefer y2 for inflow destination, y1 for outflow origin
    if "y2_statefips" in inflow.columns and "y2_countyfips" in inflow.columns:
        inflow["county_fips"] = (
            inflow["y2_statefips"].astype(str).str.zfill(2) +
            inflow["y2_countyfips"].astype(str).str.zfill(3)
        )
        inflow_mn = inflow[inflow["y2_statefips"].astype(str).str.zfill(2) == "27"].copy()
    else:
        state_col_in = pick_col(inflow, ["statefips", "state_fips", "STATEFIPS"])
        county_col_in = pick_col(inflow, ["countyfips", "county_fips", "COUNTYFIPS"])
        if state_col_in is None or county_col_in is None:
            raise ValueError(f"Could not identify inflow FIPS columns for pair {pair_code}")
        inflow["county_fips"] = (
            inflow[state_col_in].astype(str).str.zfill(2) +
            inflow[county_col_in].astype(str).str.zfill(3)
        )
        inflow_mn = inflow[inflow[state_col_in].astype(str).str.zfill(2) == "27"].copy()

    if "y1_statefips" in outflow.columns and "y1_countyfips" in outflow.columns:
        outflow["county_fips"] = (
            outflow["y1_statefips"].astype(str).str.zfill(2) +
            outflow["y1_countyfips"].astype(str).str.zfill(3)
        )
        outflow_mn = outflow[outflow["y1_statefips"].astype(str).str.zfill(2) == "27"].copy()
    else:
        state_col_out = pick_col(outflow, ["statefips", "state_fips", "STATEFIPS"])
        county_col_out = pick_col(outflow, ["countyfips", "county_fips", "COUNTYFIPS"])
        if state_col_out is None or county_col_out is None:
            raise ValueError(f"Could not identify outflow FIPS columns for pair {pair_code}")
        outflow["county_fips"] = (
            outflow[state_col_out].astype(str).str.zfill(2) +
            outflow[county_col_out].astype(str).str.zfill(3)
        )
        outflow_mn = outflow[outflow[state_col_out].astype(str).str.zfill(2) == "27"].copy()

    if returns_col_in is None or exempt_col_in is None:
        raise ValueError(f"Could not identify inflow returns/exemptions columns for pair {pair_code}")
    if returns_col_out is None or exempt_col_out is None:
        raise ValueError(f"Could not identify outflow returns/exemptions columns for pair {pair_code}")

    inflow_agg = inflow_mn.groupby("county_fips", as_index=False).agg(
        inflow_returns=(returns_col_in, "sum"),
        inflow_exemptions=(exempt_col_in, "sum"),
    )

    outflow_agg = outflow_mn.groupby("county_fips", as_index=False).agg(
        outflow_returns=(returns_col_out, "sum"),
        outflow_exemptions=(exempt_col_out, "sum"),
    )

    df = inflow_agg.merge(outflow_agg, on="county_fips", how="outer").fillna(0)
    df["year"] = out_year
    df["net_migration_returns"] = df["inflow_returns"] - df["outflow_returns"]
    df["net_migration_exemptions"] = df["inflow_exemptions"] - df["outflow_exemptions"]

    print("Cleaned rows:", df.shape[0])
    print("Unique counties:", df["county_fips"].nunique())

    return df

# --------------------------------------------------
# Build long file
# --------------------------------------------------
all_years = []

for pair_code, out_year in pairs:
    df_year = clean_pair(pair_code, out_year)
    all_years.append(df_year)

irs_long = pd.concat(all_years, ignore_index=True)

# Standardize types
irs_long["county_fips"] = (
    pd.to_numeric(irs_long["county_fips"], errors="coerce")
    .astype("Int64")
    .astype(str)
    .str.replace("<NA>", "", regex=False)
    .str.zfill(5)
)
irs_long["year"] = pd.to_numeric(irs_long["year"], errors="coerce").astype(int)

irs_long = irs_long.sort_values(["county_fips", "year"]).reset_index(drop=True)

print("\n=== FINAL IRS LONG FILE ===")
print("Shape:", irs_long.shape)
print("Unique counties:", irs_long["county_fips"].nunique())
print("Years:", irs_long["year"].min(), "-", irs_long["year"].max())
print("Duplicate county-year rows:", irs_long.duplicated(["county_fips", "year"]).sum())
print(irs_long.head(12))
print(irs_long.tail(12))

irs_long.to_csv(out_file, index=False)
print(f"\nSaved to: {out_file}")
