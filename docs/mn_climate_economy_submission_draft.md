# Climate Risk and Local Economic Adjustment in Minnesota Counties

Brendyn Beasley  
Submission draft  
April 2026

## Abstract

This paper studies how annual climate conditions are associated with local economic adjustment across Minnesota counties. I construct a county-year panel for all 87 Minnesota counties by harmonizing NOAA climate records, FEMA National Risk Index measures, Census population estimates, IRS migration data, BLS unemployment data, QCEW employment and wage data, BEA personal income data, the Census Building Permits Survey, County Business Patterns, and HUD-USPS vacancy files. The core empirical framework is a county fixed-effects design that compares counties to themselves over time while absorbing common statewide shocks with year fixed effects. I then extend the baseline model in three directions that match the substantive patterns in the data: distributed-lag climate specifications, multi-year moving-average climate measures, and interactions between precipitation and baseline flood risk.

The results point to a consistent economic pattern. Precipitation, more than temperature, is the most stable adverse climate margin in the Minnesota county data. Wetter county-years are associated with slower population growth, weaker IRS net migration, lower employment, fewer building permits, and fewer construction establishments. The migration evidence suggests that this demographic response operates more through weaker in-migration than through large increases in out-migration. Flood-risk heterogeneity is clearest in the employment regressions, where the negative association between precipitation and employment is stronger in counties with higher baseline inland flood risk. Temperature still matters, but it is most visible in broader income measures: hotter county-years are associated with lower BEA per capita income, and total personal income falls with both higher temperature and higher precipitation. Taken together, the evidence suggests that climate stress in Minnesota operates less through dramatic wage collapses and more through gradual erosion of local economic momentum.

Keywords: climate risk; local adjustment; migration; construction; county fixed effects; Minnesota

JEL Codes: Q54; R11; R23; J61

## 1. Introduction

How climate conditions affect local adjustment is a central question in regional and applied economics. Much of the public conversation focuses on headline risks such as coastal flooding, sea-level rise, wildfire, or extreme heat in large metropolitan areas. But climate-related economic pressure can also arise in inland states through precipitation, localized flooding, infrastructure strain, agricultural disruption, housing-market frictions, and changes in the relative attractiveness of places. This paper studies whether climate conditions are associated with those kinds of local adjustments across Minnesota counties.

Minnesota is a useful setting for this question for three reasons. First, its counties vary meaningfully in precipitation, temperature, inland flood risk, and economic structure. Second, Minnesota is large enough to feature substantial regional heterogeneity but compact enough to support a complete, harmonized county-year panel. Third, it is not the stereotypical case used in climate-economy research. If climate-related local stress is economically visible even in an inland Upper Midwest state, then climate adjustment is likely broader than the most obvious coastal or Sun Belt narratives suggest.

The paper asks four connected questions. First, are annual temperature and precipitation associated with county demographic outcomes such as population growth and net migration? Second, are the same climate variables associated with labor-market outcomes such as employment and unemployment? Third, do local housing and construction margins respond through weaker permitting, a thinner construction business base, or more distressed occupancy signals? Fourth, are these associations larger in counties with higher baseline flood risk? These questions are motivated by a simple idea: climate does not need to produce a dramatic collapse in any single market to matter economically. It can instead work through slower in-migration, weaker construction, lower employment, and lower income, gradually reducing local momentum.

The contribution of the project is threefold. Empirically, it assembles a broad county-year panel linking climate conditions to migration, labor markets, construction, and income outcomes. Methodologically, it formalizes the analysis in a layered econometric framework that moves from baseline fixed-effects models to lag, persistence, and heterogeneity specifications. Conceptually, it offers a disciplined middle ground between purely descriptive climate correlations and a fully structural general equilibrium model. The paper adopts a research design that is formal enough to generate theory-linked predictions and equation-based interpretation, but modest enough to remain credible given the available county-year data.

The main finding is that precipitation is the most consistent adverse climate margin in the Minnesota data. Wetter county-years are associated with weaker population growth, weaker net migration, lower employment, fewer building permits, and fewer construction establishments. Temperature is not irrelevant, but it is less central for those core real-activity outcomes. Instead, temperature appears more strongly in BEA income measures, especially per capita income. The most persuasive heterogeneity result is that precipitation is more harmful for employment in counties with higher inland flood risk. Together, these patterns suggest that climate stress in Minnesota operates through a local adjustment process in which adverse precipitation shocks weaken household inflows, construction activity, and labor demand over time.

The remainder of the paper proceeds as follows. Section 2 develops a local adjustment framework that motivates the empirical design. Section 3 presents the layered econometric system. Section 4 describes the data and descriptive patterns. Section 5 reports the main findings across demographic, labor, construction, and income outcomes. Sections 6 through 8 discuss interpretation, implications, and conclusion.

## 2. A Local Adjustment Framework

This paper is not a full general equilibrium model of the Minnesota economy, and it does not claim to recover deep structural primitives such as substitution elasticities or policy-invariant migration preferences. The county panel is better suited to a disciplined reduced-form framework with an explicit economic mapping from climate conditions to observable local outcomes. In that sense, the paper follows the broader principle that modeling, identification, and empirical interpretation should remain internally consistent even when the design is not fully structural. The goal of this section is to formalize that mapping and to show how the empirical specifications follow from it.

Let county-level climate stress in county c and year t be summarized by

$$
A_ct = ψ_T T_ct + ψ_P P_ct + ψ_PR (P_ct × R_c).     (1)
$$

Here, T_ct is annual average temperature, P_ct is annual precipitation, and R_c is baseline flood risk. The object A_ct is not directly observed; it is a latent index of local climate pressure that combines production-side disruption and amenity-side deterioration. Higher precipitation can raise disruption costs through flood exposure, infrastructure stress, and construction delays. Higher temperature can reduce local productivity or residential desirability, even if its effects are weaker or more outcome-specific.

The key conceptual step is that county outcomes adjust through distinct margins. Household sorting is one margin, construction is another, and labor demand is a third. Let inward migration, building activity, and economic activity respond to climate stress as follows:

$$
InMig_ct = f_H(A_ct),     Build_ct = f_B(A_ct),     Y_ct = f_Y(A_ct, InMig_ct, Build_ct).     (2)
$$

These mappings say that climate conditions can directly affect local outcomes, but they can also affect them indirectly by changing who moves in and how much new construction occurs. A hotter or wetter year can make a county less attractive at the same time that it makes building activity more difficult or more costly. Lower inflows and weaker construction then feed into broader employment and income outcomes.

For empirical work, I use a linearized version of this system:

$$
InMig_ct = α_0 + α_1 A_ct + μ_c + τ_t + ε_ct,     (3)
$$

$$
Build_ct = δ_0 + δ_1 A_ct + μ_c + τ_t + ν_ct,     (4)
$$

$$
Emp_ct = γ_0 + γ_1 A_ct + γ_2 InMig_ct + γ_3 Build_ct + μ_c + τ_t + ω_ct.     (5)
$$

Equations (3) through (5) should not be read as a fully identified simultaneous system. Rather, they provide an organizing structure for the paper’s evidence. The empirical analysis first estimates the reduced-form effect of climate on migration, construction, employment, and related outcomes. It then asks whether the pattern of results across those outcome families is consistent with the adjustment logic in equations (3) through (5).

### Proposition 1

If precipitation lowers county attractiveness for households and raises disruption costs for local construction and labor demand, then in a county fixed-effects framework the reduced-form effect of precipitation on population growth, net in-migration, building permits, and employment should be negative on average. Moreover, if flood exposure amplifies the disruptive effect of precipitation, then the absolute value of the precipitation effect should be larger in counties with higher baseline flood risk.

The proposition is intentionally modest. It does not claim that each outcome must respond equally strongly or in the same year. Instead, it provides a sign prediction for the central outcomes and a heterogeneity prediction for flood-prone counties. The empirical sections of the paper test those predictions directly.

## 3. Econometric Framework

### 3.1 Baseline County Fixed-Effects Model

The baseline empirical model is

$$
Y_ct = β_T T_ct + β_P P_ct + α_c + γ_t + X'_ct δ + ε_ct.     (6)
$$

The dependent variable Y_ct varies across outcome families: population growth, IRS net migration, unemployment, log employment, log income, log permit units, log construction establishments, and related measures. County fixed effects α_c absorb all time-invariant county characteristics, including geography, baseline industrial composition, and persistent institutional differences. Year fixed effects γ_t absorb shocks common to all counties in a given year, including statewide macroeconomic conditions. Standard errors are clustered at the county level to allow for arbitrary serial correlation within counties over time.

The vector X_ct is deliberately parsimonious. In some specifications it is omitted entirely, so that identification comes from within-county changes in climate net of county and year effects. This choice reflects the logic of the project: the goal is not to maximize the number of controls, but to isolate how deviations in climate within a county are associated with deviations in county outcomes.

### 3.2 Outcome-Specific Mapping

The general fixed-effects equation can be specialized to the paper’s main outcome families:

$$
PopGrowth_ct = β_T^P T_ct + β_P^P P_ct + α_c + γ_t + ε_ct^P,     (7)
$$

$$
NetMig_ct = β_T^M T_ct + β_P^M P_ct + α_c + γ_t + ε_ct^M,     (8)
$$

$$
Employment_ct = β_T^E T_ct + β_P^E P_ct + α_c + γ_t + ε_ct^E,     (9)
$$

$$
Permits_ct = β_T^B T_ct + β_P^B P_ct + α_c + γ_t + ε_ct^B.     (10)
$$

These equations formalize the empirical spirit of the paper: compare counties to themselves over time and ask whether hotter or wetter years are associated with weaker demographic and economic outcomes.

### 3.3 Persistence and Distributed Lags

The empirical results suggest that the most important climate relationships are not always purely contemporaneous. Employment, in particular, appears more sensitive to lagged and accumulated precipitation than to same-year precipitation alone. To capture that persistence, I estimate distributed-lag models of the form

$$
Y_ct = Σ_(k=0)^K β_k P_(c,t-k) + Σ_(k=0)^K θ_k T_(c,t-k) + α_c + γ_t + ε_ct,     (11)
$$

with special attention to K = 2. In practice, the paper presents contemporaneous, one-year lag, and three-year average specifications. This design allows climate stress to persist rather than requiring the entire effect to occur in the same calendar year.

### 3.4 Multi-Year Climate Exposure

To capture accumulated exposure more directly, I also estimate moving-average specifications:

$$
Y_ct = θ_T TempMA_ct^(3) + θ_P PrecMA_ct^(3) + α_c + γ_t + ε_ct,     (12)
$$

where

$$
TempMA_ct^(3) = (1/3)(T_ct + T_(c,t-1) + T_(c,t-2)),     (13)
$$

$$
PrecMA_ct^(3) = (1/3)(P_ct + P_(c,t-1) + P_(c,t-2)).     (14)
$$

These moving-average measures are useful when local adjustment is gradual. If wetter conditions erode economic momentum through delayed construction, household sorting, or business responses, then multi-year exposure may be more informative than a same-year climate shock alone.

### 3.5 Flood-Risk Heterogeneity

The paper’s most substantive interaction question is whether precipitation is more harmful in counties with higher baseline flood risk. Let R_c denote a standardized FEMA overall risk score or inland flood risk score. The heterogeneity equation is

$$
Y_ct = β_T T_ct + β_P P_ct + β_TR (T_ct × R_c) + β_PR (P_ct × R_c) + α_c + γ_t + ε_ct.     (15)
$$

Because R_c is time-invariant over the sample, its main effect is absorbed by county fixed effects and is not separately identified. The interaction term β_PR is therefore the key object of interest. A negative estimate of β_PR implies that wetter years are associated with larger adverse outcome shifts in counties with higher baseline flood exposure.

### 3.6 A Dynamic Law of Motion for Local Momentum

To give the paper a forward-looking interpretation without pretending to estimate a full dynamic equilibrium, I also interpret the reduced-form estimates through a simple law of motion for local economic momentum:

$$
g_(c,t+1) = ρ g_ct + φ_T T_ct + φ_P P_ct + φ_PR (P_ct × R_c) + η_(c,t+1).     (16)
$$

Here, g_ct can represent employment growth, income growth, or construction growth. Equation (16) formalizes the idea that county outcomes are persistent and that climate conditions can shift the path of local momentum.

Under this interpretation, expected future activity satisfies

$$
E_t[g_(c,t+τ)] = ρ^τ g_ct + Σ_(s=0)^(τ-1) ρ^s [φ_T T_(c,t+τ-1-s) + φ_P P_(c,t+τ-1-s) + φ_PR P_(c,t+τ-1-s)R_c].     (17)
$$

This is not a structural forecasting equation used for estimation in the paper. Instead, it provides an interpretation of why lagged and moving-average climate measures are economically meaningful: if climate shocks affect county momentum and that momentum is persistent, then the consequences of wet years should unfold over more than one period.

### 3.7 What This Paper Does Not Claim

The framework above is formal, but it is intentionally not a full general equilibrium model. The paper does not impose a CES production function, solve a Bellman equation for forward-looking migration or investment choice, or calibrate a statewide equilibrium with market clearing across sectors. Those would be interesting extensions, but they would require richer identifying assumptions and data than are currently available. The contribution here is instead a serious reduced-form county-economy framework: clearly stated equations, theoretically motivated persistence and heterogeneity, and a mechanism block that maps climate stress into migration, construction, employment, and income outcomes.

## 4. Data and Measurement

The analysis combines multiple sources into a harmonized Minnesota county-year panel. NOAA Climate at a Glance provides the core climate variables: annual average temperature and annual precipitation. FEMA’s National Risk Index provides baseline hazard measures, especially the overall county risk score and the inland flood risk score. Census county population estimates provide annual population totals and population growth rates. IRS county migration files provide inflow, outflow, and net migration measures.

The labor and income extensions add BLS local area unemployment rates, QCEW employment and wage measures, and BEA CAINC1 personal income data. Housing and construction outcomes come from two different sources. The Census Building Permits Survey provides county-level permit counts and values, making it possible to study whether wetter counties build less. County Business Patterns provide construction-sector establishments, employment, and payroll. Finally, HUD-USPS Q4 tract files are aggregated to the county-year level to create supplementary vacancy and no-stat address measures.

All sources are harmonized using five-digit county FIPS codes. This design is central to the project because county names vary across files and over time, while FIPS codes provide a stable geographic crosswalk. The core county panel spans all 87 Minnesota counties over 2011–2023, yielding 1,131 county-year observations before outcome-specific lag restrictions. Samples become shorter when lagged variables or specialized outcome files are required, but the empirical design remains comparable across outcome families. Table 1 reports summary statistics for the core climate, demographic, and risk variables used in the baseline panel.

The climate variables are annual rather than monthly because the paper is designed around county-year adjustment rather than within-year timing. This is appropriate for population, migration, income, and construction outcomes that are observed annually. For persistence, I construct one-year lags and three-year moving averages of temperature and precipitation. Figures 1 through 4 provide descriptive context by plotting statewide average temperature, population growth, and IRS net migration over time, along with a county-level scatterplot of mean IRS net migration against mean precipitation.

The HUD-USPS vacancy data require special caution. The underlying files are tract-level administrative snapshots rather than a designed housing survey, and the documentation warns that longitudinal interpretation is complicated by changes in USPS address management practices, especially around 2011–2012. For that reason, USPS vacancy and no-stat measures are treated as supplementary rather than headline evidence.

## 5. Empirical Findings

### 5.1 Demographic Adjustment

The demographic results are the cleanest starting point for the paper’s overall narrative. Table 2 reports the baseline fixed-effects regressions for population growth and IRS net migration. In those models, precipitation is negatively associated with both outcomes, while temperature is not a robust predictor in the longer panel. This already points to a central theme of the paper: the most consistent climate-related pressure in Minnesota is not hotter years per se, but wetter ones.

The migration decompositions deepen that result. Table 3 decomposes the IRS margin into inflows, outflows, and net migration under baseline, lagged, and moving-average climate specifications. Wetter county-years are more clearly associated with lower in-migration than with higher out-migration. This distinction matters because it suggests that climate stress is not mainly operating through obvious place abandonment. Instead, it appears to weaken a county’s ability to attract new households. That is a quieter adjustment margin, but economically it can still be powerful. If fewer people choose to move in, local demand, labor supply, housing absorption, and business expansion can all weaken over time.

This migration evidence fits the conceptual framework in equations (3) through (5). Climate stress first affects household inflows; those inflows then shape broader local outcomes. The demographic results therefore do more than document one negative coefficient. They identify a plausible mechanism through which climate conditions influence local economic momentum.

### 5.2 Labor-Market Adjustment

The labor-market evidence reinforces the precipitation story, but in a more nuanced way. Table 4 collects the labor-market regressions for employment, unemployment, and wages, while Table 5 reports heterogeneity specifications. Employment levels are lower in wetter county-years, and the relationship is strongest in lagged and multi-year precipitation specifications. That pattern is economically important. It suggests that the negative association between precipitation and employment is not just a same-year coincidence. Instead, it is consistent with an adjustment process in which repeated or accumulated wet conditions gradually weaken local labor demand.

Unemployment, however, is not a simple mirror image of employment. In some lagged or accumulated specifications, higher precipitation is associated with lower unemployment rather than higher unemployment. Taken in isolation, that sign can look puzzling. But alongside the migration results, it becomes more interpretable. A county can experience weaker employment growth without a rising unemployment rate if adjustment occurs partly through slower in-migration, selective out-migration, or changes in labor-force participation. In that sense, the unemployment result does not overturn the labor-market story. It suggests that local adjustment is happening through quantity reallocation across people and places rather than only through a larger stock of unemployed residents.

The flood-risk heterogeneity results are clearest in the employment equations. The negative relationship between precipitation and employment becomes stronger in counties with higher inland flood risk. This is one of the strongest theory-consistent interaction results in the project. It supports the proposition that precipitation is more economically disruptive when counties are structurally more exposed to inland flooding. Importantly, that pattern is visible in employment even though it is not equally strong for every outcome family. That specificity makes the heterogeneity result more credible, not less.

### 5.3 Housing and Construction

The housing and construction evidence provides some of the paper’s strongest and most intuitive economic results. Appendix C summarizes the supplemental housing, construction, income, and USPS blocks estimated using the same baseline, lagged, and moving-average fixed-effects structure. In the Census Building Permits Survey, wetter county-years are associated with fewer permit units in contemporaneous, lagged, and three-year moving-average specifications. Permit values are much less informative. This difference matters because it suggests that precipitation is more clearly connected to the quantity of new construction than to reported dollar values, which are noisier and more sensitive to composition.

County Business Patterns provide a complementary firm-side view of the same mechanism. Wetter county-years are associated with fewer construction establishments, again across contemporaneous, lagged, and multi-year precipitation specifications. Construction employment, by contrast, is weaker and mostly null. That pattern is not a failure of the data. It indicates that the most robust adjustment margin is the extensive margin of local construction activity: fewer firms and fewer permitted units, not necessarily a uniform collapse in every payroll measure.

Taken together, BPS and CBP strongly support the mechanism block of the paper. Precipitation appears to reduce new building activity and thin the construction business base. This is precisely the kind of local transmission channel that can link climate stress to broader county growth. If a county builds less and supports fewer construction establishments, it is less likely to attract new households and more likely to experience weaker downstream employment growth.

The supplementary HUD-USPS evidence is useful but should be interpreted carefully. Vacancy and no-stat measures offer a housing-occupancy perspective, yet their baseline signs are mixed and the series are affected by documented administrative shifts. In the Minnesota data, USPS vacancy outcomes do not provide as clean a climate-distress signal as permits or construction establishments. For that reason, I treat them as contextual rather than central evidence.

### 5.4 Income and Wages

The income results add an important dimension to the paper because they show that temperature is not irrelevant; it simply operates most clearly in broader income measures rather than in the core labor-market or permitting equations. As summarized in Appendix C, BEA per capita income is lower in hotter county-years, and the temperature relationship becomes stronger in lagged and moving-average specifications. Total personal income is lower in counties and years with both higher temperatures and higher precipitation.

These findings matter because they show why average wage regressions alone can be misleading. In the Minnesota data, wage levels are among the weakest outcome families. They do not consistently capture the climate-economy relationship. Broader income measures, however, indicate that household economic well-being is still affected, especially through temperature. This suggests that climate stress can reduce local prosperity even when average wage measures do not move cleanly.

The contrast between wages and income also helps discipline the interpretation of the paper. The project is not finding that every climate margin damages every county outcome symmetrically. Instead, it is finding a more textured economic pattern: precipitation is the main consistent drag on migration, employment, and construction, while temperature shows up more in BEA income outcomes and some housing occupancy measures.

### 5.5 Synthesis Across Outcomes

Across the outcome families, the most coherent interpretation is that precipitation is the dominant adverse climate margin for local real activity in Minnesota. Wetter county-years are associated with slower population growth, weaker net migration, lower employment, fewer permit units, and fewer construction establishments. Temperature matters, but primarily through broader income measures rather than through the headline real-activity margins.

This synthesis is exactly what the layered econometric framework was designed to test. The baseline fixed-effects equations identify the broad climate-outcome relationships. The lag and moving-average equations show that the precipitation effect is persistent rather than purely contemporaneous. The interaction equations show that precipitation is more harmful for employment in counties with higher inland flood risk. The mechanism equations organize the evidence into a county-economy narrative in which climate stress affects migration and construction, which in turn shape broader local performance.

## 6. Interpretation, Identification, and Scope

The estimates in this paper should be interpreted as within-county associations between climate conditions and local outcomes after absorbing county and year fixed effects. This is a strong design for a county-year panel, but it is not a randomized experiment. The paper therefore does not claim that every coefficient recovers a structural causal parameter in the narrowest sense. What it does claim is that the empirical pattern is coherent across multiple outcome families and consistent with a specific local adjustment mechanism.

That coherence is important. A single negative precipitation coefficient in one table could be noise. But a repeated pattern in population growth, migration, employment, permits, and construction establishments is much harder to dismiss. The fact that the results line up most clearly around precipitation, and that flood-risk heterogeneity appears where theory would most naturally predict it, strengthens the case that the paper is capturing meaningful local climate adjustment rather than arbitrary statistical fluctuation.

At the same time, the paper remains disciplined about what the data can support. It does not estimate a formal migration-choice model, a construction investment Bellman equation, or a statewide equilibrium with endogenous prices and quantities in every market. Those would be valuable future extensions. For the current project, the right level of ambition is a rigorous county fixed-effects framework with explicit theory-motivated dynamics and heterogeneity. In that sense, the paper is closer to applied local macro or reduced-form urban economics than to a fully structural quantitative geography model.

This positioning is a strength, not a weakness. It means the paper uses advanced mathematical structure where it adds real value: to formalize hypotheses, discipline identification, and connect empirical patterns across multiple margins. It avoids adding decorative theory that the data cannot credibly estimate.

## 7. Policy and Research Implications

The results suggest that climate-related economic pressure in Minnesota should not be understood solely as a disaster-response problem. If precipitation weakens in-migration, reduces construction activity, and lowers employment, then climate resilience is also a question of long-run local competitiveness. Counties with higher flood exposure may face not only more physical disruption but also weaker ability to attract residents, sustain business formation, and maintain economic momentum.

This has two practical implications. First, housing and infrastructure adaptation may have local growth effects that are larger than a narrow property-damage framework would imply. If wet conditions suppress permitting and shrink the construction business base, then climate adaptation can matter for future housing supply as well as current resilience. Second, local labor-market deterioration may show up before it appears in simple unemployment statistics. Policymakers who look only at unemployment rates may miss adjustment already visible in migration, employment levels, and construction activity.

For future research, the most promising extensions would deepen rather than replace the current framework. A natural next step would be to estimate more flexible nonlinear climate effects or threshold effects around very wet years. Another extension would connect county-level housing prices to the construction and migration margins already documented here. A more ambitious path would be to embed the reduced-form results in a formally estimated forward-looking migration or housing-investment model. But such work should build on the reduced-form patterns established in this paper, not skip over them.

## 8. Conclusion

This paper develops and estimates a county-year framework for studying climate risk and local economic adjustment in Minnesota. The analysis combines NOAA climate data with demographic, labor-market, income, construction, and supplementary housing-occupancy measures. The empirical strategy uses county fixed effects, year fixed effects, lag structures, moving-average climate exposure, and flood-risk interactions to characterize the relationship between local climate conditions and local outcomes.

The central result is that precipitation is the most consistent adverse climate margin in the Minnesota data. Wetter county-years are associated with slower population growth, weaker net migration, lower employment, fewer building permits, and fewer construction establishments. The employment penalty is larger in counties with higher inland flood risk. Temperature remains economically meaningful, but it appears more clearly in broader income measures than in the main labor and construction outcomes. Overall, the evidence suggests that climate stress in Minnesota works less through sudden visible collapse and more through gradual erosion of local economic momentum: fewer people arriving, fewer projects getting built, a thinner construction base, and less income being generated over time.

That conclusion is important both substantively and methodologically. Substantively, it shows that climate-economy adjustment is visible even in an inland Upper Midwest state. Methodologically, it shows that a serious county-level climate paper can be both formal and honest: it can use a layered mathematical framework, proposition-style predictions, persistence equations, and mechanism mapping without pretending to estimate a full general equilibrium model that the data do not support. That is the paper’s intended contribution.

## References

- Bureau of Economic Analysis. Local Area Personal Income and Employment, CAINC1.
- Bureau of Labor Statistics. Local Area Unemployment Statistics.
- Federal Emergency Management Agency. National Risk Index.
- Holmes, Thomas J., and Holger Sieg. 2014. “Structural Estimation in Urban Economics.” Prepared for the *Handbook of Regional and Urban Economics*.
- Internal Revenue Service. Statistics of Income County-to-County Migration Data.
- U.S. Census Bureau. Building Permits Survey.
- U.S. Census Bureau. County Business Patterns.
- U.S. Census Bureau. County Population and Housing Unit Estimates.
- U.S. Department of Housing and Urban Development. USPS Vacancy Data.
- U.S. National Centers for Environmental Information, NOAA Climate at a Glance.

## Appendix A. Main Outcome Families Used in the Paper

The paper’s empirical sections are organized around the following county-year outcomes:

- Population growth and total population from Census county estimates.
- IRS net migration, inflows, and outflows from county migration files.
- Unemployment rates from BLS local area unemployment statistics.
- Employment and wages from QCEW.
- Personal income and per capita income from BEA CAINC1.
- Permit units and permit values from the Census Building Permits Survey.
- Construction establishments, construction employment, and construction payroll from County Business Patterns.
- Vacancy and no-stat address measures from HUD-USPS Q4 files, treated as supplementary.

## Appendix B. Notes on Empirical Interpretation

Three points are especially important for interpreting the equations in the main text.

First, time-invariant FEMA risk measures are absorbed by county fixed effects, so only their interactions with time-varying climate variables are identified in the fixed-effects regressions.

Second, the mechanism system is a conceptual map rather than a claim of point-identified causal mediation. The paper uses reduced-form evidence across multiple outcome families to evaluate whether the pattern is consistent with climate operating through migration and construction.

Third, the dynamic law of motion is interpretive rather than fully structural. It motivates the empirical importance of lagged and moving-average climate exposure, but it is not presented as a calibrated statewide equilibrium model.

## Appendix C. Summary of Supplemental Outcome Results

The broader outcome blocks use the same county fixed-effects, year fixed-effects, clustered standard-error framework described in Section 3. Their substantive results can be summarized as follows.

- Building permits: precipitation is negative and statistically significant for permit units in contemporaneous, one-year lag, and three-year moving-average specifications. Permit values are weaker and generally not robust.
- Construction establishments: County Business Patterns show fewer construction establishments in wetter county-years across contemporaneous, lagged, and multi-year precipitation specifications.
- Construction employment: the CBP construction employment equations are weaker and mostly null, suggesting that the firm-count margin is more informative than payroll employment in this setting.
- BEA income: per capita income is lower in hotter county-years, especially in lagged and moving-average specifications. Total personal income is lower with both higher temperature and higher precipitation.
- USPS vacancy: vacancy and no-stat address measures add context but should be treated as supplementary because their signs are mixed and the series are vulnerable to documented administrative changes in USPS address classification.
