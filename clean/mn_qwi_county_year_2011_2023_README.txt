Minnesota QWI labor-market adjustment panel

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
- raw API files written: 416
- county-quarter rows: 36169
- county-year long rows: 9044
- county-year wide rows: 1131
- counties in wide panel: 87
- quarter rows by industry:
  - accom_food: 4524
  - agriculture: 4524
  - construction: 4524
  - health_social: 4524
  - manufacturing: 4502
  - retail: 4524
  - total_private: 4524
  - transport_warehousing: 4523
