const DATA = window.NORTH_STAR_ATLAS;
const GEOJSON = window.MN_COUNTIES_GEOJSON;

const COMPOSITE_SCORE_KEYS = new Set([
  "overall_signal_score",
  "exposure_score",
  "economic_pressure_score",
  "housing_headwind_score",
]);

const OFFICIAL_SCORE_KEYS = new Set(["risk_score", "inland_flood_risk_score", "resl_score"]);

const METRICS = {
  overall_signal_score: {
    label: "Overall climate-economic pressure",
    description:
      "Exploratory 2011-2023 county score combining precipitation exposure, official flood risk, slower migration, higher unemployment, weaker permitting, fewer construction establishments, and higher residential vacancy.",
    yearly: false,
    higherIsWorse: true,
    formatter: (v) => formatScore(v),
  },
  exposure_score: {
    label: "Exposure score",
    description:
      "Exploratory 2011-2023 score built from mean precipitation, FEMA overall risk, and FEMA inland flood risk.",
    yearly: false,
    higherIsWorse: true,
    formatter: (v) => formatScore(v),
  },
  economic_pressure_score: {
    label: "Economic pressure score",
    description:
      "Exploratory 2011-2023 score built from lower population growth, weaker net migration, and higher unemployment.",
    yearly: false,
    higherIsWorse: true,
    formatter: (v) => formatScore(v),
  },
  housing_headwind_score: {
    label: "Housing headwind score",
    description:
      "Exploratory 2011-2023 score built from weaker permit activity, fewer construction establishments, and higher residential vacancy.",
    yearly: false,
    higherIsWorse: true,
    formatter: (v) => formatScore(v),
  },
  risk_score: {
    label: "FEMA overall risk score",
    description: "Official county-level FEMA National Risk Index overall risk score.",
    yearly: false,
    higherIsWorse: true,
    formatter: (v) => formatScore(v),
  },
  inland_flood_risk_score: {
    label: "FEMA inland flood risk score",
    description: "Official county-level FEMA National Risk Index inland flood risk score.",
    yearly: false,
    higherIsWorse: true,
    formatter: (v) => formatScore(v),
  },
  resl_score: {
    label: "FEMA resilience score",
    description: "Official FEMA resilience score. Higher values indicate more resilience, not more pressure.",
    yearly: false,
    higherIsWorse: false,
    formatter: (v) => formatScore(v),
  },
  precip_total: {
    label: "Annual precipitation",
    description: "Annual precipitation total from the NOAA county-year panel.",
    yearly: true,
    higherIsWorse: true,
    formatter: (v) => `${formatNumber(v, 1)} in`,
  },
  temp_avg: {
    label: "Average annual temperature",
    description: "Average annual temperature from the NOAA county-year panel.",
    yearly: true,
    higherIsWorse: null,
    formatter: (v) => `${formatNumber(v, 1)} °F`,
  },
  pop_growth_rate: {
    label: "Population growth rate",
    description: "Annual county population growth rate from Census population estimates.",
    yearly: true,
    higherIsWorse: false,
    formatter: (v) => `${formatSigned(v, 2)}%`,
  },
  net_migration_rate: {
    label: "Net migration per 1,000 residents",
    description: "IRS-based net migration rate using exemptions per 1,000 residents.",
    yearly: true,
    higherIsWorse: false,
    formatter: (v) => formatSigned(v, 1),
  },
  unemp_rate: {
    label: "Unemployment rate",
    description: "Annual county unemployment rate from BLS local area unemployment statistics.",
    yearly: true,
    higherIsWorse: true,
    formatter: (v) => `${formatNumber(v, 1)}%`,
  },
  qcew_employment_per_1000: {
    label: "QCEW employment per 1,000 residents",
    description: "Covered employment per 1,000 residents from the county QCEW panel.",
    yearly: true,
    higherIsWorse: false,
    formatter: (v) => formatNumber(v, 1),
  },
  qcew_avg_wkly_wage: {
    label: "Average weekly wage",
    description: "Average weekly wage from county QCEW annual files.",
    yearly: true,
    higherIsWorse: false,
    formatter: (v) => currency(v, 0),
  },
  bea_pc_income: {
    label: "BEA per capita income",
    description: "BEA county per capita personal income.",
    yearly: true,
    higherIsWorse: false,
    formatter: (v) => currency(v, 0),
  },
  bps_units_per_1000: {
    label: "Permit units per 1,000 residents",
    description: "Residential permit units from Census BPS scaled by county population.",
    yearly: true,
    higherIsWorse: false,
    formatter: (v) => formatNumber(v, 2),
  },
  cbp_const_estabs_per_10k: {
    label: "Construction establishments per 10,000 residents",
    description: "County Business Patterns construction establishments scaled by county population.",
    yearly: true,
    higherIsWorse: false,
    formatter: (v) => formatNumber(v, 2),
  },
  usps_res_vacancy_pct: {
    label: "Residential USPS vacancy rate",
    description: "HUD USPS residential vacancy rate using Q4 county aggregates.",
    yearly: true,
    higherIsWorse: true,
    formatter: (v) => `${formatNumber(v, 2)}%`,
  },
};

const TREND_METRICS = [
  "precip_total",
  "temp_avg",
  "pop_growth_rate",
  "net_migration_rate",
  "unemp_rate",
  "bps_units_per_1000",
  "cbp_const_estabs_per_10k",
  "usps_res_vacancy_pct",
  "bea_pc_income",
];

const FINDINGS = {
  precip: {
    title: "Precipitation model signals",
    subtitle:
      "Baseline county fixed-effects models show precipitation as the clearest drag on migration, employment, and construction activity.",
    takeaway:
      "Across the headline baseline models, wetter county-years line up with lower net migration, lower employment, fewer permit units, and fewer construction establishments.",
    note:
      "Bars show estimate divided by its standard error. Farther from zero means a clearer directional signal; hover to see the underlying coefficient and standard error.",
    xAxisLabel: "Signal strength (estimate / standard error)",
    items: [
      {
        label: "Permit units",
        coef: -0.002051,
        se: 0.0004999,
        outcome: "Census building permit units (log)",
        interpretation: "More precipitation is associated with fewer new permit units.",
      },
      {
        label: "Employment level",
        coef: -0.0001691,
        se: 0.0000576,
        outcome: "QCEW employment (log)",
        interpretation: "Wetter county-years are associated with lower employment.",
      },
      {
        label: "Construction establishments",
        coef: -0.000233,
        se: 0.0000906,
        outcome: "CBP construction establishments (log)",
        interpretation: "Wetter county-years are associated with fewer construction firms.",
      },
      {
        label: "Net migration",
        coef: -0.0264,
        se: 0.0128,
        outcome: "IRS net migration rate",
        interpretation: "Wetter county-years are associated with weaker net migration.",
      },
      {
        label: "USPS no-stat rate",
        coef: 0.0075237,
        se: 0.0031172,
        outcome: "HUD USPS no-stat rate",
        interpretation: "Precipitation is also associated with more no-stat addresses, a noisier housing-distress signal.",
      },
    ],
  },
  temp: {
    title: "Temperature model signals",
    subtitle:
      "Temperature shows up more clearly in broader income and housing occupancy measures than in the core employment outcomes.",
    takeaway:
      "Hotter county-years are most clearly linked to lower BEA income and lower USPS vacancy, while the baseline employment relationship is close to zero.",
    note:
      "These are county fixed-effects results. The income estimates come from log models, while the USPS estimates are vacancy-rate relationships, so use the chart to compare direction and clarity rather than raw size.",
    xAxisLabel: "Signal strength (estimate / standard error)",
    items: [
      {
        label: "USPS vacancy rate",
        coef: -0.4156762,
        se: 0.1387784,
        outcome: "HUD USPS vacancy rate",
        interpretation: "Hotter county-years are associated with lower vacancy rates.",
      },
      {
        label: "Residential vacancy",
        coef: -0.4265286,
        se: 0.143567,
        outcome: "HUD USPS residential vacancy rate",
        interpretation: "Residential vacancy also moves lower in hotter county-years.",
      },
      {
        label: "BEA total income",
        coef: -0.011823,
        se: 0.0040891,
        outcome: "BEA total personal income (log)",
        interpretation: "Hotter county-years are associated with lower total personal income.",
      },
      {
        label: "BEA per capita income",
        coef: -0.0099723,
        se: 0.0036938,
        outcome: "BEA per capita personal income (log)",
        interpretation: "Per capita income also falls in hotter county-years.",
      },
      {
        label: "Employment level",
        coef: 0.0010163,
        se: 0.0052243,
        outcome: "QCEW employment (log)",
        interpretation: "The baseline employment response to temperature is close to zero.",
      },
    ],
  },
  risk: {
    title: "Flood-risk employment sensitivity",
    subtitle:
      "The employment heterogeneity model implies that precipitation has a more negative employment effect in counties with higher inland flood risk.",
    note:
      "Bars show the modeled percent change in employment from an additional inch of precipitation, using the ln employment interaction model with inland flood risk.",
    xAxisLabel: "Modeled employment effect from +1 inch precipitation (%)",
    baseCoef: -0.0000105,
    interactionCoef: -0.00000332,
  },
};

const stateSeriesByYear = new Map(DATA.statewide.map((row) => [row.year, row]));
const countiesByFips = new Map(DATA.counties.map((county) => [county.fips, county]));

const state = {
  metricKey: "overall_signal_score",
  trendMetricKey: "precip_total",
  findingsView: "precip",
  year: DATA.metadata.latest_year,
  selectedCountyFips: getInitialCounty(),
  hoveredCountyFips: null,
};

const dom = {
  metricSelect: document.querySelector("#metric-select"),
  trendMetricSelect: document.querySelector("#trend-metric-select"),
  yearRange: document.querySelector("#year-range"),
  yearValue: document.querySelector("#year-value"),
  resetView: document.querySelector("#reset-view"),
  metricTitle: document.querySelector("#metric-title"),
  mapSubtitle: document.querySelector("#map-subtitle"),
  metricDescription: document.querySelector("#metric-description"),
  metricMeaning: document.querySelector("#metric-meaning"),
  metricChips: document.querySelector("#metric-chips"),
  guideWhatTitle: document.querySelector("#guide-what-title"),
  guideWhatText: document.querySelector("#guide-what-text"),
  guideReadTitle: document.querySelector("#guide-read-title"),
  guideReadText: document.querySelector("#guide-read-text"),
  guideUseTitle: document.querySelector("#guide-use-title"),
  guideUseText: document.querySelector("#guide-use-text"),
  countyName: document.querySelector("#county-name"),
  countyContext: document.querySelector("#county-context"),
  overallScore: document.querySelector("#overall-score"),
  overallScoreNote: document.querySelector("#overall-score-note"),
  floodScore: document.querySelector("#flood-score"),
  floodScoreNote: document.querySelector("#flood-score-note"),
  popGrowthScore: document.querySelector("#pop-growth-score"),
  popGrowthNote: document.querySelector("#pop-growth-note"),
  permitScore: document.querySelector("#permit-score"),
  permitNote: document.querySelector("#permit-note"),
  detailList: document.querySelector("#detail-list"),
  rankingBody: document.querySelector("#ranking-body"),
  rankingTitle: document.querySelector("#ranking-title"),
  rankingValueLabel: document.querySelector("#ranking-value-label"),
  findingsTitle: document.querySelector("#findings-title"),
  findingsSubtitle: document.querySelector("#findings-subtitle"),
  findingsTakeaway: document.querySelector("#findings-takeaway"),
  findingsNote: document.querySelector("#findings-note"),
  findingsButtons: Array.from(document.querySelectorAll("[data-findings-view]")),
  countySearch: document.querySelector("#county-search"),
  countyOptions: document.querySelector("#county-options"),
  coverageYears: document.querySelector("#coverage-years"),
  legend: document.querySelector("#legend"),
};

dom.coverageYears.textContent = `${DATA.metadata.years[0]}-${DATA.metadata.years.at(-1)}`;

populateControls();

const map = L.map("map", {
  zoomControl: false,
  attributionControl: false,
  scrollWheelZoom: true,
  minZoom: 5.25,
  maxZoom: 9,
});

L.control.zoom({ position: "topright" }).addTo(map);

const countyLayer = L.geoJSON(GEOJSON, {
  style: styleFeature,
  onEachFeature(feature, layer) {
    layer.on({
      click: () => selectCounty(feature.properties.GEOID),
      mouseover: () => highlightCounty(feature.properties.GEOID, layer),
      mouseout: () => resetCountyStyle(feature.properties.GEOID, layer),
    });
  },
}).addTo(map);

map.fitBounds(countyLayer.getBounds(), { padding: [12, 12] });

const tooltip = L.tooltip({
  permanent: false,
  direction: "top",
  offset: [0, -8],
  className: "county-tooltip",
});

const trendChart = new Chart(document.querySelector("#trend-chart"), {
  type: "line",
  data: {
    labels: [],
    datasets: [
      {
        label: "Selected county",
        data: [],
        borderColor: "#f07b52",
        backgroundColor: "rgba(240, 123, 82, 0.18)",
        borderWidth: 3,
        pointRadius: 2,
        pointHoverRadius: 4,
        tension: 0.28,
      },
      {
        label: "Minnesota average",
        data: [],
        borderColor: "#63c7ae",
        backgroundColor: "rgba(99, 199, 174, 0.08)",
        borderWidth: 2,
        pointRadius: 0,
        tension: 0.28,
        borderDash: [6, 5],
      },
    ],
  },
  options: {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: {
        position: "bottom",
        labels: {
          usePointStyle: true,
          boxWidth: 10,
          color: "#dbe7e2",
        },
      },
      tooltip: {
        backgroundColor: "rgba(7, 14, 18, 0.96)",
        titleColor: "#f5f8f3",
        bodyColor: "#dbe7e2",
        borderColor: "rgba(255,255,255,0.08)",
        borderWidth: 1,
        callbacks: {
          label(context) {
            const metric = METRICS[state.trendMetricKey];
            return `${context.dataset.label}: ${metric.formatter(context.raw)}`;
          },
        },
      },
    },
    scales: {
      y: {
        ticks: {
          color: "#9cb2ad",
          callback(value) {
            return compactTick(value, METRICS[state.trendMetricKey]);
          },
        },
        grid: {
          color: "rgba(255, 255, 255, 0.08)",
        },
      },
      x: {
        ticks: {
          color: "#9cb2ad",
        },
        grid: {
          display: false,
        },
      },
    },
  },
});

const findingsChart = new Chart(document.querySelector("#findings-chart"), {
  type: "bar",
  data: {
    labels: [],
    datasets: [
      {
        data: [],
        backgroundColor: [],
        borderRadius: 999,
        borderSkipped: false,
        barThickness: 16,
      },
    ],
  },
  options: {
    indexAxis: "y",
    responsive: true,
    maintainAspectRatio: false,
    animation: false,
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        backgroundColor: "rgba(7, 14, 18, 0.96)",
        titleColor: "#f5f8f3",
        bodyColor: "#dbe7e2",
        borderColor: "rgba(255,255,255,0.08)",
        borderWidth: 1,
        callbacks: {
          title(items) {
            return items[0]?.label || "";
          },
          label(context) {
            const item = findingsChart.$items?.[context.dataIndex];
            if (!item) return "";
            if (state.findingsView === "risk") {
              return `Modeled effect: ${formatSigned(context.raw, 3)}% employment per +1 inch precipitation`;
            }
            return `Signal strength: ${formatSigned(context.raw, 2)}`;
          },
          afterLabel(context) {
            const item = findingsChart.$items?.[context.dataIndex];
            if (!item) return [];
            if (state.findingsView === "risk") {
              return [
                `Inland flood risk score: ${formatNumber(item.risk, 1)}`,
                item.isSelected ? "Selected county" : "Higher risk pushes the effect more negative",
              ];
            }
            return [
              `Coefficient: ${formatCoefficient(item.coef)}`,
              `Std. error: ${formatUnsignedCoefficient(item.se)}`,
              item.outcome,
              item.interpretation,
            ];
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: "#9cb2ad",
          callback(value) {
            return state.findingsView === "risk" ? `${formatSigned(value, 2)}%` : formatSigned(value, 1);
          },
        },
        title: {
          display: true,
          color: "#9cb2ad",
          font: {
            size: 11,
            weight: "600",
          },
          text: FINDINGS.precip.xAxisLabel,
        },
        grid: {
          color(context) {
            return context.tick.value === 0 ? "rgba(255, 255, 255, 0.18)" : "rgba(255, 255, 255, 0.06)";
          },
        },
      },
      y: {
        ticks: {
          color: "#dbe7e2",
        },
        grid: {
          display: false,
        },
      },
    },
  },
});

wireEvents();
render();

function populateControls() {
  Object.entries(METRICS).forEach(([key, metric]) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = metric.label;
    dom.metricSelect.append(option);
  });

  TREND_METRICS.forEach((key) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = METRICS[key].label;
    dom.trendMetricSelect.append(option);
  });

  DATA.counties
    .slice()
    .sort((a, b) => a.county_name.localeCompare(b.county_name))
    .forEach((county) => {
      const option = document.createElement("option");
      option.value = county.county_name;
      dom.countyOptions.append(option);
    });
}

function wireEvents() {
  dom.metricSelect.value = state.metricKey;
  dom.trendMetricSelect.value = state.trendMetricKey;
  dom.yearRange.value = state.year;
  syncFindingsButtons();

  dom.metricSelect.addEventListener("change", (event) => {
    state.metricKey = event.target.value;
    render();
  });

  dom.trendMetricSelect.addEventListener("change", (event) => {
    state.trendMetricKey = event.target.value;
    renderTrend();
  });

  dom.yearRange.addEventListener("input", (event) => {
    state.year = Number(event.target.value);
    render();
  });

  dom.resetView.addEventListener("click", () => {
    state.metricKey = "overall_signal_score";
    state.trendMetricKey = "precip_total";
    state.year = DATA.metadata.latest_year;
    state.selectedCountyFips = getInitialCounty();
    dom.metricSelect.value = state.metricKey;
    dom.trendMetricSelect.value = state.trendMetricKey;
    dom.yearRange.value = state.year;
    map.fitBounds(countyLayer.getBounds(), { padding: [12, 12] });
    render();
  });

  dom.countySearch.addEventListener("change", (event) => {
    const value = event.target.value.trim().toLowerCase();
    const match = DATA.counties.find((county) => county.county_name.toLowerCase() === value);
    if (match) {
      selectCounty(match.fips);
    }
  });

  dom.findingsButtons.forEach((button) => {
    button.addEventListener("click", () => {
      state.findingsView = button.dataset.findingsView;
      syncFindingsButtons();
      renderFindings();
    });
  });
}

function render() {
  const metric = METRICS[state.metricKey];
  dom.metricTitle.textContent = metric.label;
  dom.metricDescription.textContent = metric.description;
  dom.metricMeaning.textContent = buildMetricMeaning(metric);
  dom.mapSubtitle.textContent = buildMapSubtitle(metric);
  dom.metricChips.innerHTML = buildMetricChips(metric, state.metricKey);
  dom.yearValue.textContent = metric.yearly ? state.year : "All years";
  dom.yearRange.disabled = !metric.yearly;
  dom.yearRange.closest(".year-control").style.opacity = metric.yearly ? "1" : "0.45";

  countyLayer.setStyle(styleFeature);
  updateLegend();
  updateGuideCards(metric);
  renderCountyProfile();
  renderRanking();
  renderTrend();
  renderFindings();
}

function renderCountyProfile() {
  const county = countiesByFips.get(state.selectedCountyFips);
  if (!county) return;
  const statewideNetMigration = getStatewideValue("net_migration_rate");
  const statewidePermits = getStatewideValue("bps_units_per_1000");
  const statewidePopGrowth = getStatewideValue("pop_growth_rate");
  const overallRank = rankDescending(county.overall_signal_score, "overall_signal_score");
  const floodRank = rankDescending(county.inland_flood_risk_score, "inland_flood_risk_score");

  dom.countyName.textContent = county.county_name;
  dom.countySearch.value = county.county_name;
  dom.countyContext.textContent = buildCountyContext(county, {
    overallRank,
    floodRank,
    statewideNetMigration,
    statewidePermits,
  });
  dom.overallScore.textContent = formatScore(county.overall_signal_score);
  dom.overallScoreNote.textContent = `${ordinal(overallRank)} of ${DATA.counties.length} statewide • exploratory score, not a percent`;
  dom.floodScore.textContent = formatScore(county.inland_flood_risk_score);
  dom.floodScoreNote.textContent = `${ordinal(floodRank)} highest inland flood risk statewide`;
  dom.popGrowthScore.textContent = METRICS.pop_growth_rate.formatter(getMetricValue(county, "pop_growth_rate"));
  dom.popGrowthNote.textContent = `${state.year} • ${relativeToState(getMetricValue(county, "pop_growth_rate"), statewidePopGrowth)} the state average`;
  dom.permitScore.textContent = METRICS.bps_units_per_1000.formatter(getMetricValue(county, "bps_units_per_1000"));
  dom.permitNote.textContent = `${state.year} • ${relativeToState(getMetricValue(county, "bps_units_per_1000"), statewidePermits)} the state average`;

  const items = [
    ["Official overall risk score", county.risk_score, METRICS.risk_score],
    ["Official resilience score", county.resl_score, METRICS.resl_score],
    ["Average precipitation (2011-2023)", county.avg_precip_total, METRICS.precip_total],
    ["Average net migration", county.avg_net_migration_rate, METRICS.net_migration_rate],
    ["Unemployment rate", getMetricValue(county, "unemp_rate"), METRICS.unemp_rate],
    ["QCEW weekly wage", getMetricValue(county, "qcew_avg_wkly_wage"), METRICS.qcew_avg_wkly_wage],
    ["BEA per capita income", getMetricValue(county, "bea_pc_income"), METRICS.bea_pc_income],
    ["Construction establishments", getMetricValue(county, "cbp_const_estabs_per_10k"), METRICS.cbp_const_estabs_per_10k],
    ["Residential vacancy", getMetricValue(county, "usps_res_vacancy_pct"), METRICS.usps_res_vacancy_pct],
  ];

  dom.detailList.innerHTML = "";
  items.forEach(([label, value, metric]) => {
    const row = document.createElement("div");
    row.className = "detail-item";
    row.innerHTML = `<label>${label}</label><strong>${metric.formatter(value)}</strong>`;
    dom.detailList.append(row);
  });
}

function renderTrend() {
  const countySeries = DATA.series[state.selectedCountyFips] || [];
  const labels = countySeries.map((row) => row.year);
  const countyData = countySeries.map((row) => row[state.trendMetricKey]);
  const statewideData = DATA.statewide.map((row) => row[state.trendMetricKey]);

  trendChart.data.labels = labels;
  trendChart.data.datasets[0].label = countiesByFips.get(state.selectedCountyFips)?.county_name || "Selected county";
  trendChart.data.datasets[0].data = countyData;
  trendChart.data.datasets[1].data = statewideData;
  trendChart.update();
}

function renderRanking() {
  const metric = METRICS[state.metricKey];
  const rows = DATA.counties
    .map((county) => ({
      county,
      value: getMetricValue(county, state.metricKey),
    }))
    .filter((row) => row.value !== null && row.value !== undefined)
    .sort((a, b) => b.value - a.value);

  dom.rankingTitle.textContent = `${metric.label} ranking`;
  dom.rankingValueLabel.textContent = metric.yearly ? `${state.year} value` : "Score";
  dom.rankingBody.innerHTML = "";

  rows.forEach((row, idx) => {
    const tr = document.createElement("tr");
    if (row.county.fips === state.selectedCountyFips) {
      tr.classList.add("active");
    }
    tr.innerHTML = `
      <td>${idx + 1}</td>
      <td>${row.county.county_name}</td>
      <td>${metric.formatter(row.value)}</td>
    `;
    tr.addEventListener("click", () => selectCounty(row.county.fips));
    dom.rankingBody.append(tr);
  });
}

function renderFindings() {
  syncFindingsButtons();
  const view = FINDINGS[state.findingsView];
  dom.findingsTitle.textContent = view.title;
  dom.findingsSubtitle.textContent = view.subtitle;
  dom.findingsNote.textContent = view.note;

  if (state.findingsView === "risk") {
    const items = buildRiskSensitivityItems();
    const selected = items.find((item) => item.isSelected);
    const statewideAvg = average(
      DATA.counties.map(
        (county) => 100 * (view.baseCoef + view.interactionCoef * county.inland_flood_risk_score),
      ),
    );

    dom.findingsTakeaway.textContent = selected
      ? `${selected.label}'s modeled employment response is ${formatSigned(selected.value, 3)}% for an extra inch of precipitation, compared with a statewide average of ${formatSigned(statewideAvg, 3)}%. Higher inland flood risk pushes the precipitation effect further negative.`
      : "Higher inland flood risk pushes the modeled employment effect of precipitation further negative.";

    findingsChart.data.labels = items.map((item) => item.label);
    findingsChart.data.datasets[0].data = items.map((item) => item.value);
    findingsChart.data.datasets[0].backgroundColor = items.map((item) =>
      item.isSelected ? "#5da7d1" : "rgba(240, 123, 82, 0.78)",
    );
    findingsChart.$items = items;
    findingsChart.options.scales.x.title.text = view.xAxisLabel;
    findingsChart.options.scales.x.max = 0;
    findingsChart.options.scales.x.min = Math.min(...items.map((item) => item.value)) * 1.18;
  } else {
    const items = view.items.map((item) => ({
      ...item,
      value: item.coef / item.se,
    }));

    dom.findingsTakeaway.textContent = view.takeaway;
    findingsChart.data.labels = items.map((item) => item.label);
    findingsChart.data.datasets[0].data = items.map((item) => item.value);
    findingsChart.data.datasets[0].backgroundColor = items.map((item) =>
      item.value >= 0 ? "rgba(99, 199, 174, 0.78)" : "rgba(240, 123, 82, 0.78)",
    );
    findingsChart.$items = items;
    findingsChart.options.scales.x.title.text = view.xAxisLabel;
    const maxAbs = Math.max(...items.map((item) => Math.abs(item.value)), 1);
    findingsChart.options.scales.x.min = -maxAbs * 1.18;
    findingsChart.options.scales.x.max = maxAbs * 1.18;
  }

  findingsChart.update();
}

function syncFindingsButtons() {
  dom.findingsButtons.forEach((button) => {
    button.classList.toggle("is-active", button.dataset.findingsView === state.findingsView);
  });
}

function updateLegend() {
  const metric = METRICS[state.metricKey];
  const values = DATA.counties
    .map((county) => getMetricValue(county, state.metricKey))
    .filter((value) => value !== null && value !== undefined)
    .sort((a, b) => a - b);

  const thresholds = buildThresholds(values);
  const palette = metric.higherIsWorse === false ? goodPalette() : badPalette();

  dom.legend.innerHTML = `<h4>${metric.yearly ? `${state.year} scale` : "County scale"}</h4>`;
  palette.forEach((color, idx) => {
    const start = idx === 0 ? values[0] : thresholds[idx - 1];
    const end = thresholds[idx] ?? values.at(-1);
    const row = document.createElement("div");
    row.className = "legend-row";
    row.innerHTML = `
      <span class="legend-swatch" style="background:${color}"></span>
      <span>${metric.formatter(start)} to ${metric.formatter(end)}</span>
    `;
    dom.legend.append(row);
  });
}

function selectCounty(fips) {
  state.selectedCountyFips = fips;
  const layer = findLayerByFips(fips);
  if (layer) {
    map.fitBounds(layer.getBounds(), { padding: [24, 24], maxZoom: 8.2 });
  }
  render();
}

function highlightCounty(fips, layer) {
  state.hoveredCountyFips = fips;
  layer.setStyle({
    weight: 2.5,
    color: "#f5f8f3",
    fillOpacity: 0.88,
  });

  const county = countiesByFips.get(fips);
  const metric = METRICS[state.metricKey];
  const value = county ? getMetricValue(county, state.metricKey) : null;
  const label = county ? county.county_name : "County";
  tooltip.setContent(`<strong>${label}</strong><br>${metric.formatter(value)}`);
  layer.bindTooltip(tooltip).openTooltip();
}

function resetCountyStyle(fips, layer) {
  state.hoveredCountyFips = null;
  countyLayer.resetStyle(layer);
}

function findLayerByFips(fips) {
  let match = null;
  countyLayer.eachLayer((layer) => {
    if (layer.feature?.properties?.GEOID === fips) {
      match = layer;
    }
  });
  return match;
}

function styleFeature(feature) {
  const county = countiesByFips.get(feature.properties.GEOID);
  const value = county ? getMetricValue(county, state.metricKey) : null;
  const color = getFillColor(value, state.metricKey);
  const isSelected = feature.properties.GEOID === state.selectedCountyFips;
  return {
    color: isSelected ? "#f5f8f3" : "rgba(238, 243, 233, 0.28)",
    weight: isSelected ? 2.6 : 0.8,
    fillColor: color,
    fillOpacity: value == null ? 0.38 : 0.82,
  };
}

function getMetricValue(county, metricKey) {
  const metric = METRICS[metricKey];
  if (!county) return null;
  if (!metric.yearly) {
    return county[metricKey];
  }
  const series = DATA.series[county.fips] || [];
  const row = series.find((entry) => entry.year === state.year);
  return row ? row[metricKey] : null;
}

function getFillColor(value, metricKey) {
  const metric = METRICS[metricKey];
  if (value == null || Number.isNaN(value)) {
    return "rgba(255, 255, 255, 0.08)";
  }

  const values = DATA.counties
    .map((county) => getMetricValue(county, metricKey))
    .filter((entry) => entry !== null && entry !== undefined)
    .sort((a, b) => a - b);
  const thresholds = buildThresholds(values);
  const palette = metric.higherIsWorse === false ? goodPalette() : badPalette();

  for (let i = 0; i < thresholds.length; i += 1) {
    if (value <= thresholds[i]) {
      return palette[i];
    }
  }
  return palette.at(-1);
}

function buildThresholds(values) {
  if (!values.length) return [0, 0, 0, 0, 0];
  const q = [0.2, 0.4, 0.6, 0.8];
  return q.map((pct) => values[Math.min(values.length - 1, Math.floor(values.length * pct))]);
}

function badPalette() {
  return ["#56453b", "#8e654b", "#bd744a", "#e76b46", "#ff8c66"];
}

function goodPalette() {
  return ["#2a403c", "#2e665c", "#37927f", "#4dc4a4", "#81f3cd"];
}

function buildMapSubtitle(metric) {
  if (!metric.yearly) {
    return "This lens compares counties using full-period county profiles rather than a single annual snapshot.";
  }
  return `This lens is showing county values for ${state.year}. Click a county to compare its trend with the statewide average.`;
}

function buildMetricMeaning(metric) {
  if (COMPOSITE_SCORE_KEYS.has(state.metricKey)) {
    return "This is an exploratory score on a 0 to 100 county scale. It is a relative ranking across Minnesota, not a percentage.";
  }
  if (OFFICIAL_SCORE_KEYS.has(state.metricKey)) {
    return "This is an official FEMA score reported on a 0 to 100 scale. It is a score, not a percentage.";
  }
  if (metric.higherIsWorse === true) {
    return "Warmer orange counties are showing higher values. For this lens, higher generally means more exposure, stress, or headwind.";
  }
  if (metric.higherIsWorse === false) {
    return "Brighter green counties are showing higher values. For this lens, higher generally means more activity, resilience, or strength.";
  }
  return "This lens is descriptive rather than directional, so color is showing relative position across counties rather than a built-in good or bad score.";
}

function updateGuideCards(metric) {
  dom.guideWhatTitle.textContent = metric.yearly ? `${state.year} county snapshot` : "Long-run county profile";
  dom.guideWhatText.textContent = metric.yearly
    ? `Each county is shaded using its ${state.year} value for ${metric.label.toLowerCase()}.`
    : `Each county is shaded using its full-period score for ${metric.label.toLowerCase()}, built from the project’s county-level data.`;

  dom.guideReadTitle.textContent = metric.higherIsWorse === false ? "Greens signal stronger positions" : "Warm tones signal more pressure";
  dom.guideReadText.textContent = buildMetricMeaning(metric);

  dom.guideUseTitle.textContent = "Three easy steps";
  dom.guideUseText.textContent =
    "Pick a lens, click a county on the map or ranking table, then use the trend viewer to see whether that county is moving with or away from the statewide pattern.";
}

function buildMetricChips(metric, metricKey) {
  const chips = [];
  chips.push(metric.yearly ? `${state.year} snapshot` : "2011-2023 county profile");

  if (COMPOSITE_SCORE_KEYS.has(metricKey)) {
    chips.push("Exploratory score");
    chips.push("0-100 relative scale");
  } else if (OFFICIAL_SCORE_KEYS.has(metricKey)) {
    chips.push("Official FEMA score");
    chips.push("0-100 score");
  } else {
    chips.push("Observed county measure");
  }

  if (metric.higherIsWorse === true) {
    chips.push("Higher = more pressure");
  } else if (metric.higherIsWorse === false) {
    chips.push("Higher = stronger position");
  } else {
    chips.push("Relative county comparison");
  }

  return chips.map((chip) => `<span class="metric-chip">${chip}</span>`).join("");
}

function buildCountyContext(county, context) {
  const netMigration = getMetricValue(county, "net_migration_rate");
  const permits = getMetricValue(county, "bps_units_per_1000");
  const migrationPhrase = relativeToState(netMigration, context.statewideNetMigration);
  const permitPhrase = relativeToState(permits, context.statewidePermits);

  return `${county.county_name} ranks ${ordinal(context.overallRank)} of ${DATA.counties.length} on the dashboard's overall pressure score. Its inland flood risk is ${ordinal(context.floodRank)} highest statewide, net migration is ${migrationPhrase} the Minnesota average, and permit activity is ${permitPhrase} the statewide pace in ${state.year}.`;
}

function buildRiskSensitivityItems() {
  const view = FINDINGS.risk;
  const selectedCounty = countiesByFips.get(state.selectedCountyFips);

  const items = DATA.counties
    .map((county) => ({
      label: county.county_name,
      fips: county.fips,
      risk: county.inland_flood_risk_score,
      value: 100 * (view.baseCoef + view.interactionCoef * county.inland_flood_risk_score),
      isSelected: county.fips === state.selectedCountyFips,
    }))
    .sort((a, b) => a.value - b.value);

  const top = items.slice(0, 7);
  if (selectedCounty && !top.some((item) => item.fips === selectedCounty.fips)) {
    top.push(items.find((item) => item.fips === selectedCounty.fips));
  } else if (items[7]) {
    top.push(items[7]);
  }

  return top.sort((a, b) => a.value - b.value);
}

function getInitialCounty() {
  const sorted = DATA.counties
    .slice()
    .sort((a, b) => b.overall_signal_score - a.overall_signal_score);
  return sorted[0].fips;
}

function rankDescending(value, metricKey) {
  const values = DATA.counties
    .map((county) => county[metricKey])
    .filter((entry) => entry !== null && entry !== undefined)
    .sort((a, b) => b - a);
  const index = values.findIndex((entry) => entry <= value);
  return index === -1 ? values.length : index + 1;
}

function percentile(value, metricKey) {
  const values = DATA.counties
    .map((county) => county[metricKey])
    .filter((entry) => entry !== null && entry !== undefined)
    .sort((a, b) => a - b);
  const index = values.findIndex((entry) => entry >= value);
  if (index === -1) return 100;
  return Math.round((index / Math.max(values.length - 1, 1)) * 100);
}

function formatNumber(value, decimals = 1) {
  if (value == null || Number.isNaN(value)) return "No data";
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatSigned(value, decimals = 1) {
  if (value == null || Number.isNaN(value)) return "No data";
  return Number(value).toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
    signDisplay: "always",
  });
}

function currency(value, decimals = 0) {
  if (value == null || Number.isNaN(value)) return "No data";
  return Number(value).toLocaleString(undefined, {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function compactTick(value, metric) {
  if (metric === METRICS.bea_pc_income || metric === METRICS.qcew_avg_wkly_wage) {
    return currency(value, 0);
  }
  return formatNumber(value, 1);
}

function getStatewideValue(metricKey) {
  const row = stateSeriesByYear.get(state.year);
  return row ? row[metricKey] : null;
}

function average(values) {
  const filtered = values.filter((value) => value !== null && value !== undefined && !Number.isNaN(value));
  if (!filtered.length) return null;
  return filtered.reduce((sum, value) => sum + value, 0) / filtered.length;
}

function relativeToState(value, stateValue) {
  if ([value, stateValue].some((entry) => entry == null || Number.isNaN(entry))) {
    return "in line with";
  }
  const tolerance = Math.max(Math.abs(stateValue) * 0.05, 0.1);
  if (Math.abs(value - stateValue) <= tolerance) {
    return "roughly in line with";
  }
  return value > stateValue ? "above" : "below";
}

function formatCoefficient(value) {
  if (value == null || Number.isNaN(value)) return "No data";
  const absValue = Math.abs(value);
  let decimals = 3;
  if (absValue < 0.1) decimals = 4;
  if (absValue < 0.01) decimals = 5;
  if (absValue < 0.001) decimals = 6;
  return formatSigned(value, decimals);
}

function formatUnsignedCoefficient(value) {
  if (value == null || Number.isNaN(value)) return "No data";
  const absValue = Math.abs(value);
  let decimals = 3;
  if (absValue < 0.1) decimals = 4;
  if (absValue < 0.01) decimals = 5;
  if (absValue < 0.001) decimals = 6;
  return formatNumber(value, decimals);
}

function formatScore(value) {
  if (value == null || Number.isNaN(value)) return "No data";
  return `${formatNumber(value, 1)} / 100`;
}

function ordinal(value) {
  if (value == null || Number.isNaN(value)) return "";
  const n = Number(value);
  const mod10 = n % 10;
  const mod100 = n % 100;
  if (mod10 === 1 && mod100 !== 11) return `${n}st`;
  if (mod10 === 2 && mod100 !== 12) return `${n}nd`;
  if (mod10 === 3 && mod100 !== 13) return `${n}rd`;
  return `${n}th`;
}
