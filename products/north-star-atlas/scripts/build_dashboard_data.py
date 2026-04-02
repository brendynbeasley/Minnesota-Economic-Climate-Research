#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


PRODUCT_DIR = Path(__file__).resolve().parents[1]
ROOT = PRODUCT_DIR.parents[1]
DATA_DIR = PRODUCT_DIR / "data"


def load_frame(path: Path, *, stata: bool = False) -> pd.DataFrame:
    if stata:
        df = pd.read_stata(path, convert_categoricals=False)
    else:
        df = pd.read_csv(path)

    if "county_fips" in df.columns:
        df["county_fips"] = pd.to_numeric(df["county_fips"], errors="coerce").astype("Int64")
    if "year" in df.columns:
        df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def zscore(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    std = series.std(ddof=0)
    if pd.isna(std) or std == 0:
        return pd.Series(0.0, index=series.index)
    return (series - series.mean()) / std


def minmax_0_100(series: pd.Series) -> pd.Series:
    series = pd.to_numeric(series, errors="coerce")
    lo = series.min()
    hi = series.max()
    if pd.isna(lo) or pd.isna(hi) or hi == lo:
        return pd.Series(50.0, index=series.index)
    return ((series - lo) / (hi - lo) * 100).round(1)


def first_valid(series: pd.Series):
    non_null = series.dropna()
    return None if non_null.empty else non_null.iloc[0]


def maybe_number(value):
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    return value


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    panel = load_frame(ROOT / "clean" / "mn_panel_with_unemployment_qcew.dta", stata=True)
    bps = load_frame(ROOT / "clean" / "bps_mn_county_year_2011_2024.csv")
    cbp = load_frame(ROOT / "clean" / "cbp_mn_county_year_2011_2023_construction.csv")
    usps = load_frame(ROOT / "clean" / "mn_usps_vacancy_q4_county_2011_2023.csv")
    bea = load_frame(ROOT / "clean" / "bea_mn_county_year_2011_2024.csv")

    keep_bps = [
        "county_fips",
        "year",
        "bps_total_units",
        "bps_total_value",
        "bps_units_1_unit",
    ]
    keep_cbp = [
        "county_fips",
        "year",
        "cbp_const_emp",
        "cbp_const_q1_payroll",
        "cbp_const_annual_payroll",
        "cbp_const_establishments",
    ]
    keep_usps = [
        "county_fips",
        "year",
        "usps_vacancy_rate",
        "usps_nostat_rate",
        "usps_res_vacancy_rate",
        "usps_res_nostat_rate",
        "usps_total_addr",
        "usps_vacant_addr",
        "usps_res_addr",
        "usps_res_vacant_addr",
    ]
    keep_bea = [
        "county_fips",
        "year",
        "bea_personal_income",
        "bea_population",
        "bea_pc_income",
    ]

    panel = panel.merge(bps[keep_bps], on=["county_fips", "year"], how="left")
    panel = panel.merge(cbp[keep_cbp], on=["county_fips", "year"], how="left")
    panel = panel.merge(usps[keep_usps], on=["county_fips", "year"], how="left")
    panel = panel.merge(bea[keep_bea], on=["county_fips", "year"], how="left")

    numeric_cols = [
        "temp_avg",
        "precip_total",
        "pop_total",
        "pop_growth_rate",
        "risk_score",
        "inland_flood_risk_score",
        "resl_score",
        "net_migration_exemptions",
        "unemp_rate",
        "qcew_employment",
        "qcew_avg_wkly_wage",
        "qcew_total_wages",
        "bps_total_units",
        "bps_total_value",
        "bps_units_1_unit",
        "cbp_const_emp",
        "cbp_const_establishments",
        "cbp_const_annual_payroll",
        "usps_vacancy_rate",
        "usps_nostat_rate",
        "usps_res_vacancy_rate",
        "usps_res_nostat_rate",
        "bea_personal_income",
        "bea_population",
        "bea_pc_income",
    ]
    for col in numeric_cols:
        if col in panel.columns:
            panel[col] = pd.to_numeric(panel[col], errors="coerce")

    panel["county_fips"] = panel["county_fips"].astype(int)
    panel["year"] = panel["year"].astype(int)
    panel["fips"] = panel["county_fips"].map(lambda x: f"{int(x):05d}")
    panel["county_name"] = panel["county_name"].fillna(panel.get("county_name_census"))
    panel["county_name"] = panel["county_name"].fillna(panel.get("county_name_bps"))
    panel["county_name"] = panel["county_name"].fillna(panel.get("county_name_bea"))
    panel["county_name"] = panel["county_name"].fillna(panel.get("county_name_fema"))
    panel["county_name"] = panel["county_name"].astype(str).str.replace(" County", "", regex=False)

    panel["net_migration_rate"] = 1000 * panel["net_migration_exemptions"] / panel["pop_total"]
    panel["qcew_employment_per_1000"] = 1000 * panel["qcew_employment"] / panel["pop_total"]
    panel["bps_units_per_1000"] = 1000 * panel["bps_total_units"] / panel["pop_total"]
    panel["bps_single_family_units_per_1000"] = 1000 * panel["bps_units_1_unit"] / panel["pop_total"]
    panel["cbp_const_estabs_per_10k"] = 10000 * panel["cbp_const_establishments"] / panel["pop_total"]
    panel["cbp_const_emp_per_1000"] = 1000 * panel["cbp_const_emp"] / panel["pop_total"]
    panel["usps_vacancy_pct"] = 100 * panel["usps_vacancy_rate"]
    panel["usps_res_vacancy_pct"] = 100 * panel["usps_res_vacancy_rate"]
    panel["usps_nostat_pct"] = 100 * panel["usps_nostat_rate"]
    panel["usps_res_nostat_pct"] = 100 * panel["usps_res_nostat_rate"]

    latest_year = int(panel["year"].max())

    avg = (
        panel.groupby(["county_fips", "fips", "county_name"], as_index=False)
        .agg(
            avg_temp_avg=("temp_avg", "mean"),
            avg_precip_total=("precip_total", "mean"),
            avg_pop_growth_rate=("pop_growth_rate", "mean"),
            avg_net_migration_rate=("net_migration_rate", "mean"),
            avg_unemp_rate=("unemp_rate", "mean"),
            avg_bps_units_per_1000=("bps_units_per_1000", "mean"),
            avg_cbp_const_estabs_per_10k=("cbp_const_estabs_per_10k", "mean"),
            avg_usps_res_vacancy_pct=("usps_res_vacancy_pct", "mean"),
            avg_qcew_employment_per_1000=("qcew_employment_per_1000", "mean"),
            avg_bea_pc_income=("bea_pc_income", "mean"),
            risk_score=("risk_score", first_valid),
            inland_flood_risk_score=("inland_flood_risk_score", first_valid),
            resl_score=("resl_score", first_valid),
        )
    )

    avg["exposure_raw"] = (
        zscore(avg["avg_precip_total"])
        + zscore(avg["risk_score"])
        + zscore(avg["inland_flood_risk_score"])
    ) / 3
    avg["economic_pressure_raw"] = (
        zscore(-avg["avg_pop_growth_rate"])
        + zscore(-avg["avg_net_migration_rate"])
        + zscore(avg["avg_unemp_rate"])
    ) / 3
    avg["housing_headwind_raw"] = (
        zscore(-avg["avg_bps_units_per_1000"])
        + zscore(-avg["avg_cbp_const_estabs_per_10k"])
        + zscore(avg["avg_usps_res_vacancy_pct"])
    ) / 3
    avg["overall_signal_raw"] = (
        avg["exposure_raw"] + avg["economic_pressure_raw"] + avg["housing_headwind_raw"]
    ) / 3

    for raw, scaled in [
        ("exposure_raw", "exposure_score"),
        ("economic_pressure_raw", "economic_pressure_score"),
        ("housing_headwind_raw", "housing_headwind_score"),
        ("overall_signal_raw", "overall_signal_score"),
    ]:
        avg[scaled] = minmax_0_100(avg[raw]).round(1)

    latest = (
        panel.loc[panel["year"] == latest_year]
        .copy()
        .sort_values(["county_fips", "year"])
        .drop_duplicates("county_fips", keep="last")
    )

    summary = avg.merge(
        latest[
            [
                "county_fips",
                "pop_total",
                "temp_avg",
                "precip_total",
                "pop_growth_rate",
                "net_migration_rate",
                "unemp_rate",
                "qcew_employment_per_1000",
                "qcew_avg_wkly_wage",
                "bea_pc_income",
                "bps_units_per_1000",
                "bps_single_family_units_per_1000",
                "cbp_const_estabs_per_10k",
                "cbp_const_emp_per_1000",
                "usps_vacancy_pct",
                "usps_res_vacancy_pct",
            ]
        ],
        on="county_fips",
        how="left",
        suffixes=("", "_latest"),
    )

    state_series = (
        panel.groupby("year", as_index=False)
        .agg(
            temp_avg=("temp_avg", "mean"),
            precip_total=("precip_total", "mean"),
            pop_growth_rate=("pop_growth_rate", "mean"),
            net_migration_rate=("net_migration_rate", "mean"),
            unemp_rate=("unemp_rate", "mean"),
            qcew_employment_per_1000=("qcew_employment_per_1000", "mean"),
            qcew_avg_wkly_wage=("qcew_avg_wkly_wage", "mean"),
            bea_pc_income=("bea_pc_income", "mean"),
            bps_units_per_1000=("bps_units_per_1000", "mean"),
            cbp_const_estabs_per_10k=("cbp_const_estabs_per_10k", "mean"),
            usps_res_vacancy_pct=("usps_res_vacancy_pct", "mean"),
            usps_vacancy_pct=("usps_vacancy_pct", "mean"),
        )
        .sort_values("year")
    )

    county_series = {}
    for fips, group in panel.sort_values(["county_fips", "year"]).groupby("fips"):
        records = []
        for _, row in group.iterrows():
            records.append(
                {
                    "year": int(row["year"]),
                    "temp_avg": maybe_number(row["temp_avg"]),
                    "precip_total": maybe_number(row["precip_total"]),
                    "pop_growth_rate": maybe_number(row["pop_growth_rate"]),
                    "net_migration_rate": maybe_number(row["net_migration_rate"]),
                    "unemp_rate": maybe_number(row["unemp_rate"]),
                    "qcew_employment_per_1000": maybe_number(row["qcew_employment_per_1000"]),
                    "qcew_avg_wkly_wage": maybe_number(row["qcew_avg_wkly_wage"]),
                    "bea_pc_income": maybe_number(row["bea_pc_income"]),
                    "bps_units_per_1000": maybe_number(row["bps_units_per_1000"]),
                    "cbp_const_estabs_per_10k": maybe_number(row["cbp_const_estabs_per_10k"]),
                    "usps_res_vacancy_pct": maybe_number(row["usps_res_vacancy_pct"]),
                    "usps_vacancy_pct": maybe_number(row["usps_vacancy_pct"]),
                }
            )
        county_series[fips] = records

    county_list = []
    for _, row in summary.sort_values("county_name").iterrows():
        county_list.append(
            {
                "fips": row["fips"],
                "county_fips": int(row["county_fips"]),
                "county_name": row["county_name"],
                "latest_year": latest_year,
                "latest_population": maybe_number(row["pop_total"]),
                "risk_score": maybe_number(row["risk_score"]),
                "inland_flood_risk_score": maybe_number(row["inland_flood_risk_score"]),
                "resl_score": maybe_number(row["resl_score"]),
                "overall_signal_score": maybe_number(row["overall_signal_score"]),
                "exposure_score": maybe_number(row["exposure_score"]),
                "economic_pressure_score": maybe_number(row["economic_pressure_score"]),
                "housing_headwind_score": maybe_number(row["housing_headwind_score"]),
                "temp_avg": maybe_number(row["temp_avg"]),
                "precip_total": maybe_number(row["precip_total"]),
                "pop_growth_rate": maybe_number(row["pop_growth_rate"]),
                "net_migration_rate": maybe_number(row["net_migration_rate"]),
                "unemp_rate": maybe_number(row["unemp_rate"]),
                "qcew_employment_per_1000": maybe_number(row["qcew_employment_per_1000"]),
                "qcew_avg_wkly_wage": maybe_number(row["qcew_avg_wkly_wage"]),
                "bea_pc_income": maybe_number(row["bea_pc_income"]),
                "bps_units_per_1000": maybe_number(row["bps_units_per_1000"]),
                "bps_single_family_units_per_1000": maybe_number(row["bps_single_family_units_per_1000"]),
                "cbp_const_estabs_per_10k": maybe_number(row["cbp_const_estabs_per_10k"]),
                "cbp_const_emp_per_1000": maybe_number(row["cbp_const_emp_per_1000"]),
                "usps_vacancy_pct": maybe_number(row["usps_vacancy_pct"]),
                "usps_res_vacancy_pct": maybe_number(row["usps_res_vacancy_pct"]),
                "avg_temp_avg": maybe_number(row["avg_temp_avg"]),
                "avg_precip_total": maybe_number(row["avg_precip_total"]),
                "avg_pop_growth_rate": maybe_number(row["avg_pop_growth_rate"]),
                "avg_net_migration_rate": maybe_number(row["avg_net_migration_rate"]),
                "avg_unemp_rate": maybe_number(row["avg_unemp_rate"]),
                "avg_bps_units_per_1000": maybe_number(row["avg_bps_units_per_1000"]),
                "avg_cbp_const_estabs_per_10k": maybe_number(row["avg_cbp_const_estabs_per_10k"]),
                "avg_usps_res_vacancy_pct": maybe_number(row["avg_usps_res_vacancy_pct"]),
                "avg_qcew_employment_per_1000": maybe_number(row["avg_qcew_employment_per_1000"]),
                "avg_bea_pc_income": maybe_number(row["avg_bea_pc_income"]),
            }
        )

    payload = {
        "metadata": {
            "title": "North Star Atlas",
            "subtitle": "Minnesota county climate risk and economic pressure dashboard",
            "latest_year": latest_year,
            "years": sorted(panel["year"].dropna().astype(int).unique().tolist()),
            "created_from": [
                "mn_panel_with_unemployment_qcew.dta",
                "bps_mn_county_year_2011_2024.csv",
                "cbp_mn_county_year_2011_2023_construction.csv",
                "mn_usps_vacancy_q4_county_2011_2023.csv",
                "bea_mn_county_year_2011_2024.csv",
            ],
            "method_note": "Composite scores are exploratory county comparisons built from the project’s strongest signals: precipitation exposure, official flood risk, migration pressure, unemployment, building permits, construction establishments, and USPS residential vacancy.",
        },
        "statewide": [
            {
                "year": int(row["year"]),
                "temp_avg": maybe_number(row["temp_avg"]),
                "precip_total": maybe_number(row["precip_total"]),
                "pop_growth_rate": maybe_number(row["pop_growth_rate"]),
                "net_migration_rate": maybe_number(row["net_migration_rate"]),
                "unemp_rate": maybe_number(row["unemp_rate"]),
                "qcew_employment_per_1000": maybe_number(row["qcew_employment_per_1000"]),
                "qcew_avg_wkly_wage": maybe_number(row["qcew_avg_wkly_wage"]),
                "bea_pc_income": maybe_number(row["bea_pc_income"]),
                "bps_units_per_1000": maybe_number(row["bps_units_per_1000"]),
                "cbp_const_estabs_per_10k": maybe_number(row["cbp_const_estabs_per_10k"]),
                "usps_res_vacancy_pct": maybe_number(row["usps_res_vacancy_pct"]),
                "usps_vacancy_pct": maybe_number(row["usps_vacancy_pct"]),
            }
            for _, row in state_series.iterrows()
        ],
        "counties": county_list,
        "series": county_series,
    }

    geojson = json.loads((DATA_DIR / "mn_counties.geojson").read_text())

    (DATA_DIR / "dashboard-data.js").write_text(
        "window.NORTH_STAR_ATLAS = " + json.dumps(payload, separators=(",", ":")) + ";\n"
    )
    (DATA_DIR / "mn-counties.js").write_text(
        "window.MN_COUNTIES_GEOJSON = " + json.dumps(geojson, separators=(",", ":")) + ";\n"
    )


if __name__ == "__main__":
    main()
