*******************************************************
* final_mn_climate_project.do
* Minnesota Climate Risk and Local Economic Conditions
* Final workflow: graphs, summary stats, regressions,
* and exportable tables/figures.
*******************************************************

clear all
set more off

* -----------------------------------------------------
* 0) Paths
* -----------------------------------------------------
local root "/Users/brendynbeasley/Desktop/mn_climate_project"
local clean "`root'/clean"
local out   "`root'/output"
local figs  "`out'/figures"
local tabs  "`out'/tables"
local logs  "`out'/logs"

capture mkdir "`out'"
capture mkdir "`figs'"
capture mkdir "`tabs'"
capture mkdir "`logs'"

log using "`logs'/final_mn_climate_project.log", replace text

* -----------------------------------------------------
* 1) Load final long panel
* -----------------------------------------------------
use "`clean'/mn_county_panel_2011_2023_plus_irs.dta", clear

* -----------------------------------------------------
* 2) Panel setup + derived variables
* -----------------------------------------------------
xtset county_fips year

capture drop irs_net_mig_rate
capture drop risk_std
capture drop flood_risk_std

* IRS migration rate per 1,000 residents
* Missing in 2011 by construction because IRS panel begins in 2012.
gen irs_net_mig_rate = 1000 * net_migration_exemptions / pop_total

* Standardized risk measures
summ risk_score if !missing(risk_score)
gen risk_std = (risk_score - r(mean)) / r(sd)

summ inland_flood_risk_score if !missing(inland_flood_risk_score)
gen flood_risk_std = (inland_flood_risk_score - r(mean)) / r(sd)

* -----------------------------------------------------
* 3) Final descriptive checks
* -----------------------------------------------------
describe
duplicates report county_fips year
summ temp_avg precip_total pop_total pop_growth_rate irs_net_mig_rate risk_score inland_flood_risk_score
count if !missing(irs_net_mig_rate)
count if year==2011 & !missing(irs_net_mig_rate)
count if year>=2012 & !missing(irs_net_mig_rate)

* -----------------------------------------------------
* 4) Exportable summary statistics table
* -----------------------------------------------------
* DOCX
capture noisily dtable temp_avg precip_total pop_total pop_growth_rate irs_net_mig_rate risk_score inland_flood_risk_score, ///
    title("Summary Statistics") ///
    nformat(%9.3f mean sd) ///
    export("`tabs'/summary_statistics.docx", replace)

* XLSX
capture noisily dtable temp_avg precip_total pop_total pop_growth_rate irs_net_mig_rate risk_score inland_flood_risk_score, ///
    title("Summary Statistics") ///
    nformat(%9.3f mean sd) ///
    export("`tabs'/summary_statistics.xlsx", replace)

* -----------------------------------------------------
* 5) Main regressions
* -----------------------------------------------------
estimates clear

xtreg pop_growth_rate c.temp_avg##c.risk_std precip_total i.year, fe vce(cluster county_fips)
estimates store m1

xtreg pop_growth_rate c.temp_avg##c.flood_risk_std precip_total i.year, fe vce(cluster county_fips)
estimates store m2

xtreg irs_net_mig_rate c.temp_avg##c.risk_std precip_total i.year, fe vce(cluster county_fips)
estimates store m3

xtreg irs_net_mig_rate c.temp_avg##c.flood_risk_std precip_total i.year, fe vce(cluster county_fips)
estimates store m4

* Display in Results window
estimates table m1 m2 m3 m4, b(%9.3f) se(%9.3f) stats(N r2_within, fmt(%9.0g %9.3f)) star(.10 .05 .01)

* Exportable regression table (DOCX and XLSX)
* etable is built-in in recent Stata versions.
capture noisily etable, estimates(m1 m2 m3 m4) showstars showstarsnote ///
    title("Main Regression Results") ///
    export("`tabs'/regression_table.docx", replace)

capture noisily etable, estimates(m1 m2 m3 m4) showstars showstarsnote ///
    title("Main Regression Results") ///
    export("`tabs'/regression_table.xlsx", replace)

* -----------------------------------------------------
* 6) Graphs
* -----------------------------------------------------

* Average temperature by year
preserve
collapse (mean) temp_avg, by(year)
twoway line temp_avg year, ///
    title("Average Temperature by Year") ///
    ytitle("Average annual temperature") ///
    xtitle("Year") ///
    xlabel(2011(1)2023)
graph export "`figs'/avg_temp_by_year.png", replace
restore

* Average precipitation by year
preserve
collapse (mean) precip_total, by(year)
twoway line precip_total year, ///
    title("Average Precipitation by Year") ///
    ytitle("Average annual precipitation") ///
    xtitle("Year") ///
    xlabel(2011(1)2023)
graph export "`figs'/avg_precip_by_year.png", replace
restore

* Average population growth by year
preserve
collapse (mean) pop_growth_rate, by(year)
twoway line pop_growth_rate year, ///
    title("Average Population Growth by Year") ///
    ytitle("Mean population growth rate") ///
    xtitle("Year") ///
    xlabel(2011(1)2023)
graph export "`figs'/avg_pop_growth_by_year.png", replace
restore

* Average IRS net migration rate by year
preserve
collapse (mean) irs_net_mig_rate, by(year)
twoway line irs_net_mig_rate year, ///
    title("Average IRS Net Migration Rate by Year") ///
    ytitle("Mean IRS net migration rate") ///
    xtitle("Year") ///
    xlabel(2012(1)2023)
graph export "`figs'/avg_irs_net_mig_rate_by_year.png", replace
restore

* County mean IRS net migration vs precipitation (scatter only)
preserve
collapse (mean) precip_total irs_net_mig_rate, by(county_fips)
twoway scatter irs_net_mig_rate precip_total, ///
    title("County Mean IRS Net Migration vs Precipitation") ///
    ytitle("Mean IRS net migration rate") ///
    xtitle("Mean precipitation")
graph export "`figs'/county_mean_irs_net_mig_vs_precip.png", replace
restore

* County mean IRS net migration vs precipitation with fitted line
preserve
collapse (mean) precip_total irs_net_mig_rate, by(county_fips)
twoway ///
    (scatter irs_net_mig_rate precip_total) ///
    (lfit irs_net_mig_rate precip_total), ///
    title("County Mean IRS Net Migration vs Precipitation") ///
    ytitle("Mean IRS net migration rate") ///
    xtitle("Mean precipitation")
graph export "`figs'/county_mean_irs_net_mig_vs_precip_lfit.png", replace
restore

log close
