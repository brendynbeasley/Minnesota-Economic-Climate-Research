Minnesota HUD USPS Vacancy Panel (Q4 only)
=========================================

Source directory: /Users/brendynbeasley/Desktop/mn_climate_project/raw/hud
Raw files used: HUD USPS tract summary DBFs for Q4 of each year, 2011-2023
Auxiliary files inspected: 2018-USPS-FAQ.pdf and USPS_Data_Dictionary_07212008.pdf

Build approach
--------------
- Each raw Q4 tract DBF was filtered to Minnesota using tract GEOID starting with state FIPS 27.
- County FIPS were derived as the first 5 digits of tract GEOID.
- Tract rows were aggregated directly to county-year by summing tract-level address counts.
- No tract harmonization was attempted because the target output is county-year, not tract panel.
- The file uses Q4 only, so each row is a county-year snapshot rather than an annual average.

Variables used
--------------
- GEOID / geoid: tract identifier
- AMS_RES, AMS_BUS, AMS_OTH: active address counts by type
- RES_VAC, BUS_VAC, OTH_VAC: vacant counts by type
- NOSTAT_RES, NOSTAT_BUS, NOSTAT_OTH: no-stat counts by type

Output variables
----------------
- county_fips, county_name, year, quarter, tract_standard, tract_rows
- usps_total_addr = AMS_RES + AMS_BUS + AMS_OTH
- usps_vacant_addr = RES_VAC + BUS_VAC + OTH_VAC
- usps_nostat_addr = NOSTAT_RES + NOSTAT_BUS + NOSTAT_OTH
- usps_res_addr = AMS_RES
- usps_res_vacant_addr = RES_VAC
- usps_res_nostat_addr = NOSTAT_RES
- usps_vacancy_rate = usps_vacant_addr / usps_total_addr
- usps_nostat_rate = usps_nostat_addr / usps_total_addr
- usps_res_vacancy_rate = usps_res_vacant_addr / usps_res_addr
- usps_res_nostat_rate = usps_res_nostat_addr / usps_res_addr

Rate denominator note
---------------------
- Overall vacancy and no-stat rates use total addresses because the tract files contain residential, business, and other address counts.
- Residential-specific rates are also included for housing-focused analysis where AMS_RES is the more appropriate denominator.

Known limitations / caveats
---------------------------
- HUD USPS data are tract-level snapshots derived from USPS administrative records, not a designed housing survey.
- HUD FAQ documentation warns that longitudinal analysis is harder because USPS address management practices changed over time, including the Move to Competitive change that affected addresses around 2011-2012.
- Tract geography changes over time. Per project guidance, 2010 tracts apply through 2022 and 2020 tracts begin in 2023 Q1 and later.
- Because the panel is aggregated to county-year, tract-boundary changes are not harmonized beyond county aggregation.

Diagnostics
-----------
Rows written: 1131
Unique county-year rows: 1131
Unique counties: 87

Row counts by year and Minnesota county coverage:
- 2011: county rows=87, tract rows=1299, raw dbf records=65757
- 2012: county rows=87, tract rows=1334, raw dbf records=73258
- 2013: county rows=87, tract rows=1335, raw dbf records=73267
- 2014: county rows=87, tract rows=1335, raw dbf records=73352
- 2015: county rows=87, tract rows=1334, raw dbf records=73453
- 2016: county rows=87, tract rows=1335, raw dbf records=73464
- 2017: county rows=87, tract rows=1337, raw dbf records=73584
- 2018: county rows=87, tract rows=1335, raw dbf records=73470
- 2019: county rows=87, tract rows=1335, raw dbf records=73491
- 2020: county rows=87, tract rows=1335, raw dbf records=73469
- 2021: county rows=87, tract rows=1335, raw dbf records=73472
- 2022: county rows=87, tract rows=1335, raw dbf records=73472
- 2023: county rows=87, tract rows=1502, raw dbf records=84874

Summary stats:
- usps_vacancy_rate: n=1131, mean=0.060294, min=0.000000, p25=0.024950, median=0.049884, p75=0.087075, max=0.202544
- usps_nostat_rate: n=1131, mean=0.117384, min=0.017247, p25=0.070967, median=0.098956, p75=0.146970, max=0.408062
- usps_res_vacancy_rate: n=1131, mean=0.057554, min=0.000000, p25=0.020369, median=0.045824, p75=0.085671, max=0.199970
- usps_res_nostat_rate: n=1131, mean=0.113432, min=0.009483, p25=0.067893, median=0.094800, p75=0.144139, max=0.419550

Potential break checks:
- Statewide total addresses, 2011 to 2012: 2587483 -> 2652496 (2.51% change)
- Statewide total addresses, 2022 to 2023: 2897080 -> 2973517 (2.64% change)
- Statewide vacancy rate, 2011: 0.04500049; 2012: 0.04645134
- Statewide vacancy rate, 2022: 0.02273979; 2023: 0.02159362
