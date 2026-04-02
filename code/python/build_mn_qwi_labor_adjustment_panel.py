from __future__ import annotations

import csv
import json
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "raw" / "census_qwi"
RAW_RESPONSES_DIR = RAW_DIR / "api_responses" / "sa_a05_u"
CLEAN_DIR = ROOT / "clean"

API_BASE = "https://api.census.gov/data/timeseries/qwi/sa"
YEARS = range(2011, 2024)
QUARTERS = range(1, 5)

INDUSTRIES = [
    {"slug": "total_private", "code": None, "label": "All private industries"},
    {"slug": "agriculture", "code": "11", "label": "Agriculture, forestry, fishing and hunting"},
    {"slug": "construction", "code": "23", "label": "Construction"},
    {"slug": "manufacturing", "code": "31-33", "label": "Manufacturing"},
    {"slug": "retail", "code": "44-45", "label": "Retail trade"},
    {"slug": "transport_warehousing", "code": "48-49", "label": "Transportation and warehousing"},
    {"slug": "health_social", "code": "62", "label": "Health care and social assistance"},
    {"slug": "accom_food", "code": "72", "label": "Accommodation and food services"},
]

GET_FIELDS = [
    "Emp",
    "sEmp",
    "HirA",
    "sHirA",
    "Sep",
    "sSep",
    "EarnS",
    "sEarnS",
    "FrmJbGn",
    "sFrmJbGn",
    "FrmJbLs",
    "sFrmJbLs",
]

QUARTER_FIELD_MAP = {
    "Emp": "qwi_emp",
    "sEmp": "qwi_emp_flag",
    "HirA": "qwi_hires",
    "sHirA": "qwi_hires_flag",
    "Sep": "qwi_separations",
    "sSep": "qwi_sep_flag",
    "EarnS": "qwi_earns",
    "sEarnS": "qwi_earns_flag",
    "FrmJbGn": "qwi_job_gains",
    "sFrmJbGn": "qwi_job_gains_flag",
    "FrmJbLs": "qwi_job_losses",
    "sFrmJbLs": "qwi_job_losses_flag",
}

ANNUAL_NUMERIC_RULES = {
    "qwi_emp": "mean",
    "qwi_hires": "sum",
    "qwi_separations": "sum",
    "qwi_earns": "mean",
    "qwi_job_gains": "sum",
    "qwi_job_losses": "sum",
}

ANNUAL_FLAG_FIELDS = [
    "qwi_emp_flag",
    "qwi_hires_flag",
    "qwi_sep_flag",
    "qwi_earns_flag",
    "qwi_job_gains_flag",
    "qwi_job_losses_flag",
]


def clean_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    return value.strip().replace('"', "")


def load_mn_county_names() -> Dict[int, str]:
    bea_path = ROOT / "raw" / "bea" / "CAGDP1" / "CAGDP1_MN_2001_2024.csv"
    names: Dict[int, str] = {}
    with bea_path.open(newline="", encoding="latin-1") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            geofips = clean_text(row.get("GeoFIPS", ""))
            geoname = clean_text(row.get("GeoName", ""))
            if len(geofips) == 5 and geofips.startswith("27") and geofips != "27000":
                names[int(geofips)] = geoname.replace(", MN", "")
    return dict(sorted(names.items()))


def parse_number(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    text = value.strip()
    if text == "" or text in {"N", "NA", "(D)"}:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def parse_flag(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = value.strip()
    return text or None


def query_qwi(params: Dict[str, str], retries: int = 3, pause: float = 0.15) -> List[List[str]]:
    url = API_BASE + "?" + urllib.parse.urlencode(params)
    last_error: Optional[Exception] = None
    for attempt in range(1, retries + 1):
        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                data = json.load(response)
            time.sleep(pause)
            return data
        except Exception as exc:  # pragma: no cover - network retries
            last_error = exc
            if attempt == retries:
                raise
            time.sleep(pause * attempt)
    raise RuntimeError(f"QWI request failed: {last_error}")


def save_raw_response(path: Path, url: str, data: List[List[str]]) -> None:
    payload = {"url": url, "header": data[0], "rows": data[1:]}
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)


def numeric_mean(values: Iterable[Optional[float]]) -> Optional[float]:
    usable = [v for v in values if v is not None]
    if not usable:
        return None
    return sum(usable) / len(usable)


def numeric_sum(values: Iterable[Optional[float]]) -> Optional[float]:
    usable = [v for v in values if v is not None]
    if not usable:
        return None
    return sum(usable)


def sorted_flag_codes(flags: Iterable[Optional[str]]) -> str:
    usable = sorted(
        {flag for flag in flags if flag is not None},
        key=lambda x: (0, int(x)) if x.lstrip("-").isdigit() else (1, x),
    )
    return "|".join(usable)


def flag_issue(flags: Iterable[Optional[str]]) -> Optional[int]:
    usable = [flag for flag in flags if flag is not None]
    if not usable:
        return None
    return int(any(flag != "1" for flag in usable))


def write_csv(path: Path, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_qwi_panels() -> None:
    county_names = load_mn_county_names()
    quarter_rows: List[Dict[str, object]] = []
    query_manifest: List[Dict[str, object]] = []

    for industry in INDUSTRIES:
        for year in YEARS:
            for quarter in QUARTERS:
                params = {
                    "get": ",".join(GET_FIELDS),
                    "for": "county:*",
                    "in": "state:27",
                    "year": str(year),
                    "quarter": str(quarter),
                    "ownercode": "A05",
                    "seasonadj": "U",
                }
                if industry["code"] is not None:
                    params["industry"] = industry["code"]

                url = API_BASE + "?" + urllib.parse.urlencode(params)
                data = query_qwi(params)

                raw_path = (
                    RAW_RESPONSES_DIR
                    / industry["slug"]
                    / f"qwi_sa_a05_u_{industry['slug']}_{year}_q{quarter}.json"
                )
                save_raw_response(raw_path, url, data)

                query_manifest.append(
                    {
                        "industry": industry["slug"],
                        "industry_code": industry["code"] or "TOTAL",
                        "year": year,
                        "quarter": quarter,
                        "url": url,
                        "rows_returned": len(data) - 1,
                        "raw_file": str(raw_path.relative_to(ROOT)),
                    }
                )

                header = data[0]
                for values in data[1:]:
                    record = dict(zip(header, values))
                    county_fips = int(f"27{record['county']}")
                    row = {
                        "county_fips": county_fips,
                        "county_name": county_names.get(county_fips, ""),
                        "year": year,
                        "quarter": quarter,
                        "industry_code": industry["code"] or "TOTAL",
                        "industry": industry["slug"],
                        "industry_label": industry["label"],
                        "ownercode": "A05",
                        "seasonadj": "U",
                    }
                    for source_name, dest_name in QUARTER_FIELD_MAP.items():
                        value = record.get(source_name)
                        if dest_name.endswith("_flag"):
                            row[dest_name] = parse_flag(value)
                        else:
                            row[dest_name] = parse_number(value)
                    quarter_rows.append(row)

    quarter_rows.sort(key=lambda r: (r["county_fips"], r["year"], r["quarter"], r["industry"]))

    quarter_fieldnames = [
        "county_fips",
        "county_name",
        "year",
        "quarter",
        "industry_code",
        "industry",
        "industry_label",
        "ownercode",
        "seasonadj",
        "qwi_emp",
        "qwi_emp_flag",
        "qwi_hires",
        "qwi_hires_flag",
        "qwi_separations",
        "qwi_sep_flag",
        "qwi_earns",
        "qwi_earns_flag",
        "qwi_job_gains",
        "qwi_job_gains_flag",
        "qwi_job_losses",
        "qwi_job_losses_flag",
    ]
    write_csv(CLEAN_DIR / "mn_qwi_county_quarter_2011_2023.csv", quarter_rows, quarter_fieldnames)
    write_csv(RAW_DIR / "qwi_query_manifest.csv", query_manifest, list(query_manifest[0].keys()))

    grouped: Dict[tuple, List[Dict[str, object]]] = defaultdict(list)
    for row in quarter_rows:
        grouped[(row["county_fips"], row["year"], row["industry"])].append(row)

    year_long_rows: List[Dict[str, object]] = []
    for (county_fips, year, industry_slug), rows in sorted(grouped.items()):
        first = rows[0]
        annual = {
            "county_fips": county_fips,
            "county_name": first["county_name"],
            "year": year,
            "industry_code": first["industry_code"],
            "industry": industry_slug,
            "industry_label": first["industry_label"],
            "ownercode": first["ownercode"],
            "seasonadj": first["seasonadj"],
            "quarters_observed": len(rows),
            "qwi_incomplete_year": int(len(rows) < 4),
        }

        for field, rule in ANNUAL_NUMERIC_RULES.items():
            values = [row[field] for row in rows]
            annual[field] = numeric_mean(values) if rule == "mean" else numeric_sum(values)

        for flag_field in ANNUAL_FLAG_FIELDS:
            flags = [row[flag_field] for row in rows]
            annual[f"{flag_field}_codes"] = sorted_flag_codes(flags)
            annual[f"{flag_field}_issue"] = flag_issue(flags)

        year_long_rows.append(annual)

    year_long_fieldnames = [
        "county_fips",
        "county_name",
        "year",
        "industry_code",
        "industry",
        "industry_label",
        "ownercode",
        "seasonadj",
        "quarters_observed",
        "qwi_incomplete_year",
        "qwi_emp",
        "qwi_hires",
        "qwi_separations",
        "qwi_earns",
        "qwi_job_gains",
        "qwi_job_losses",
        "qwi_emp_flag_codes",
        "qwi_emp_flag_issue",
        "qwi_hires_flag_codes",
        "qwi_hires_flag_issue",
        "qwi_sep_flag_codes",
        "qwi_sep_flag_issue",
        "qwi_earns_flag_codes",
        "qwi_earns_flag_issue",
        "qwi_job_gains_flag_codes",
        "qwi_job_gains_flag_issue",
        "qwi_job_losses_flag_codes",
        "qwi_job_losses_flag_issue",
    ]
    write_csv(CLEAN_DIR / "mn_qwi_county_year_2011_2023.csv", year_long_rows, year_long_fieldnames)

    all_county_years = []
    for county_fips, county_name in county_names.items():
        for year in YEARS:
            all_county_years.append(
                {"county_fips": county_fips, "county_name": county_name, "year": year}
            )

    annual_lookup = {
        (row["county_fips"], row["year"], row["industry"]): row for row in year_long_rows
    }

    wide_rows: List[Dict[str, object]] = []
    for base in all_county_years:
        row = dict(base)
        for industry in INDUSTRIES:
            suffix = industry["slug"]
            annual = annual_lookup.get((base["county_fips"], base["year"], suffix), {})
            row[f"qwi_emp_{suffix}"] = annual.get("qwi_emp")
            row[f"qwi_hires_{suffix}"] = annual.get("qwi_hires")
            row[f"qwi_separations_{suffix}"] = annual.get("qwi_separations")
            row[f"qwi_earns_{suffix}"] = annual.get("qwi_earns")
            row[f"qwi_job_gains_{suffix}"] = annual.get("qwi_job_gains")
            row[f"qwi_job_losses_{suffix}"] = annual.get("qwi_job_losses")
            row[f"qwi_emp_flag_issue_{suffix}"] = annual.get("qwi_emp_flag_issue")
            row[f"qwi_hires_flag_issue_{suffix}"] = annual.get("qwi_hires_flag_issue")
            row[f"qwi_sep_flag_issue_{suffix}"] = annual.get("qwi_sep_flag_issue")
            row[f"qwi_earns_flag_issue_{suffix}"] = annual.get("qwi_earns_flag_issue")
            row[f"qwi_job_gains_flag_issue_{suffix}"] = annual.get("qwi_job_gains_flag_issue")
            row[f"qwi_job_losses_flag_issue_{suffix}"] = annual.get("qwi_job_losses_flag_issue")
            row[f"qwi_quarters_observed_{suffix}"] = annual.get("quarters_observed")
            row[f"qwi_incomplete_year_{suffix}"] = annual.get("qwi_incomplete_year")
        wide_rows.append(row)

    wide_fieldnames = ["county_fips", "county_name", "year"]
    for industry in INDUSTRIES:
        suffix = industry["slug"]
        wide_fieldnames.extend(
            [
                f"qwi_emp_{suffix}",
                f"qwi_hires_{suffix}",
                f"qwi_separations_{suffix}",
                f"qwi_earns_{suffix}",
                f"qwi_job_gains_{suffix}",
                f"qwi_job_losses_{suffix}",
                f"qwi_emp_flag_issue_{suffix}",
                f"qwi_hires_flag_issue_{suffix}",
                f"qwi_sep_flag_issue_{suffix}",
                f"qwi_earns_flag_issue_{suffix}",
                f"qwi_job_gains_flag_issue_{suffix}",
                f"qwi_job_losses_flag_issue_{suffix}",
                f"qwi_quarters_observed_{suffix}",
                f"qwi_incomplete_year_{suffix}",
            ]
        )
    write_csv(CLEAN_DIR / "mn_qwi_county_year_2011_2023_wide.csv", wide_rows, wide_fieldnames)

    industry_counts = defaultdict(int)
    for row in quarter_rows:
        industry_counts[row["industry"]] += 1

    readme = f"""Minnesota QWI labor-market adjustment panel

Source
- U.S. Census Bureau Quarterly Workforce Indicators (QWI) API
- Endpoint used: /data/timeseries/qwi/sa
- Query geography: for=county:*&in=state:27

Build choices
- Ownership: A05 (all private employment)
- Seasonal adjustment: U (not seasonally adjusted)
- Time coverage: 2011 Q1 through 2023 Q4
- Worker detail: pulled from the sa endpoint without sex or age predicates so the baseline files reflect county totals rather than subgroup cells

Industries included
- total_private (no industry predicate; all private industries)
- agriculture (11)
- construction (23)
- manufacturing (31-33)
- retail (44-45)
- transport_warehousing (48-49)
- health_social (62)
- accom_food (72)

Indicators included
- Emp, HirA, Sep, EarnS
- FrmJbGn and FrmJbLs as optional job creation / destruction extensions
- Matching QWI status flags for every indicator

Annualization rules
- qwi_emp: average of quarterly Emp
- qwi_hires: sum of quarterly HirA
- qwi_separations: sum of quarterly Sep
- qwi_earns: average of quarterly EarnS
- qwi_job_gains: sum of quarterly FrmJbGn
- qwi_job_losses: sum of quarterly FrmJbLs

Flag handling
- County-quarter files preserve the raw quarterly QWI status flags
- County-year files keep pipe-separated quarterly flag codes and a *_flag_issue indicator that equals 1 if any observed quarter had a non-1 flag
- qwi_incomplete_year equals 1 when fewer than four quarterly observations were returned for a county-year-industry cell

Outputs
- raw/census_qwi/api_responses/sa_a05_u/... raw JSON API pulls
- raw/census_qwi/qwi_query_manifest.csv query manifest
- clean/mn_qwi_county_quarter_2011_2023.csv county-quarter long panel
- clean/mn_qwi_county_year_2011_2023.csv county-year long panel
- clean/mn_qwi_county_year_2011_2023_wide.csv county-year wide merge-ready panel

Diagnostics
- raw API files written: {len(query_manifest)}
- county-quarter rows: {len(quarter_rows)}
- county-year long rows: {len(year_long_rows)}
- county-year wide rows: {len(wide_rows)}
- counties in wide panel: {len(county_names)}
- quarter rows by industry:
{chr(10).join(f"  - {slug}: {count}" for slug, count in sorted(industry_counts.items()))}
"""
    (CLEAN_DIR / "mn_qwi_county_year_2011_2023_README.txt").write_text(readme, encoding="utf-8")


if __name__ == "__main__":
    build_qwi_panels()
