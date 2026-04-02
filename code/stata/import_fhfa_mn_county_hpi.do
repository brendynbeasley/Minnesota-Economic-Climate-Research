import excel using "/Users/brendynbeasley/Desktop/mn_climate_project/raw/fhfa/hpi_at_county.xlsx", ///
    sheet("county") cellrange(A7:H50000) clear

rename A state_abbr
rename B county_name
rename C county_fips
rename D year
rename E fhfa_annual_change
rename F fhfa_hpi
rename G fhfa_hpi_1990base
rename H fhfa_hpi_2000base

keep if state_abbr == "MN"
keep if inrange(year, 2011, 2023)

order county_fips county_name year fhfa_annual_change fhfa_hpi fhfa_hpi_1990base fhfa_hpi_2000base
sort county_fips year

isid county_fips year

save "/Users/brendynbeasley/Desktop/mn_climate_project/clean/fhfa_mn_county_year_2011_2023.dta", replace
export delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/clean/fhfa_mn_county_year_2011_2023.csv", replace
