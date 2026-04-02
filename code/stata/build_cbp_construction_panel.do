*******************************************************
* build_cbp_construction_panel.do
* Build Minnesota county-year CBP construction panel
*******************************************************

clear all
set more off

tempfile master23
save `master23', emptyok replace

forvalues y = 11/23 {
    import delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/raw/census_cbp/cbp`y'co.txt", clear stringcols(_all) varnames(1)

    keep fipstate fipscty naics emp qp1 ap est
    keep if fipstate == "27"
    keep if fipscty != "999"
    keep if naics == "23----"

    gen year = 2000 + `y'
    gen county_fips = real(fipstate + fipscty)

    destring emp qp1 ap est, replace force

    keep county_fips year emp qp1 ap est
    append using `master23'
    save `master23', replace
}

use `master23', clear
sort county_fips year
isid county_fips year

rename emp cbp_const_emp
rename qp1 cbp_const_q1_payroll
rename ap cbp_const_annual_payroll
rename est cbp_const_establishments

save "/Users/brendynbeasley/Desktop/mn_climate_project/clean/cbp_mn_county_year_2011_2023_construction.dta", replace
export delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/clean/cbp_mn_county_year_2011_2023_construction.csv", replace
