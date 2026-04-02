#!/usr/bin/env python3

"""Build a tidy Minnesota county-year Census Building Permits Survey panel."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
RAW_FILE = ROOT / "raw" / "census_bps" / "New_Master_python_2026_01.csv"
OUT_ALL = ROOT / "clean" / "bps_mn_county_year_1990_2024.csv"
OUT_2011 = ROOT / "clean" / "bps_mn_county_year_2011_2024.csv"

KEEP_FIELDS = {
    "county_fips": "FIPS_COUNTY_5_DIGITS",
    "county_name_bps": "COUNTY_NAME",
    "year": "YEAR",
    "bps_total_bldgs": "TOTAL_BLDGS",
    "bps_total_bldgs_rep": "TOTAL_BLDGS_REP",
    "bps_total_units": "TOTAL_UNITS",
    "bps_total_units_rep": "TOTAL_UNITS_REP",
    "bps_total_value": "TOTAL_VALUE",
    "bps_total_value_rep": "TOTAL_VALUE_REP",
    "bps_bldgs_1_unit": "BLDGS_1_UNIT",
    "bps_bldgs_1_unit_rep": "BLDGS_1_UNIT_REP",
    "bps_bldgs_2_units": "BLDGS_2_UNITS",
    "bps_bldgs_2_units_rep": "BLDGS_2_UNITS_REP",
    "bps_bldgs_3_4_units": "BLDGS_3_4_UNITS",
    "bps_bldgs_3_4_units_rep": "BLDGS_3_4_UNITS_REP",
    "bps_bldgs_5_units": "BLDGS_5_UNITS",
    "bps_bldgs_5_units_rep": "BLDGS_5_UNITS_REP",
    "bps_units_1_unit": "UNITS_1_UNIT",
    "bps_units_1_unit_rep": "UNITS_1_UNIT_REP",
    "bps_units_2_units": "UNITS_2_UNITS",
    "bps_units_2_units_rep": "UNITS_2_UNITS_REP",
    "bps_units_3_4_units": "UNITS_3_4_UNITS",
    "bps_units_3_4_units_rep": "UNITS_3_4_UNITS_REP",
    "bps_units_5_units": "UNITS_5_UNITS",
    "bps_units_5_units_rep": "UNITS_5_UNITS_REP",
    "bps_value_1_unit": "VALUE_1_UNIT",
    "bps_value_1_unit_rep": "VALUE_1_UNIT_REP",
    "bps_value_2_units": "VALUE_2_UNITS",
    "bps_value_2_units_rep": "VALUE_2_UNITS_REP",
    "bps_value_3_4_units": "VALUE_3_4_UNITS",
    "bps_value_3_4_units_rep": "VALUE_3_4_UNITS_REP",
    "bps_value_5_units": "VALUE_5_UNITS",
    "bps_value_5_units_rep": "VALUE_5_UNITS_REP",
}


def clean_text(value: str | None) -> str:
    return "" if value is None else value.strip()


def clean_county_name(value: str | None) -> str:
    name = clean_text(value)
    return name.replace(" County", "").strip()


def parse_numeric(value: str | None) -> str:
    value = clean_text(value)
    if value in {"", ".", "(D)", "(NA)"}:
        return ""
    return value.replace(",", "")


def build_record(row: dict[str, str]) -> dict[str, str]:
    record: dict[str, str] = {}
    for out_name, raw_name in KEEP_FIELDS.items():
        if out_name == "county_name_bps":
            record[out_name] = clean_county_name(row.get(raw_name))
        elif out_name in {"county_fips", "year"}:
            record[out_name] = clean_text(row.get(raw_name))
        else:
            record[out_name] = parse_numeric(row.get(raw_name))
    return record


def substantive_payload(record: dict[str, str]) -> tuple[tuple[str, str], ...]:
    return tuple(
        (key, value)
        for key, value in sorted(record.items())
        if key not in {"county_fips", "year"}
    )


def main() -> None:
    records: dict[tuple[str, str], dict[str, str]] = {}
    duplicate_rows = 0
    conflicting_rows: list[tuple[tuple[str, str], dict[str, str], dict[str, str]]] = []

    with RAW_FILE.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if clean_text(row.get("STATE_NAME")) != "Minnesota":
                continue
            if clean_text(row.get("LOCATION_TYPE")) != "County":
                continue
            if clean_text(row.get("PERIOD")) != "Annual":
                continue

            record = build_record(row)
            key = (record["county_fips"], record["year"])

            if key in records:
                duplicate_rows += 1
                if substantive_payload(records[key]) != substantive_payload(record):
                    conflicting_rows.append((key, records[key], record))
                continue

            records[key] = record

    if conflicting_rows:
        first_key, first_old, first_new = conflicting_rows[0]
        raise ValueError(
            "Found conflicting duplicate county-year rows in BPS data: "
            f"{first_key}\nexisting={first_old}\nnew={first_new}"
        )

    rows = sorted(records.values(), key=lambda r: (r["county_fips"], int(r["year"])))
    fieldnames = list(KEEP_FIELDS)

    OUT_ALL.parent.mkdir(parents=True, exist_ok=True)
    with OUT_ALL.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    rows_2011 = [row for row in rows if 2011 <= int(row["year"]) <= 2024]
    with OUT_2011.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_2011)

    print(f"Wrote {len(rows):,} rows to {OUT_ALL}")
    print(f"Wrote {len(rows_2011):,} rows to {OUT_2011}")
    print(f"Dropped {duplicate_rows:,} duplicate annual rows after county-year deduplication")


if __name__ == "__main__":
    main()
