*******************************************************
* run_working_paper_extensions.do
* Minnesota climate working-paper extensions
* Builds an analysis-ready panel, reruns the newer
* BEA/QWI/NASS blocks, and exports targeted robustness
* tables and figures for the manuscript draft.
*******************************************************

clear all
set more off
capture log close

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

log using "`logs'/run_working_paper_extensions.log", replace text

* -----------------------------------------------------
* 1) Build analysis-ready county-year panel
* -----------------------------------------------------
use "`clean'/mn_panel_with_unemployment_qcew.dta", clear
sort county_fips year
isid county_fips year

capture drop bps_*
merge 1:1 county_fips year using "`clean'/bps_mn_county_year_2011_2024.dta", ///
    keep(master match) nogen keepusing(bps_*)

capture drop cbp_*
merge 1:1 county_fips year using "`clean'/cbp_mn_county_year_2011_2023_construction.dta", ///
    keep(master match) nogen keepusing(cbp_*)

capture drop bea_personal_income bea_population bea_pc_income
merge 1:1 county_fips year using "`clean'/bea_mn_county_year_2011_2024.dta", ///
    keep(master match) nogen keepusing(bea_personal_income bea_population bea_pc_income)

capture drop bea_real_gdp bea_nominal_gdp bea_real_gdp_construction
merge 1:1 county_fips year using "`clean'/bea_gdp_mn_county_year_2011_2023.dta", ///
    keep(master match) nogen keepusing(bea_real_gdp bea_nominal_gdp bea_real_gdp_construction)

capture drop fhfa_*
merge 1:1 county_fips year using "`clean'/fhfa_mn_county_year_2011_2023.dta", ///
    keep(master match) nogen keepusing(fhfa_*)

capture drop usps_*
merge 1:1 county_fips year using "`clean'/mn_usps_vacancy_q4_county_2011_2023.dta", ///
    keep(master match) nogen keepusing(usps_*)

capture drop qwi_*
merge 1:1 county_fips year using "`clean'/mn_qwi_county_year_2011_2023_wide.dta", ///
    keep(master match) nogen keepusing(qwi_*)

capture drop nass_*
merge 1:1 county_fips year using "`clean'/nass_mn_county_year_2011_2023.dta", ///
    keep(master match) nogen keepusing(nass_*)

sort county_fips year
isid county_fips year

save "`clean'/mn_working_paper_analysis_panel_2011_2023.dta", replace
export delimited using "`clean'/mn_working_paper_analysis_panel_2011_2023.csv", replace

* -----------------------------------------------------
* 2) Panel setup + derived variables
* -----------------------------------------------------
xtset county_fips year

capture drop L1_precip L1_temp L2_precip L2_temp F1_precip F1_temp precip_ma3 temp_ma3 county_t
gen L1_precip = L.precip_total
gen L1_temp   = L.temp_avg
gen L2_precip = L2.precip_total
gen L2_temp   = L2.temp_avg
gen F1_precip = F1.precip_total
gen F1_temp   = F1.temp_avg

gen precip_ma3 = (precip_total + L1_precip + L2_precip) / 3 if !missing(precip_total, L1_precip, L2_precip)
gen temp_ma3   = (temp_avg + L1_temp + L2_temp) / 3 if !missing(temp_avg, L1_temp, L2_temp)
gen county_t   = year - 2011

capture drop irs_net_mig_rate irs_inflow_rate irs_outflow_rate flood_risk_std
capture drop ln_qcew_employment ln_bps_total_units ln_cbp_const_establishments
capture drop ln_bea_real_gdp ln_bea_nominal_gdp ln_bea_real_gdp_construction
capture drop ln_bea_personal_income ln_bea_pc_income ln_fhfa_hpi
capture drop ln_qwi_emp_total_private ln_qwi_hires_total_private ln_qwi_separations_total_private
capture drop ln_qwi_emp_construction ln_qwi_hires_construction ln_qwi_separations_construction
capture drop qwi_hire_rate_total_private qwi_sep_rate_total_private qwi_jc_rate_tp qwi_jd_rate_tp
capture drop qwi_hire_rate_construction qwi_sep_rate_construction qwi_jc_rate_con qwi_jd_rate_con
capture drop ln_nass_corn_yield ln_nass_soy_yield ln_nass_corn_planted ln_nass_soy_planted

gen irs_net_mig_rate = 1000 * net_migration_exemptions / pop_total if pop_total > 0 & !missing(net_migration_exemptions)
gen irs_inflow_rate  = 1000 * inflow_exemptions / pop_total if pop_total > 0 & !missing(inflow_exemptions)
gen irs_outflow_rate = 1000 * outflow_exemptions / pop_total if pop_total > 0 & !missing(outflow_exemptions)

summ inland_flood_risk_score if !missing(inland_flood_risk_score)
gen flood_risk_std = (inland_flood_risk_score - r(mean)) / r(sd)

gen ln_qcew_employment         = ln(qcew_employment) if qcew_employment > 0
gen ln_bps_total_units         = ln(bps_total_units + 1) if !missing(bps_total_units)
gen ln_cbp_const_establishments = ln(cbp_const_establishments + 1) if !missing(cbp_const_establishments)

gen ln_bea_real_gdp             = ln(bea_real_gdp) if bea_real_gdp > 0
gen ln_bea_nominal_gdp          = ln(bea_nominal_gdp) if bea_nominal_gdp > 0
gen ln_bea_real_gdp_construction = ln(bea_real_gdp_construction) if bea_real_gdp_construction > 0
gen ln_bea_personal_income      = ln(bea_personal_income) if bea_personal_income > 0
gen ln_bea_pc_income            = ln(bea_pc_income) if bea_pc_income > 0
gen ln_fhfa_hpi                 = ln(fhfa_hpi) if fhfa_hpi > 0

gen ln_qwi_emp_total_private         = ln(qwi_emp_total_private + 1)
gen ln_qwi_hires_total_private       = ln(qwi_hires_total_private + 1)
gen ln_qwi_separations_total_private = ln(qwi_separations_total_private + 1)
gen ln_qwi_emp_construction          = ln(qwi_emp_construction + 1)
gen ln_qwi_hires_construction        = ln(qwi_hires_construction + 1)
gen ln_qwi_separations_construction  = ln(qwi_separations_construction + 1)

gen qwi_hire_rate_total_private = 100 * qwi_hires_total_private / qwi_emp_total_private if qwi_emp_total_private > 0
gen qwi_sep_rate_total_private  = 100 * qwi_separations_total_private / qwi_emp_total_private if qwi_emp_total_private > 0
gen qwi_jc_rate_tp              = 100 * qwi_job_gains_total_private / qwi_emp_total_private if qwi_emp_total_private > 0
gen qwi_jd_rate_tp              = 100 * qwi_job_losses_total_private / qwi_emp_total_private if qwi_emp_total_private > 0

gen qwi_hire_rate_construction = 100 * qwi_hires_construction / qwi_emp_construction if qwi_emp_construction > 0
gen qwi_sep_rate_construction  = 100 * qwi_separations_construction / qwi_emp_construction if qwi_emp_construction > 0
gen qwi_jc_rate_con            = 100 * qwi_job_gains_construction / qwi_emp_construction if qwi_emp_construction > 0
gen qwi_jd_rate_con            = 100 * qwi_job_losses_construction / qwi_emp_construction if qwi_emp_construction > 0

gen ln_nass_corn_yield   = ln(nass_corn_grain_yield_buac) if nass_corn_grain_yield_buac > 0
gen ln_nass_soy_yield    = ln(nass_soy_yield_buac) if nass_soy_yield_buac > 0
gen ln_nass_corn_planted = ln(nass_corn_planted_acres) if nass_corn_planted_acres > 0
gen ln_nass_soy_planted  = ln(nass_soy_planted_acres) if nass_soy_planted_acres > 0

summ precip_total, detail
scalar precip_iqr = r(p75) - r(p25)
scalar precip_sd  = r(sd)

save "`clean'/mn_working_paper_analysis_panel_2011_2023.dta", replace
export delimited using "`clean'/mn_working_paper_analysis_panel_2011_2023.csv", replace

* -----------------------------------------------------
* 3) Headline contemporaneous table
* -----------------------------------------------------
estimates clear

xtreg pop_growth_rate c.temp_avg c.precip_total i.year, fe vce(cluster county_fips)
estimates store h1

xtreg irs_net_mig_rate c.temp_avg c.precip_total i.year if !missing(irs_net_mig_rate), fe vce(cluster county_fips)
estimates store h2

xtreg ln_qcew_employment c.temp_avg c.precip_total i.year if !missing(ln_qcew_employment), fe vce(cluster county_fips)
estimates store h3

xtreg ln_bps_total_units c.temp_avg c.precip_total i.year if !missing(ln_bps_total_units), fe vce(cluster county_fips)
estimates store h4

xtreg ln_cbp_const_establishments c.temp_avg c.precip_total i.year if !missing(ln_cbp_const_establishments), fe vce(cluster county_fips)
estimates store h5

esttab h1 h2 h3 h4 h5 using "`tabs'/working_paper_headline_baseline.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2_w, labels("N" "Within R-squared")) compress

esttab h1 h2 h3 h4 h5 using "`tabs'/working_paper_headline_baseline.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2_w, labels("N" "Within R-squared")) ///
    addnotes("County and year fixed effects included.", "Standard errors clustered at the county level.")

* -----------------------------------------------------
* 4) Placebo leads on headline outcomes
* -----------------------------------------------------
estimates clear

xtreg pop_growth_rate c.temp_avg c.precip_total c.F1_precip i.year if !missing(F1_precip), fe vce(cluster county_fips)
estimates store p1

xtreg irs_net_mig_rate c.temp_avg c.precip_total c.F1_precip i.year if !missing(irs_net_mig_rate, F1_precip), fe vce(cluster county_fips)
estimates store p2

xtreg ln_qcew_employment c.temp_avg c.precip_total c.F1_precip i.year if !missing(ln_qcew_employment, F1_precip), fe vce(cluster county_fips)
estimates store p3

xtreg ln_bps_total_units c.temp_avg c.precip_total c.F1_precip i.year if !missing(ln_bps_total_units, F1_precip), fe vce(cluster county_fips)
estimates store p4

xtreg ln_cbp_const_establishments c.temp_avg c.precip_total c.F1_precip i.year if !missing(ln_cbp_const_establishments, F1_precip), fe vce(cluster county_fips)
estimates store p5

esttab p1 p2 p3 p4 p5 using "`tabs'/working_paper_placebo_leads.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total F1_precip) ///
    order(temp_avg precip_total F1_precip) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2_w, labels("N" "Within R-squared")) compress

esttab p1 p2 p3 p4 p5 using "`tabs'/working_paper_placebo_leads.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total F1_precip) ///
    order(temp_avg precip_total F1_precip) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2_w, labels("N" "Within R-squared")) ///
    addnotes("County and year fixed effects included.", "The placebo term is next year's precipitation.", "Standard errors clustered at the county level.")

* -----------------------------------------------------
* 5) County-trend robustness on headline outcomes
* -----------------------------------------------------
estimates clear

xtreg pop_growth_rate c.temp_avg c.precip_total i.year c.county_t#i.county_fips, fe vce(cluster county_fips)
estimates store t1

xtreg irs_net_mig_rate c.temp_avg c.precip_total i.year c.county_t#i.county_fips if !missing(irs_net_mig_rate), fe vce(cluster county_fips)
estimates store t2

xtreg ln_qcew_employment c.temp_avg c.precip_total i.year c.county_t#i.county_fips if !missing(ln_qcew_employment), fe vce(cluster county_fips)
estimates store t3

xtreg ln_bps_total_units c.temp_avg c.precip_total i.year c.county_t#i.county_fips if !missing(ln_bps_total_units), fe vce(cluster county_fips)
estimates store t4

xtreg ln_cbp_const_establishments c.temp_avg c.precip_total i.year c.county_t#i.county_fips if !missing(ln_cbp_const_establishments), fe vce(cluster county_fips)
estimates store t5

esttab t1 t2 t3 t4 t5 using "`tabs'/working_paper_county_trends.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2_w, labels("N" "Within R-squared")) compress

esttab t1 t2 t3 t4 t5 using "`tabs'/working_paper_county_trends.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2_w, labels("N" "Within R-squared")) ///
    addnotes("County and year fixed effects included.", "County-specific linear time trends included.", "Standard errors clustered at the county level.")

* -----------------------------------------------------
* 6) Population-weighted headline outcomes
* -----------------------------------------------------
estimates clear

areg pop_growth_rate c.temp_avg c.precip_total i.year [aw=pop_total], absorb(county_fips) vce(cluster county_fips)
estimates store w1

areg irs_net_mig_rate c.temp_avg c.precip_total i.year [aw=pop_total] if !missing(irs_net_mig_rate), absorb(county_fips) vce(cluster county_fips)
estimates store w2

areg ln_qcew_employment c.temp_avg c.precip_total i.year [aw=pop_total] if !missing(ln_qcew_employment), absorb(county_fips) vce(cluster county_fips)
estimates store w3

areg ln_bps_total_units c.temp_avg c.precip_total i.year [aw=pop_total] if !missing(ln_bps_total_units), absorb(county_fips) vce(cluster county_fips)
estimates store w4

areg ln_cbp_const_establishments c.temp_avg c.precip_total i.year [aw=pop_total] if !missing(ln_cbp_const_establishments), absorb(county_fips) vce(cluster county_fips)
estimates store w5

esttab w1 w2 w3 w4 w5 using "`tabs'/working_paper_population_weighted.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2, labels("N" "R-squared")) compress

esttab w1 w2 w3 w4 w5 using "`tabs'/working_paper_population_weighted.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("Pop growth" "IRS net mig rate" "Log QCEW emp" "Log permit units" "Log const estabs") ///
    stats(N r2, labels("N" "R-squared")) ///
    addnotes("County and year fixed effects included.", "Observations weighted by county population.", "Standard errors clustered at the county level.")

* -----------------------------------------------------
* 7) QWI mechanism table
* -----------------------------------------------------
estimates clear

xtreg ln_qwi_hires_total_private c.temp_avg c.precip_total i.year if qwi_inc_tp == 0 & qwi_hflag_tp == 0, fe vce(cluster county_fips)
estimates store q1

xtreg qwi_sep_rate_total_private c.temp_avg c.precip_total i.year if qwi_inc_tp == 0 & qwi_sflag_tp == 0, fe vce(cluster county_fips)
estimates store q2

xtreg ln_qwi_emp_total_private c.temp_avg c.precip_total i.year if qwi_inc_tp == 0 & qwi_eflag_tp == 0, fe vce(cluster county_fips)
estimates store q3

xtreg ln_qwi_hires_construction c.temp_avg c.precip_total i.year if qwi_inc_con == 0 & qwi_hflag_con == 0, fe vce(cluster county_fips)
estimates store q4

xtreg qwi_sep_rate_construction c.temp_avg c.precip_total i.year if qwi_inc_con == 0 & qwi_sflag_con == 0, fe vce(cluster county_fips)
estimates store q5

xtreg ln_qwi_emp_construction c.temp_avg c.precip_total i.year if qwi_inc_con == 0 & qwi_eflag_con == 0, fe vce(cluster county_fips)
estimates store q6

esttab q1 q2 q3 q4 q5 q6 using "`tabs'/working_paper_qwi_mechanisms.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("TP hires" "TP sep rate" "TP emp" "Const hires" "Const sep rate" "Const emp") ///
    stats(N r2_w, labels("N" "Within R-squared")) compress

esttab q1 q2 q3 q4 q5 q6 using "`tabs'/working_paper_qwi_mechanisms.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total) ///
    mtitles("TP hires" "TP sep rate" "TP emp" "Const hires" "Const sep rate" "Const emp") ///
    stats(N r2_w, labels("N" "Within R-squared")) ///
    addnotes("County and year fixed effects included.", "QWI models apply the sector-specific incomplete-year and flag filters.", "Standard errors clustered at the county level.")

* -----------------------------------------------------
* 8) BEA GDP persistence table
* -----------------------------------------------------
estimates clear

xtreg ln_bea_real_gdp c.temp_avg c.precip_total i.year if !missing(ln_bea_real_gdp), fe vce(cluster county_fips)
estimates store g1

xtreg ln_bea_real_gdp c.L1_temp c.L1_precip i.year if !missing(ln_bea_real_gdp, L1_temp, L1_precip), fe vce(cluster county_fips)
estimates store g2

xtreg ln_bea_real_gdp c.temp_ma3 c.precip_ma3 i.year if !missing(ln_bea_real_gdp, temp_ma3, precip_ma3), fe vce(cluster county_fips)
estimates store g3

xtreg ln_bea_real_gdp_construction c.temp_avg c.precip_total i.year if !missing(ln_bea_real_gdp_construction), fe vce(cluster county_fips)
estimates store g4

xtreg ln_bea_real_gdp_construction c.L1_temp c.L1_precip i.year if !missing(ln_bea_real_gdp_construction, L1_temp, L1_precip), fe vce(cluster county_fips)
estimates store g5

xtreg ln_bea_real_gdp_construction c.temp_ma3 c.precip_ma3 i.year if !missing(ln_bea_real_gdp_construction, temp_ma3, precip_ma3), fe vce(cluster county_fips)
estimates store g6

esttab g1 g2 g3 g4 g5 g6 using "`tabs'/working_paper_bea_gdp_persistence.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total L1_temp L1_precip temp_ma3 precip_ma3) ///
    mtitles("GDP contemp" "GDP lag" "GDP MA3" "Const GDP contemp" "Const GDP lag" "Const GDP MA3") ///
    stats(N r2_w, labels("N" "Within R-squared")) compress

esttab g1 g2 g3 g4 g5 g6 using "`tabs'/working_paper_bea_gdp_persistence.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total L1_temp L1_precip temp_ma3 precip_ma3) ///
    mtitles("GDP contemp" "GDP lag" "GDP MA3" "Const GDP contemp" "Const GDP lag" "Const GDP MA3") ///
    stats(N r2_w, labels("N" "Within R-squared")) ///
    addnotes("County and year fixed effects included.", "Lagged and moving-average climate specifications use the balanced annual panel setup.", "Standard errors clustered at the county level.")

* -----------------------------------------------------
* 9) NASS yield persistence table
* -----------------------------------------------------
estimates clear

tempname nasspost
postfile `nasspost' str8 crop str16 spec double coef se lb ub pval N using ///
    "`tabs'/working_paper_nass_yield_persistence_coeffs.dta", replace

xtreg ln_nass_corn_yield c.temp_avg c.precip_total i.year if !missing(ln_nass_corn_yield), fe vce(cluster county_fips)
estimates store n1
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `nasspost' ("Corn") ("Contemporaneous") (`coef') (`se') (`lb') (`ub') (`pval') (e(N))

xtreg ln_nass_corn_yield c.L1_temp c.L1_precip i.year if !missing(ln_nass_corn_yield, L1_temp, L1_precip), fe vce(cluster county_fips)
estimates store n2
local coef = _b[L1_precip]
local se   = _se[L1_precip]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `nasspost' ("Corn") ("Lag 1") (`coef') (`se') (`lb') (`ub') (`pval') (e(N))

xtreg ln_nass_corn_yield c.temp_ma3 c.precip_ma3 i.year if !missing(ln_nass_corn_yield, temp_ma3, precip_ma3), fe vce(cluster county_fips)
estimates store n3
local coef = _b[precip_ma3]
local se   = _se[precip_ma3]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `nasspost' ("Corn") ("3-year avg") (`coef') (`se') (`lb') (`ub') (`pval') (e(N))

xtreg ln_nass_soy_yield c.temp_avg c.precip_total i.year if !missing(ln_nass_soy_yield), fe vce(cluster county_fips)
estimates store n4
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `nasspost' ("Soy") ("Contemporaneous") (`coef') (`se') (`lb') (`ub') (`pval') (e(N))

xtreg ln_nass_soy_yield c.L1_temp c.L1_precip i.year if !missing(ln_nass_soy_yield, L1_temp, L1_precip), fe vce(cluster county_fips)
estimates store n5
local coef = _b[L1_precip]
local se   = _se[L1_precip]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `nasspost' ("Soy") ("Lag 1") (`coef') (`se') (`lb') (`ub') (`pval') (e(N))

xtreg ln_nass_soy_yield c.temp_ma3 c.precip_ma3 i.year if !missing(ln_nass_soy_yield, temp_ma3, precip_ma3), fe vce(cluster county_fips)
estimates store n6
local coef = _b[precip_ma3]
local se   = _se[precip_ma3]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `nasspost' ("Soy") ("3-year avg") (`coef') (`se') (`lb') (`ub') (`pval') (e(N))

postclose `nasspost'

esttab n1 n2 n3 n4 n5 n6 using "`tabs'/working_paper_nass_yield_persistence.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total L1_temp L1_precip temp_ma3 precip_ma3) ///
    mtitles("Corn contemp" "Corn lag" "Corn MA3" "Soy contemp" "Soy lag" "Soy MA3") ///
    stats(N r2_w, labels("N" "Within R-squared")) compress

esttab n1 n2 n3 n4 n5 n6 using "`tabs'/working_paper_nass_yield_persistence.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total L1_temp L1_precip temp_ma3 precip_ma3) ///
    mtitles("Corn contemp" "Corn lag" "Corn MA3" "Soy contemp" "Soy lag" "Soy MA3") ///
    stats(N r2_w, labels("N" "Within R-squared")) ///
    addnotes("County and year fixed effects included.", "Lagged and moving-average climate specifications test persistence in agricultural productivity.", "Standard errors clustered at the county level.")

preserve
use "`tabs'/working_paper_nass_yield_persistence_coeffs.dta", clear
export delimited using "`tabs'/working_paper_nass_yield_persistence_coeffs.csv", replace

gen plot_order = .
replace plot_order = 1 if spec == "Contemporaneous"
replace plot_order = 2 if spec == "Lag 1"
replace plot_order = 3 if spec == "3-year avg"

label define nassspec 1 "Contemporaneous" 2 "Lag 1" 3 "3-year avg"
label values plot_order nassspec

twoway ///
    (rcap ub lb plot_order if crop == "Corn", horizontal lcolor(navy)) ///
    (scatter plot_order coef if crop == "Corn", msymbol(D) mcolor(navy)) ///
    (rcap ub lb plot_order if crop == "Soy", horizontal lcolor(forest_green)) ///
    (scatter plot_order coef if crop == "Soy", msymbol(O) mcolor(forest_green)), ///
    by(crop, note("") cols(2)) ///
    yscale(reverse) ///
    ylabel(1 "Contemporaneous" 2 "Lag 1" 3 "3-year avg", angle(0)) ///
    xline(0, lpattern(dash) lcolor(maroon)) ///
    xtitle("Precipitation coefficient") ///
    ytitle("") ///
    title("NASS Yield Sensitivity to Precipitation")

graph export "`figs'/working_paper_nass_yield_persistence.png", replace
restore

* -----------------------------------------------------
* 10) NASS acreage persistence table
* -----------------------------------------------------
estimates clear

xtreg ln_nass_corn_planted c.temp_avg c.precip_total i.year if !missing(ln_nass_corn_planted), fe vce(cluster county_fips)
estimates store a1

xtreg ln_nass_corn_planted c.L1_temp c.L1_precip i.year if !missing(ln_nass_corn_planted, L1_temp, L1_precip), fe vce(cluster county_fips)
estimates store a2

xtreg ln_nass_corn_planted c.temp_ma3 c.precip_ma3 i.year if !missing(ln_nass_corn_planted, temp_ma3, precip_ma3), fe vce(cluster county_fips)
estimates store a3

xtreg ln_nass_soy_planted c.temp_avg c.precip_total i.year if !missing(ln_nass_soy_planted), fe vce(cluster county_fips)
estimates store a4

xtreg ln_nass_soy_planted c.L1_temp c.L1_precip i.year if !missing(ln_nass_soy_planted, L1_temp, L1_precip), fe vce(cluster county_fips)
estimates store a5

xtreg ln_nass_soy_planted c.temp_ma3 c.precip_ma3 i.year if !missing(ln_nass_soy_planted, temp_ma3, precip_ma3), fe vce(cluster county_fips)
estimates store a6

esttab a1 a2 a3 a4 a5 a6 using "`tabs'/working_paper_nass_acreage_persistence.csv", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total L1_temp L1_precip temp_ma3 precip_ma3) ///
    mtitles("Corn planted contemp" "Corn planted lag" "Corn planted MA3" "Soy planted contemp" "Soy planted lag" "Soy planted MA3") ///
    stats(N r2_w, labels("N" "Within R-squared")) compress

esttab a1 a2 a3 a4 a5 a6 using "`tabs'/working_paper_nass_acreage_persistence.rtf", replace ///
    b(%9.4f) se(%9.4f) star(* 0.10 ** 0.05 *** 0.01) ///
    keep(temp_avg precip_total L1_temp L1_precip temp_ma3 precip_ma3) ///
    mtitles("Corn planted contemp" "Corn planted lag" "Corn planted MA3" "Soy planted contemp" "Soy planted lag" "Soy planted MA3") ///
    stats(N r2_w, labels("N" "Within R-squared")) ///
    addnotes("County and year fixed effects included.", "These acreage models complement the stronger yield results.", "Standard errors clustered at the county level.")

* -----------------------------------------------------
* 11) Saved precipitation-effect datasets and figure
* -----------------------------------------------------
tempname effpost
postfile `effpost' str32 outcome str8 family double coef se lb ub pval N iqr_effect sd_effect using ///
    "`tabs'/working_paper_precip_effects.dta", replace

xtreg pop_growth_rate c.temp_avg c.precip_total i.year, fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("Population growth") ("rate") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

xtreg irs_net_mig_rate c.temp_avg c.precip_total i.year if !missing(irs_net_mig_rate), fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("IRS net migration") ("rate") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

xtreg ln_qcew_employment c.temp_avg c.precip_total i.year if !missing(ln_qcew_employment), fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("QCEW employment") ("log") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

xtreg ln_bps_total_units c.temp_avg c.precip_total i.year if !missing(ln_bps_total_units), fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("Permit units") ("log") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

xtreg ln_cbp_const_establishments c.temp_avg c.precip_total i.year if !missing(ln_cbp_const_establishments), fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("Construction estabs") ("log") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

xtreg ln_bea_real_gdp_construction c.temp_avg c.precip_total i.year if !missing(ln_bea_real_gdp_construction), fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("Construction GDP") ("log") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

xtreg ln_nass_corn_yield c.temp_avg c.precip_total i.year if !missing(ln_nass_corn_yield), fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("Corn yield") ("log") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

xtreg ln_nass_soy_yield c.temp_avg c.precip_total i.year if !missing(ln_nass_soy_yield), fe vce(cluster county_fips)
local coef = _b[precip_total]
local se   = _se[precip_total]
local tcrit = invttail(e(df_r), 0.025)
local lb = `coef' - `tcrit' * `se'
local ub = `coef' + `tcrit' * `se'
local pval = 2 * ttail(e(df_r), abs(`coef' / `se'))
post `effpost' ("Soy yield") ("log") (`coef') (`se') (`lb') (`ub') (`pval') (e(N)) (`coef' * precip_iqr) (`coef' * precip_sd)

postclose `effpost'

preserve
use "`tabs'/working_paper_precip_effects.dta", clear
format coef se lb ub pval iqr_effect sd_effect %9.4f
export delimited using "`tabs'/working_paper_precip_effects.csv", replace

keep if family == "log"
gen plot_order = .
replace plot_order = 1 if outcome == "Soy yield"
replace plot_order = 2 if outcome == "Corn yield"
replace plot_order = 3 if outcome == "Construction GDP"
replace plot_order = 4 if outcome == "Construction estabs"
replace plot_order = 5 if outcome == "Permit units"
replace plot_order = 6 if outcome == "QCEW employment"

twoway ///
    (rcap ub lb plot_order, horizontal lcolor(navy)) ///
    (scatter plot_order coef, msymbol(D) mcolor(navy)), ///
    yscale(reverse) ///
    ylabel(1 "Soy yield" 2 "Corn yield" 3 "Construction GDP" 4 "Construction estabs" 5 "Permit units" 6 "QCEW employment", angle(0)) ///
    xline(0, lpattern(dash) lcolor(maroon)) ///
    xtitle("Precipitation coefficient") ///
    ytitle("") ///
    title("Precipitation Effects Across Log Outcomes")

graph export "`figs'/working_paper_precip_log_outcomes.png", replace
restore

* -----------------------------------------------------
* 12) Save final panel and close
* -----------------------------------------------------
sort county_fips year
save "`clean'/mn_working_paper_analysis_panel_2011_2023.dta", replace
export delimited using "`clean'/mn_working_paper_analysis_panel_2011_2023.csv", replace

log close
