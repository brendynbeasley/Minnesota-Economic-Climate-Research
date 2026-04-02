clear all
set more off

local qcew_root "/Users/brendynbeasley/Desktop/mn_climate_project/raw/qcew_mn"
local out_file  "/Users/brendynbeasley/Desktop/mn_climate_project/mn_qcew_panel_2011_2024.dta"

tempfile qcew_all
save `qcew_all', emptyok replace

forvalues y = 2011/2024 {
    local folder "`qcew_root'/`y'.annual.by_area"
    local files : dir "`folder'" files "*.csv"

    foreach f of local files {
        if strpos(lower("`f'"), "statewide") continue
        if strpos(lower("`f'"), "unknown") continue
        if regexm("`f'", "^[0-9]{4}\.annual CS") continue
        if regexm("`f'", "^[0-9]{4}\.annual C") continue

        import delimited using "`folder'/`f'", clear varnames(1)
        rename *, lower

        keep if qtr == "A" ///
            & own_code == 0 ///
            & industry_code == "10" ///
            & agglvl_code == 70 ///
            & size_code == 0

        count
        assert r(N) == 1

        keep area_fips year annual_avg_estabs annual_avg_emplvl total_annual_wages annual_avg_wkly_wage
        rename area_fips            county_fips
        rename annual_avg_estabs    qcew_estabs
        rename annual_avg_emplvl    qcew_employment
        rename total_annual_wages   qcew_total_wages
        rename annual_avg_wkly_wage qcew_avg_wkly_wage

        append using `qcew_all'
        save `qcew_all', replace
    }
}

use `qcew_all', clear
sort county_fips year
isid county_fips year
count
assert r(N) == 1218

save "`out_file'", replace
