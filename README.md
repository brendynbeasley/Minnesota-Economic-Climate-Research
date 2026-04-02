# Minnesota Climate Project

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.19381049.svg)](https://doi.org/10.5281/zenodo.19381049)

County-year research project on repeated wet years, flood exposure, housing activity, agricultural productivity, and local economic adjustment in Minnesota.

> Headline result: using annual Minnesota county data and fixed-effects models, this project finds that repeated wet years are most clearly associated with fewer permit units, lower construction GDP, and lower corn and soybean yields.

## Table of Contents

- [Overview](#overview)
- [Why Minnesota](#why-minnesota)
- [Project Objectives](#project-objectives)
- [Research Design](#research-design)
- [Key Findings](#key-findings)
- [Data Sources](#data-sources)
- [Results and Visuals](#results-and-visuals)
- [How To Use This Repository](#how-to-use-this-repository)
- [Repository Layout](#repository-layout)
- [Acknowledgments](#acknowledgments)
- [Future Work](#future-work)
- [Citation and Data Access](#citation-and-data-access)

## Overview

This repository studies how annual weather variation relates to local economic adjustment in Minnesota. It combines NOAA weather data with county-level demographic, labor, housing, income, agricultural, and risk datasets to build a panel covering Minnesota counties over time.

The project is designed to answer a practical research question:

- How do repeated wet years, especially high-precipitation county-years, relate to local economic outcomes?
- Are higher-risk counties more sensitive to those weather pressures?
- Which outcomes show the clearest signal: construction, sectoral output, agriculture, labor, or migration?

This repository contains the cleaned datasets, build scripts, Stata workflows, research outputs, and a standalone interactive dashboard that communicates the results visually.

## Why Minnesota

Minnesota is a useful setting for studying repeated wet years and local economic activity because it combines:

- substantial year-to-year variation in precipitation and temperature
- meaningful flood exposure across counties
- a mix of urban, suburban, and rural local economies
- observable adjustment margins in migration, housing, labor markets, and income

That combination makes it possible to study not just whether climate matters, but how local economies adjust when climate stress increases.

## Project Objectives

The project has four main goals:

- build a reproducible Minnesota county-year panel that combines weather, risk, labor, housing, output, and agricultural data
- estimate within-county relationships between weather variables and local economic outcomes using fixed-effects models
- test whether flood risk amplifies weather-related economic pressure
- communicate the findings in a way that is useful both for research and for public-facing interpretation

## Research Design

### Unit of Analysis

- Minnesota county-year panel
- 87 counties
- main analysis window centered on 2011-2023, with some extensions depending on source coverage

### Core Methodology

- county fixed effects
- year fixed effects
- standard errors clustered by county
- contemporaneous, lagged, and moving-average climate specifications
- heterogeneity tests using FEMA risk and inland flood risk measures

### Main Outcome Families

- population growth and migration
- unemployment and employment
- construction and housing activity
- wages and broader income
- supplementary housing occupancy/distress measures

## Key Findings

### Main Conclusion

**Precipitation is the most consistent adverse weather margin in the Minnesota data.** The strongest and most stable evidence is concentrated in building permits, construction GDP, and corn and soybean yields.

### Housing and Construction

- Census Building Permits Survey results show fewer permit units in wetter county-years
- BEA county GDP results show lower construction-sector GDP in wetter county-years
- County Business Patterns show fewer construction establishments in wetter county-years, though this margin is less stable than permits

Interpretation:
**the clearest adjustment margin in the project is weaker local building activity and a thinner construction base.**

### Agriculture

- NASS crop results show lower corn and soybean yields in wetter county-years
- the negative yield relationship persists in lagged and moving-average specifications
- planted acreage is much less responsive than yields

Interpretation:
**wet conditions show up more clearly as a productivity shock than as a broad withdrawal of planted land.**

### Labor Markets

- employment levels are lower in wetter county-years in baseline and weighted specifications
- the employment relationship weakens materially once county-specific trends are added
- QWI results show lower total-private hiring and higher construction separation rates in wetter county-years

Interpretation:
**labor-market evidence supports the broader story, but it is not as durable as the construction and crop-yield results.**

### Demography and Migration

- precipitation is negatively associated with county population growth
- precipitation is negatively associated with IRS-based net migration
- the migration mechanism appears to work more through **lower in-migration** than through large increases in out-migration

Interpretation:
**weather-related stress in Minnesota looks less like sudden abandonment and more like a gradual weakening of county attractiveness and momentum, though these demographic results are more fragile than the core construction and productivity findings.**

### Risk Heterogeneity

- the negative precipitation-employment relationship becomes stronger in counties with higher baseline flood risk
- the inland flood risk interaction is one of the clearest heterogeneity results in the project

Interpretation:
**flood exposure appears to amplify the labor-market consequences of precipitation.**

### Income

- BEA per capita income is lower in hotter county-years, especially in lagged and multi-year specifications
- total personal income is lower in counties and years with both higher temperature and more precipitation
- broader income measures are more climate-sensitive than payroll wages alone

### Wages

- wage levels are the least persuasive outcome family in the project
- temperature shows up in a limited way in wage growth, but wages do not carry the main story

Interpretation:
**climate-related adjustment is more visible in migration, employment, construction, and income than in average wages.**

### USPS Vacancy Data

- HUD-USPS vacancy measures are informative but should be treated as supplementary
- hotter county-years are associated with lower vacancy in baseline specifications, which likely reflects tighter housing markets rather than clear climate distress
- no-stat measures are somewhat more consistent with precipitation-related disruption, but they are also more administratively sensitive

Interpretation:
**USPS data add context, but they should not be the headline evidence.**

## Data Sources

The project uses multiple public data sources. NOAA climate data serve as the backbone of the panel.

| Source | Role in Project | Local Folder |
|---|---|---|
| NOAA climate data | backbone county-year temperature and precipitation measures | [raw/noaa](raw/noaa) |
| FEMA National Risk Index | county flood and hazard risk measures | [raw/fema](raw/fema) |
| Census population estimates | county population and growth | [raw/census](raw/census) |
| IRS migration data | inflow, outflow, and net migration | [raw/irs](raw/irs) |
| BLS LAUS | county unemployment rates | [raw/bls](raw/bls) |
| QCEW | county employment and wages | [raw/qcew_mn](raw/qcew_mn) |
| BEA CAINC1 income data | personal income and per capita income | [raw/bea](raw/bea) |
| Census Building Permits Survey | county permit counts and values | [raw/census_bps](raw/census_bps) |
| County Business Patterns | construction establishments and employment | [raw/census_cbp](raw/census_cbp) |
| HUD USPS vacancy files | vacancy and no-stat address measures | [raw/hud](raw/hud) |

## Results and Visuals

### Final Research Outputs

- Working paper: [docs/mn_climate_economy_submission_draft.pdf](docs/mn_climate_economy_submission_draft.pdf)
- Main Stata workflow: [code/stata/final_mn_climate_project.do](code/stata/final_mn_climate_project.do)
- Working-paper extensions: [code/stata/run_working_paper_extensions.do](code/stata/run_working_paper_extensions.do)

### Interactive Dashboard

- North Star Atlas: [products/north-star-atlas/index.html](products/north-star-atlas/index.html)

The dashboard is designed as a communication layer on top of the paper:

- map county patterns
- compare counties to statewide trends
- view research findings graphically
- connect formal regression results to the county-level data

### Selected Output Files

- Summary statistics: [output/tables/summary_statistics.xlsx](output/tables/summary_statistics.xlsx)
- Main regression workbook: [output/tables/regression_table.xlsx](output/tables/regression_table.xlsx)
- Employment table: [output/tables/table_emp.rtf](output/tables/table_emp.rtf)
- Heterogeneity table: [output/tables/table_heterogeneity.rtf](output/tables/table_heterogeneity.rtf)
- Migration mechanism table: [output/tables/stage3_migration_mechanism.rtf](output/tables/stage3_migration_mechanism.rtf)

### Example Figures

- [output/figures/avg_pop_growth_by_year.png](output/figures/avg_pop_growth_by_year.png)
- [output/figures/avg_irs_net_mig_rate_by_year.png](output/figures/avg_irs_net_mig_rate_by_year.png)
- [output/figures/county_mean_irs_net_mig_vs_precip_lfit.png](output/figures/county_mean_irs_net_mig_vs_precip_lfit.png)

## How To Use This Repository

### For Readers

If you want the fastest way to understand the project:

1. Read the paper in [docs/mn_climate_economy_submission_draft.pdf](docs/mn_climate_economy_submission_draft.pdf).
2. Open the dashboard in [products/north-star-atlas/index.html](products/north-star-atlas/index.html).
3. Review the key tables in [output/tables](output/tables).

### For Researchers

If you want to work directly with the data and code:

1. Start with the main panel in [clean/mn_county_panel_2011_2023_plus_irs.dta](clean/mn_county_panel_2011_2023_plus_irs.dta).
2. Use the labor-market extension panel in [clean/mn_panel_with_unemployment_qcew.dta](clean/mn_panel_with_unemployment_qcew.dta).
3. Run the main Stata workflow in [code/stata/final_mn_climate_project.do](code/stata/final_mn_climate_project.do).

### Canonical Clean Datasets

- Main climate + census + IRS panel: [clean/mn_county_panel_2011_2023_plus_irs.dta](clean/mn_county_panel_2011_2023_plus_irs.dta)
- QCEW county panel: [clean/qcew_mn_county_year_2011_2024.dta](clean/qcew_mn_county_year_2011_2024.dta)
- Unemployment + QCEW extension: [clean/mn_panel_with_unemployment_qcew.dta](clean/mn_panel_with_unemployment_qcew.dta)
- BEA income extension: [clean/bea_mn_county_year_2011_2024.dta](clean/bea_mn_county_year_2011_2024.dta)
- BPS extension: [clean/bps_mn_county_year_2011_2024.dta](clean/bps_mn_county_year_2011_2024.dta)
- CBP construction extension: [clean/cbp_mn_county_year_2011_2023_construction.dta](clean/cbp_mn_county_year_2011_2023_construction.dta)
- USPS vacancy extension: [clean/mn_usps_vacancy_q4_county_2011_2023.dta](clean/mn_usps_vacancy_q4_county_2011_2023.dta)

## Repository Layout

- [raw](raw): downloaded source files organized by provider
- [clean](clean): cleaned and merge-ready datasets
- [code/python](code/python): Python data-cleaning and panel-building scripts
- [code/stata](code/stata): Stata import, build, and regression workflows
- [output](output): tables, figures, and logs
- [docs](docs): manuscript and paper files
- [products](products): dashboards and communication products
- [archive](archive): older or legacy files moved out of the main working tree

## GitHub Upload Notes

- This project includes large raw-data folders and local machine artifacts that are not appropriate for a standard GitHub repo.
- The repository `.gitignore` excludes `raw/`, `raw.zip`, local virtual environments, logs, and LaTeX build files so the upload stays lightweight and GitHub-safe.
- The research-facing materials to keep under version control are primarily `code/`, `docs/`, `output/figures/`, `output/tables/`, `products/`, selected `clean/` outputs, and this README.

## Acknowledgments

This project draws on public data made available by:

- NOAA
- FEMA
- U.S. Census Bureau
- IRS
- BLS
- BEA
- HUD

Project author:

- Brendyn Beasley

## Citation and Data Access

The Zenodo archive is the official project DOI for raw research materials:

- [Zenodo DOI: 10.5281/zenodo.19381049](https://doi.org/10.5281/zenodo.19381049)

Use the DOI link above to access the official archived research materials and raw data package associated with this project.
