from pathlib import Path
from io import StringIO
import time

import pandas as pd
import requests

project_root = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
out_dir = project_root / "clean"
out_dir.mkdir(parents=True, exist_ok=True)

county_codes = [
    "MN-001", "MN-003", "MN-005", "MN-007", "MN-009", "MN-011", "MN-013", "MN-015", "MN-017", "MN-019",
    "MN-021", "MN-023", "MN-025", "MN-027", "MN-029", "MN-031", "MN-033", "MN-035", "MN-037", "MN-039",
    "MN-041", "MN-043", "MN-045", "MN-047", "MN-049", "MN-051", "MN-053", "MN-055", "MN-057", "MN-059",
    "MN-061", "MN-063", "MN-065", "MN-067", "MN-069", "MN-071", "MN-073", "MN-075", "MN-077", "MN-079",
    "MN-081", "MN-083", "MN-085", "MN-087", "MN-089", "MN-091", "MN-093", "MN-095", "MN-097", "MN-099",
    "MN-101", "MN-103", "MN-105", "MN-107", "MN-109", "MN-111", "MN-113", "MN-115", "MN-117", "MN-119",
    "MN-121", "MN-123", "MN-125", "MN-127", "MN-129", "MN-131", "MN-133", "MN-135", "MN-137", "MN-139",
    "MN-141", "MN-143", "MN-145", "MN-147", "MN-149", "MN-151", "MN-153", "MN-155", "MN-157", "MN-159",
    "MN-161", "MN-163", "MN-165", "MN-167", "MN-169", "MN-171", "MN-173",
]


def fetch_and_clean_series(county_code, param):
    url = (
        "https://www.ncei.noaa.gov/access/monitoring/climate-at-a-glance/"
        f"county/time-series/{county_code}/{param}/12/0/2011-2023/data.csv"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    raw = pd.read_csv(StringIO(r.text), header=None)

    county_label = str(raw.iloc[0, 0]).replace("#  ", "").strip()

    df = raw.iloc[:, [0, 1]].copy()
    df.columns = ["date", "value"]
    df["date"] = df["date"].astype(str).str.strip()

    # NOAA responses include metadata/header rows; keep only YYYYMM-style observations.
    df = df[df["date"].str.fullmatch(r"\d{6}")].copy()
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["year"] = df["date"].str[:4].astype(int)
    df["county_code"] = county_code
    df["county_name"] = county_label

    if param == "tavg":
        df = df.rename(columns={"value": "temp_avg"})
    elif param == "pcp":
        df = df.rename(columns={"value": "precip_total"})

    return df


temp_list = []
pcp_list = []

for c in county_codes:
    try:
        temp_list.append(fetch_and_clean_series(c, "tavg"))
        pcp_list.append(fetch_and_clean_series(c, "pcp"))
        print(f"Downloaded and cleaned {c}")
        time.sleep(0.25)
    except Exception as e:
        print(f"Failed for {c}: {e}")

if not temp_list or not pcp_list:
    raise RuntimeError("No NOAA series downloaded successfully.")

temp_df = pd.concat(temp_list, ignore_index=True)
pcp_df = pd.concat(pcp_list, ignore_index=True)

temp_df.to_csv(out_dir / "noaa_mn_temp_clean.csv", index=False)
pcp_df.to_csv(out_dir / "noaa_mn_precip_clean.csv", index=False)

print(temp_df.head())
print(pcp_df.head())
print("Temp shape:", temp_df.shape)
print("Precip shape:", pcp_df.shape)
print("Unique temp counties:", temp_df["county_code"].nunique())
print("Unique precip counties:", pcp_df["county_code"].nunique())
