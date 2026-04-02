import delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/raw/nass/nass.csv", ///
    clear varnames(nonames) stringcols(_all)

drop in 1

rename v1  program
rename v2  year
rename v3  period
rename v4  week_ending
rename v5  geolevel
rename v6  state
rename v7  stateansi
rename v8  agdistrict
rename v9  agdistrictcode
rename v10 county
rename v11 countyansi
rename v12 zipcode
rename v13 region
rename v14 watershed_code
rename v15 watershed
rename v16 commodity
rename v17 dataitem
rename v18 domain
rename v19 domaincategory
rename v20 value
rename v21 cv_pct

foreach var in program year period geolevel state stateansi county countyansi commodity dataitem domain value cv_pct {
    replace `var' = trim(itrim(`var'))
}

keep if program == "SURVEY"
keep if state == "MINNESOTA"
keep if geolevel == "COUNTY"
keep if period == "YEAR"
keep if domain == "TOTAL"
keep if inrange(real(year), 2011, 2023)

drop if countyansi == ""
drop if county == "OTHER (COMBINED) COUNTIES"

gen keep_item = 0
replace keep_item = 1 if inlist(dataitem, ///
    "CORN - ACRES PLANTED", ///
    "CORN, GRAIN - ACRES HARVESTED", ///
    "CORN, GRAIN - YIELD, MEASURED IN BU / ACRE", ///
    "CORN, SILAGE - ACRES HARVESTED", ///
    "CORN, SILAGE - YIELD, MEASURED IN TONS / ACRE")
replace keep_item = 1 if inlist(dataitem, ///
    "SOYBEANS - ACRES HARVESTED", ///
    "SOYBEANS - ACRES PLANTED", ///
    "SOYBEANS - YIELD, MEASURED IN BU / ACRE", ///
    "WHEAT, SPRING, (EXCL DURUM) - ACRES HARVESTED", ///
    "WHEAT, SPRING, (EXCL DURUM) - ACRES PLANTED", ///
    "WHEAT, SPRING, (EXCL DURUM) - YIELD, MEASURED IN BU / ACRE")
keep if keep_item
drop keep_item

replace value = subinstr(value, ",", "", .)
replace cv_pct = subinstr(cv_pct, ",", "", .)

destring year value cv_pct, replace force

gen county_fips = real(stateansi + countyansi)
rename county county_name
replace county_name = proper(lower(county_name))
replace county_name = "McLeod" if county_name == "Mcleod"
replace county_name = "Lake of the Woods" if county_name == "Lake Of The Woods"

gen series = ""
replace series = "corn_planted_acres"      if dataitem == "CORN - ACRES PLANTED"
replace series = "corn_grain_harv_acres"   if dataitem == "CORN, GRAIN - ACRES HARVESTED"
replace series = "corn_grain_yield_buac"   if dataitem == "CORN, GRAIN - YIELD, MEASURED IN BU / ACRE"
replace series = "corn_silage_harv_acres"  if dataitem == "CORN, SILAGE - ACRES HARVESTED"
replace series = "corn_silage_yield_tonac" if dataitem == "CORN, SILAGE - YIELD, MEASURED IN TONS / ACRE"
replace series = "soy_harv_acres"          if dataitem == "SOYBEANS - ACRES HARVESTED"
replace series = "soy_planted_acres"       if dataitem == "SOYBEANS - ACRES PLANTED"
replace series = "soy_yield_buac"          if dataitem == "SOYBEANS - YIELD, MEASURED IN BU / ACRE"
replace series = "swheat_harv_acres"       if dataitem == "WHEAT, SPRING, (EXCL DURUM) - ACRES HARVESTED"
replace series = "swheat_planted_acres"    if dataitem == "WHEAT, SPRING, (EXCL DURUM) - ACRES PLANTED"
replace series = "swheat_yield_buac"       if dataitem == "WHEAT, SPRING, (EXCL DURUM) - YIELD, MEASURED IN BU / ACRE"

assert !missing(series)

keep county_fips county_name year series value cv_pct
sort county_fips year series
isid county_fips year series

tempfile nass_long
save `nass_long'

reshape wide value cv_pct, i(county_fips county_name year) j(series) string

rename valuecorn_planted_acres      nass_corn_planted_acres
rename valuecorn_grain_harv_acres   nass_corn_grain_harv_acres
rename valuecorn_grain_yield_buac   nass_corn_grain_yield_buac
rename valuecorn_silage_harv_acres  nass_corn_silage_harv_acres
rename valuecorn_silage_yield_tonac nass_corn_silage_yield_tonac
rename valuesoy_harv_acres          nass_soy_harv_acres
rename valuesoy_planted_acres       nass_soy_planted_acres
rename valuesoy_yield_buac          nass_soy_yield_buac
rename valueswheat_harv_acres       nass_swheat_harv_acres
rename valueswheat_planted_acres    nass_swheat_planted_acres
rename valueswheat_yield_buac       nass_swheat_yield_buac

rename cv_pctcorn_planted_acres      nass_corn_planted_acres_cv
rename cv_pctcorn_grain_harv_acres   nass_corn_grain_harv_acres_cv
rename cv_pctcorn_grain_yield_buac   nass_corn_grain_yield_buac_cv
rename cv_pctcorn_silage_harv_acres  nass_corn_silage_harv_acres_cv
rename cv_pctcorn_silage_yield_tonac nass_corn_silage_yield_tonac_cv
rename cv_pctsoy_harv_acres          nass_soy_harv_acres_cv
rename cv_pctsoy_planted_acres       nass_soy_planted_acres_cv
rename cv_pctsoy_yield_buac          nass_soy_yield_buac_cv
rename cv_pctswheat_harv_acres       nass_swheat_harv_acres_cv
rename cv_pctswheat_planted_acres    nass_swheat_planted_acres_cv
rename cv_pctswheat_yield_buac       nass_swheat_yield_buac_cv

order county_fips county_name year ///
    nass_corn_planted_acres nass_corn_grain_harv_acres nass_corn_grain_yield_buac ///
    nass_corn_silage_harv_acres nass_corn_silage_yield_tonac ///
    nass_soy_planted_acres nass_soy_harv_acres nass_soy_yield_buac ///
    nass_swheat_planted_acres nass_swheat_harv_acres nass_swheat_yield_buac

sort county_fips year
isid county_fips year

save "/Users/brendynbeasley/Desktop/mn_climate_project/clean/nass_mn_county_year_2011_2023.dta", replace
export delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/clean/nass_mn_county_year_2011_2023.csv", replace

use `nass_long', clear
order county_fips county_name year series value cv_pct
sort county_fips year series

save "/Users/brendynbeasley/Desktop/mn_climate_project/clean/nass_mn_county_year_2011_2023_long.dta", replace
export delimited using "/Users/brendynbeasley/Desktop/mn_climate_project/clean/nass_mn_county_year_2011_2023_long.csv", replace
