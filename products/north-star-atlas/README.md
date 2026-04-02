# North Star Atlas

Static map-based county dashboard for the Minnesota climate-economy project.

## What it is

This product combines the project’s strongest county-year layers into a standalone dashboard:

- official FEMA risk and inland flood risk
- NOAA climate measures
- Census population growth
- IRS migration
- BLS unemployment and QCEW labor-market outcomes
- Census Building Permits activity
- CBP construction establishment counts
- HUD USPS residential vacancy
- BEA per capita income

The dashboard is intended as a communication and exploration layer, not a replacement for the paper’s formal regressions.

## Files

- [index.html](/Users/brendynbeasley/Desktop/mn_climate_project/products/north-star-atlas/index.html): entry point
- [styles.css](/Users/brendynbeasley/Desktop/mn_climate_project/products/north-star-atlas/styles.css): presentation
- [app.js](/Users/brendynbeasley/Desktop/mn_climate_project/products/north-star-atlas/app.js): dashboard logic
- [scripts/build_dashboard_data.py](/Users/brendynbeasley/Desktop/mn_climate_project/products/north-star-atlas/scripts/build_dashboard_data.py): rebuilds the dashboard data bundle
- [data/dashboard-data.js](/Users/brendynbeasley/Desktop/mn_climate_project/products/north-star-atlas/data/dashboard-data.js): merged dashboard dataset
- [data/mn-counties.js](/Users/brendynbeasley/Desktop/mn_climate_project/products/north-star-atlas/data/mn-counties.js): Minnesota county geometry bundle

## Rebuild

Run:

```bash
cd /Users/brendynbeasley/Desktop/mn_climate_project
./.venv/bin/python products/north-star-atlas/scripts/build_dashboard_data.py
```

## Notes

- The county geometry was pulled from the U.S. Census TIGERweb county service and bundled locally for a simple static deployment.
- Composite scores in the dashboard are exploratory and meant for orientation. For formal claims, use the underlying variables and regression tables.
