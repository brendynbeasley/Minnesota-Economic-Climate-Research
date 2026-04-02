#!/usr/bin/env python3

"""Build a tidy Minnesota county-year BEA CAINC1 panel."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
RAW_FILE = ROOT / "raw" / "bea" / "CAINC1_MN_1969_2024.csv"
OUT_ALL = ROOT / "clean" / "bea_mn_county_year_1969_2024.csv"
OUT_2011 = ROOT / "clean" / "bea_mn_county_year_2011_2024.csv"

LINE_MAP = {
    "1": "bea_personal_income",
    "2": "bea_population",
    "3": "bea_pc_income",
}


def clean_text(value: str | None) -> str:
    return "" if value is None else value.strip()


def clean_county_name(geo_name: str) -> str:
    return geo_name.replace(", MN", "").strip()


def parse_numeric(value: str | None) -> str:
    value = clean_text(value)
    return "" if value in {"", "(NA)", "(D)"} else value


def main() -> None:
    with RAW_FILE.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        years = [field for field in reader.fieldnames if field and field.isdigit()]
        panel: dict[tuple[str, str], dict[str, str]] = {}

        for row in reader:
            line_code = clean_text(row.get("LineCode"))
            if line_code not in LINE_MAP:
                continue

            county_fips = clean_text(row.get("GeoFIPS")).replace('"', "")
            if county_fips == "27000":
                continue

            county_name = clean_county_name(clean_text(row.get("GeoName")).replace('"', ""))
            for year in years:
                key = (county_fips, year)
                record = panel.setdefault(
                    key,
                    {
                        "county_fips": county_fips,
                        "county_name_bea": county_name,
                        "year": year,
                        "bea_personal_income": "",
                        "bea_population": "",
                        "bea_pc_income": "",
                    },
                )
                record[LINE_MAP[line_code]] = parse_numeric(row.get(year))

    rows = sorted(panel.values(), key=lambda r: (r["county_fips"], int(r["year"])))
    out_fields = [
        "county_fips",
        "county_name_bea",
        "year",
        "bea_personal_income",
        "bea_population",
        "bea_pc_income",
    ]

    OUT_ALL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_ALL.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows)

    rows_2011 = [row for row in rows if 2011 <= int(row["year"]) <= 2024]
    with OUT_2011.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(rows_2011)

    print(f"Wrote {len(rows):,} rows to {OUT_ALL}")
    print(f"Wrote {len(rows_2011):,} rows to {OUT_2011}")


if __name__ == "__main__":
    main()
