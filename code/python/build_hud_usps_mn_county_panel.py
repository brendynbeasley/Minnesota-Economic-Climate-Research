#!/usr/bin/env python3

"""Build a Minnesota county-year HUD USPS vacancy panel from Q4 tract DBFs."""

from __future__ import annotations

import csv
import re
import struct
from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path


ROOT = Path("/Users/brendynbeasley/Desktop/mn_climate_project")
RAW_DIR = ROOT / "raw" / "hud"
CLEAN_DIR = ROOT / "clean"

OUT_CSV = CLEAN_DIR / "mn_usps_vacancy_q4_county_2011_2023.csv"
OUT_README = CLEAN_DIR / "mn_usps_vacancy_q4_county_2011_2023_README.txt"

YEAR_RE = re.compile(r"12(20\d{2}|201\d)")
TARGET_YEARS = list(range(2011, 2024))
MINNESOTA_STATE_FIPS = "27"


@dataclass(frozen=True)
class DbfField:
    name: str
    field_type: str
    length: int
    decimals: int


def extract_year(path: Path) -> int | None:
    match = YEAR_RE.search(path.name.lower())
    return int(match.group(1)) if match else None


def load_county_names() -> dict[str, str]:
    path = CLEAN_DIR / "fema_mn_counties_clean.csv"
    county_names: dict[str, str] = {}
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            county_fips = (row.get("county_fips") or "").strip()
            county_name = (row.get("county_name") or "").strip()
            if county_fips:
                county_names[county_fips] = county_name
    return county_names


def read_dbf_header(path: Path) -> tuple[int, int, int, list[DbfField]]:
    with path.open("rb") as f:
        header = f.read(32)
        record_count = struct.unpack("<I", header[4:8])[0]
        header_length = struct.unpack("<H", header[8:10])[0]
        record_length = struct.unpack("<H", header[10:12])[0]
        field_count = (header_length - 33) // 32
        fields: list[DbfField] = []

        for _ in range(field_count):
            desc = f.read(32)
            name = desc[:11].split(b"\x00", 1)[0].decode("ascii", "ignore").lower()
            field_type = chr(desc[11])
            length = desc[16]
            decimals = desc[17]
            fields.append(DbfField(name, field_type, length, decimals))

    return record_count, header_length, record_length, fields


def parse_record(raw: bytes, fields: list[DbfField]) -> dict[str, str]:
    pos = 1
    out: dict[str, str] = {}
    for field in fields:
        cell = raw[pos : pos + field.length]
        pos += field.length
        out[field.name] = cell.decode("latin1", "ignore").strip()
    return out


def iter_dbf_records(path: Path) -> tuple[int, list[dict[str, str]]]:
    record_count, header_length, record_length, fields = read_dbf_header(path)
    records: list[dict[str, str]] = []

    with path.open("rb") as f:
        f.seek(header_length)
        while True:
            raw = f.read(record_length)
            if not raw:
                break
            if raw[0:1] == b"*":
                continue
            records.append(parse_record(raw, fields))

    return record_count, records


def parse_int(value: str | None) -> int:
    text = "" if value is None else value.strip()
    if not text:
        return 0
    try:
        return int(Decimal(text))
    except (InvalidOperation, ValueError):
        return 0


def tract_standard_for_year(year: int) -> str:
    return "2020" if year >= 2023 else "2010"


def rate(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return ""
    return f"{numerator / denominator:.8f}"


def format_float(value: float) -> str:
    return f"{value:.8f}"


def format_stat(values: list[float]) -> str:
    if not values:
        return "n=0"
    ordered = sorted(values)
    n = len(ordered)

    def pct(p: float) -> float:
        idx = (n - 1) * p
        lower = int(idx)
        upper = min(lower + 1, n - 1)
        weight = idx - lower
        return ordered[lower] * (1 - weight) + ordered[upper] * weight

    return (
        f"n={n}, mean={sum(ordered) / n:.6f}, min={ordered[0]:.6f}, "
        f"p25={pct(0.25):.6f}, median={pct(0.50):.6f}, "
        f"p75={pct(0.75):.6f}, max={ordered[-1]:.6f}"
    )


def main() -> None:
    county_names = load_county_names()
    dbf_files = []
    for path in sorted(RAW_DIR.glob("*.dbf")):
        year = extract_year(path)
        if year in TARGET_YEARS:
            dbf_files.append((year, path))

    found_years = sorted(year for year, _ in dbf_files)
    missing_years = [year for year in TARGET_YEARS if year not in found_years]
    if missing_years:
        raise ValueError(f"Missing Q4 HUD USPS files for years: {missing_years}")

    county_year: dict[tuple[str, int], dict[str, int | str]] = {}
    tract_rows_by_year: dict[int, int] = defaultdict(int)
    statewide_totals: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    dbf_record_counts: dict[int, int] = {}

    for year, path in dbf_files:
        record_count, records = iter_dbf_records(path)
        dbf_record_counts[year] = record_count

        for record in records:
            geoid = (record.get("geoid") or "").strip()
            if len(geoid) != 11 or not geoid.startswith(MINNESOTA_STATE_FIPS):
                continue

            county_fips = geoid[:5]
            tract_rows_by_year[year] += 1

            res_addr = parse_int(record.get("ams_res"))
            bus_addr = parse_int(record.get("ams_bus"))
            oth_addr = parse_int(record.get("ams_oth"))
            res_vac = parse_int(record.get("res_vac"))
            bus_vac = parse_int(record.get("bus_vac"))
            oth_vac = parse_int(record.get("oth_vac"))
            res_nostat = parse_int(record.get("nostat_res"))
            bus_nostat = parse_int(record.get("nostat_bus"))
            oth_nostat = parse_int(record.get("nostat_oth"))

            total_addr = res_addr + bus_addr + oth_addr
            vacant_addr = res_vac + bus_vac + oth_vac
            nostat_addr = res_nostat + bus_nostat + oth_nostat

            key = (county_fips, year)
            row = county_year.setdefault(
                key,
                {
                    "county_fips": county_fips,
                    "county_name": county_names.get(county_fips, ""),
                    "year": year,
                    "quarter": 4,
                    "tract_standard": tract_standard_for_year(year),
                    "tract_rows": 0,
                    "usps_total_addr": 0,
                    "usps_vacant_addr": 0,
                    "usps_nostat_addr": 0,
                    "usps_res_addr": 0,
                    "usps_res_vacant_addr": 0,
                    "usps_res_nostat_addr": 0,
                },
            )

            row["tract_rows"] = int(row["tract_rows"]) + 1
            row["usps_total_addr"] = int(row["usps_total_addr"]) + total_addr
            row["usps_vacant_addr"] = int(row["usps_vacant_addr"]) + vacant_addr
            row["usps_nostat_addr"] = int(row["usps_nostat_addr"]) + nostat_addr
            row["usps_res_addr"] = int(row["usps_res_addr"]) + res_addr
            row["usps_res_vacant_addr"] = int(row["usps_res_vacant_addr"]) + res_vac
            row["usps_res_nostat_addr"] = int(row["usps_res_nostat_addr"]) + res_nostat

            statewide_totals[year]["usps_total_addr"] += total_addr
            statewide_totals[year]["usps_vacant_addr"] += vacant_addr
            statewide_totals[year]["usps_nostat_addr"] += nostat_addr
            statewide_totals[year]["usps_res_addr"] += res_addr

    rows: list[dict[str, str]] = []
    for county_fips, year in sorted(county_year, key=lambda x: (x[0], x[1])):
        row = county_year[(county_fips, year)]
        total_addr = int(row["usps_total_addr"])
        vacant_addr = int(row["usps_vacant_addr"])
        nostat_addr = int(row["usps_nostat_addr"])
        res_addr = int(row["usps_res_addr"])
        res_vac = int(row["usps_res_vacant_addr"])
        res_nostat = int(row["usps_res_nostat_addr"])

        rows.append(
            {
                "county_fips": str(row["county_fips"]),
                "county_name": str(row["county_name"]),
                "year": str(row["year"]),
                "quarter": str(row["quarter"]),
                "tract_standard": str(row["tract_standard"]),
                "tract_rows": str(row["tract_rows"]),
                "usps_total_addr": str(total_addr),
                "usps_vacant_addr": str(vacant_addr),
                "usps_nostat_addr": str(nostat_addr),
                "usps_res_addr": str(res_addr),
                "usps_res_vacant_addr": str(res_vac),
                "usps_res_nostat_addr": str(res_nostat),
                "usps_vacancy_rate": rate(vacant_addr, total_addr),
                "usps_nostat_rate": rate(nostat_addr, total_addr),
                "usps_res_vacancy_rate": rate(res_vac, res_addr),
                "usps_res_nostat_rate": rate(res_nostat, res_addr),
            }
        )

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "county_fips",
        "county_name",
        "year",
        "quarter",
        "tract_standard",
        "tract_rows",
        "usps_total_addr",
        "usps_vacant_addr",
        "usps_nostat_addr",
        "usps_res_addr",
        "usps_res_vacant_addr",
        "usps_res_nostat_addr",
        "usps_vacancy_rate",
        "usps_nostat_rate",
        "usps_res_vacancy_rate",
        "usps_res_nostat_rate",
    ]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    year_counts = defaultdict(int)
    for row in rows:
        year_counts[int(row["year"])] += 1

    vacancy_rates = [float(row["usps_vacancy_rate"]) for row in rows if row["usps_vacancy_rate"]]
    nostat_rates = [float(row["usps_nostat_rate"]) for row in rows if row["usps_nostat_rate"]]
    res_vacancy_rates = [
        float(row["usps_res_vacancy_rate"]) for row in rows if row["usps_res_vacancy_rate"]
    ]
    res_nostat_rates = [
        float(row["usps_res_nostat_rate"]) for row in rows if row["usps_res_nostat_rate"]
    ]

    statewide_total_2011 = statewide_totals[2011]["usps_total_addr"]
    statewide_total_2012 = statewide_totals[2012]["usps_total_addr"]
    statewide_total_2022 = statewide_totals[2022]["usps_total_addr"]
    statewide_total_2023 = statewide_totals[2023]["usps_total_addr"]

    change_2011_2012 = (
        ((statewide_total_2012 / statewide_total_2011) - 1) * 100 if statewide_total_2011 else 0.0
    )
    change_2022_2023 = (
        ((statewide_total_2023 / statewide_total_2022) - 1) * 100 if statewide_total_2022 else 0.0
    )

    statewide_vacancy = {}
    for year in TARGET_YEARS:
        total_addr = statewide_totals[year]["usps_total_addr"]
        vacant_addr = statewide_totals[year]["usps_vacant_addr"]
        nostat_addr = statewide_totals[year]["usps_nostat_addr"]
        statewide_vacancy[year] = {
            "vacancy_rate": (vacant_addr / total_addr) if total_addr else 0.0,
            "nostat_rate": (nostat_addr / total_addr) if total_addr else 0.0,
        }

    with OUT_README.open("w", encoding="utf-8") as f:
        f.write("Minnesota HUD USPS Vacancy Panel (Q4 only)\n")
        f.write("=========================================\n\n")
        f.write(f"Source directory: {RAW_DIR}\n")
        f.write("Raw files used: HUD USPS tract summary DBFs for Q4 of each year, 2011-2023\n")
        f.write("Auxiliary files inspected: 2018-USPS-FAQ.pdf and USPS_Data_Dictionary_07212008.pdf\n\n")
        f.write("Build approach\n")
        f.write("--------------\n")
        f.write("- Each raw Q4 tract DBF was filtered to Minnesota using tract GEOID starting with state FIPS 27.\n")
        f.write("- County FIPS were derived as the first 5 digits of tract GEOID.\n")
        f.write("- Tract rows were aggregated directly to county-year by summing tract-level address counts.\n")
        f.write("- No tract harmonization was attempted because the target output is county-year, not tract panel.\n")
        f.write("- The file uses Q4 only, so each row is a county-year snapshot rather than an annual average.\n\n")
        f.write("Variables used\n")
        f.write("--------------\n")
        f.write("- GEOID / geoid: tract identifier\n")
        f.write("- AMS_RES, AMS_BUS, AMS_OTH: active address counts by type\n")
        f.write("- RES_VAC, BUS_VAC, OTH_VAC: vacant counts by type\n")
        f.write("- NOSTAT_RES, NOSTAT_BUS, NOSTAT_OTH: no-stat counts by type\n\n")
        f.write("Output variables\n")
        f.write("----------------\n")
        f.write("- county_fips, county_name, year, quarter, tract_standard, tract_rows\n")
        f.write("- usps_total_addr = AMS_RES + AMS_BUS + AMS_OTH\n")
        f.write("- usps_vacant_addr = RES_VAC + BUS_VAC + OTH_VAC\n")
        f.write("- usps_nostat_addr = NOSTAT_RES + NOSTAT_BUS + NOSTAT_OTH\n")
        f.write("- usps_res_addr = AMS_RES\n")
        f.write("- usps_res_vacant_addr = RES_VAC\n")
        f.write("- usps_res_nostat_addr = NOSTAT_RES\n")
        f.write("- usps_vacancy_rate = usps_vacant_addr / usps_total_addr\n")
        f.write("- usps_nostat_rate = usps_nostat_addr / usps_total_addr\n")
        f.write("- usps_res_vacancy_rate = usps_res_vacant_addr / usps_res_addr\n")
        f.write("- usps_res_nostat_rate = usps_res_nostat_addr / usps_res_addr\n\n")
        f.write("Rate denominator note\n")
        f.write("---------------------\n")
        f.write(
            "- Overall vacancy and no-stat rates use total addresses because the tract files contain residential, "
            "business, and other address counts.\n"
        )
        f.write(
            "- Residential-specific rates are also included for housing-focused analysis where AMS_RES is the more "
            "appropriate denominator.\n\n"
        )
        f.write("Known limitations / caveats\n")
        f.write("---------------------------\n")
        f.write(
            "- HUD USPS data are tract-level snapshots derived from USPS administrative records, not a designed "
            "housing survey.\n"
        )
        f.write(
            "- HUD FAQ documentation warns that longitudinal analysis is harder because USPS address management "
            "practices changed over time, including the Move to Competitive change that affected addresses around "
            "2011-2012.\n"
        )
        f.write(
            "- Tract geography changes over time. Per project guidance, 2010 tracts apply through 2022 and 2020 "
            "tracts begin in 2023 Q1 and later.\n"
        )
        f.write(
            "- Because the panel is aggregated to county-year, tract-boundary changes are not harmonized beyond "
            "county aggregation.\n\n"
        )
        f.write("Diagnostics\n")
        f.write("-----------\n")
        f.write(f"Rows written: {len(rows)}\n")
        f.write(f"Unique county-year rows: {len({(r['county_fips'], r['year']) for r in rows})}\n")
        f.write(f"Unique counties: {len({r['county_fips'] for r in rows})}\n\n")
        f.write("Row counts by year and Minnesota county coverage:\n")
        for year in TARGET_YEARS:
            f.write(
                f"- {year}: county rows={year_counts[year]}, tract rows={tract_rows_by_year[year]}, "
                f"raw dbf records={dbf_record_counts[year]}\n"
            )
        f.write("\nSummary stats:\n")
        f.write(f"- usps_vacancy_rate: {format_stat(vacancy_rates)}\n")
        f.write(f"- usps_nostat_rate: {format_stat(nostat_rates)}\n")
        f.write(f"- usps_res_vacancy_rate: {format_stat(res_vacancy_rates)}\n")
        f.write(f"- usps_res_nostat_rate: {format_stat(res_nostat_rates)}\n\n")
        f.write("Potential break checks:\n")
        f.write(
            f"- Statewide total addresses, 2011 to 2012: {statewide_total_2011} -> {statewide_total_2012} "
            f"({change_2011_2012:.2f}% change)\n"
        )
        f.write(
            f"- Statewide total addresses, 2022 to 2023: {statewide_total_2022} -> {statewide_total_2023} "
            f"({change_2022_2023:.2f}% change)\n"
        )
        f.write(
            f"- Statewide vacancy rate, 2011: {format_float(statewide_vacancy[2011]['vacancy_rate'])}; "
            f"2012: {format_float(statewide_vacancy[2012]['vacancy_rate'])}\n"
        )
        f.write(
            f"- Statewide vacancy rate, 2022: {format_float(statewide_vacancy[2022]['vacancy_rate'])}; "
            f"2023: {format_float(statewide_vacancy[2023]['vacancy_rate'])}\n"
        )

    print(f"Wrote {len(rows):,} rows to {OUT_CSV}")
    print(f"Wrote notes to {OUT_README}")
    for year in TARGET_YEARS:
        print(
            f"{year}: counties={year_counts[year]}, tract_rows={tract_rows_by_year[year]}, "
            f"statewide_total_addr={statewide_totals[year]['usps_total_addr']}"
        )
    print(
        "Break checks: "
        f"2011->2012 total addr {change_2011_2012:.2f}%, "
        f"2022->2023 total addr {change_2022_2023:.2f}%"
    )


if __name__ == "__main__":
    main()
