import delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/raw/bea/CAGDP1/CAGDP1_MN_2001_2024.csv", clear varnames(nonames) stringcols(_all)

drop in 1

rename v1 geofips
rename v2 geoname
rename v3 region
rename v4 tablename
rename v5 linecode
rename v6 industryclassification
rename v7 description
rename v8 unit

local col = 9
forvalues y = 2001/2024 {
    rename v`col' y`y'
    local ++col
}

replace geofips = trim(itrim(subinstr(geofips, char(34), "", .)))
replace geoname = trim(itrim(subinstr(geoname, char(34), "", .)))

keep if substr(geofips, 1, 2) == "27"
keep if strlen(geofips) == 5
drop if geofips == "27000"
keep if inlist(linecode, "1", "3")

destring linecode y2011-y2023, replace force

keep geofips geoname linecode y2011-y2023
reshape long y, i(geofips geoname linecode) j(year)
rename y gdp_value
reshape wide gdp_value, i(geofips geoname year) j(linecode)

rename gdp_value1 bea_real_gdp
rename gdp_value3 bea_nominal_gdp
rename geoname county_name

replace county_name = subinstr(county_name, ", MN", "", .)
gen county_fips = real(geofips)

keep county_fips county_name year bea_real_gdp bea_nominal_gdp
sort county_fips year
isid county_fips year

tempfile bea_summary
save `bea_summary'

import delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/raw/bea/CAGDP9/CAGDP9_MN_2001_2024.csv", clear varnames(nonames) stringcols(_all)

drop in 1

rename v1 geofips
rename v2 geoname
rename v3 region
rename v4 tablename
rename v5 linecode
rename v6 industryclassification
rename v7 description
rename v8 unit

local col = 9
forvalues y = 2001/2024 {
    rename v`col' y`y'
    local ++col
}

replace geofips = trim(itrim(subinstr(geofips, char(34), "", .)))

keep if substr(geofips, 1, 2) == "27"
keep if strlen(geofips) == 5
drop if geofips == "27000"
keep if linecode == "11"

destring y2011-y2023, replace force

keep geofips y2011-y2023
reshape long y, i(geofips) j(year)
rename y bea_real_gdp_construction

gen county_fips = real(geofips)
keep county_fips year bea_real_gdp_construction
sort county_fips year
isid county_fips year

merge 1:1 county_fips year using `bea_summary', nogen
order county_fips county_name year bea_real_gdp bea_nominal_gdp bea_real_gdp_construction
sort county_fips year
isid county_fips year

save "/Users/brendynbeasley/Desktop/mn_climate_project/clean/bea_gdp_mn_county_year_2011_2023.dta", replace
export delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/clean/bea_gdp_mn_county_year_2011_2023.csv", replace
