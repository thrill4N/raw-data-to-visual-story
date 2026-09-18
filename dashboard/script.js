const INK = "#1B1D1B";
const INK_SOFT = "#4A4A46";
const RETAIL = "#2B5B6B";
const RETAIL_TINT = "#DCE8EA";
const CLINICAL = "#8C5A2B";
const FLAG = "#B23A3A";
const HAIRLINE = "#D8D5CB";

const baseFont = { family: "IBM Plex Sans, sans-serif", color: INK_SOFT, size: 13 };
const baseLayout = {
  paper_bgcolor: "transparent",
  plot_bgcolor: "transparent",
  font: baseFont,
  margin: { t: 24, r: 20, b: 40, l: 56 },
  hoverlabel: { font: { family: "IBM Plex Sans, sans-serif" } },
};
const plotConfig = { displayModeBar: false, responsive: true };

function fmtMoney(n) {
  return "$" + Math.round(n).toLocaleString("en-US");
}

async function loadData() {
  const [eco, drug] = await Promise.all([
    fetch("data/ecommerce.json").then(r => r.json()),
    fetch("data/drug.json").then(r => r.json()),
  ]);
  renderRetail(eco);
  renderClinical(drug);
}

function renderRetail(eco) {
  document.getElementById("stat-revenue").textContent = fmtMoney(eco.total_revenue);

  // Revenue by month
  const months = Object.keys(eco.revenue_by_month);
  const revenues = Object.values(eco.revenue_by_month);
  Plotly.newPlot("chart-revenue-month", [{
    x: months, y: revenues, type: "scatter", mode: "lines",
    line: { color: RETAIL, width: 2.5 },
    fill: "tozeroy", fillcolor: "rgba(43,91,107,0.08)",
    hovertemplate: "%{x}<br>" + "$%{y:,.0f}<extra></extra>",
  }], { ...baseLayout, title: { text: "Monthly revenue", font: { size: 14, color: INK } },
        xaxis: { showgrid: false, tickangle: -45, nticks: 12 },
        yaxis: { showgrid: true, gridcolor: HAIRLINE, tickprefix: "$" } },
    plotConfig);

  // Category revenue
  const cats = Object.keys(eco.category_revenue);
  const catVals = Object.values(eco.category_revenue);
  Plotly.newPlot("chart-category", [{
    x: catVals, y: cats, type: "bar", orientation: "h",
    marker: { color: RETAIL },
    hovertemplate: "%{y}<br>$%{x:,.0f}<extra></extra>",
  }], { ...baseLayout, title: { text: "Revenue by category", font: { size: 14, color: INK } },
        xaxis: { showgrid: true, gridcolor: HAIRLINE, tickprefix: "$" },
        yaxis: { autorange: "reversed" } },
    plotConfig);

  // Status donut
  Plotly.newPlot("chart-status", [{
    labels: Object.keys(eco.status_breakdown), values: Object.values(eco.status_breakdown),
    type: "pie", hole: 0.55,
    marker: { colors: [RETAIL, "#7FA6AC", "#C7D9CE"] },
    textfont: { size: 11 },
  }], { ...baseLayout, title: { text: "Order status", font: { size: 13, color: INK } }, showlegend: true,
        legend: { orientation: "h", y: -0.15, font: { size: 10 } } },
    plotConfig);

  // Payment method
  const pm = Object.entries(eco.payment_method_breakdown);
  Plotly.newPlot("chart-payment", [{
    x: pm.map(d => d[0]), y: pm.map(d => d[1]), type: "bar",
    marker: { color: RETAIL_TINT, line: { color: RETAIL, width: 1.2 } },
  }], { ...baseLayout, title: { text: "Payment method", font: { size: 13, color: INK } },
        xaxis: { showgrid: false }, yaxis: { showgrid: true, gridcolor: HAIRLINE } },
    plotConfig);

  // Top cities
  const cityEntries = Object.entries(eco.top_cities).slice(0, 6);
  Plotly.newPlot("chart-cities", [{
    x: cityEntries.map(d => d[1]), y: cityEntries.map(d => d[0]),
    type: "bar", orientation: "h",
    marker: { color: RETAIL },
  }], { ...baseLayout, title: { text: "Top cities by orders", font: { size: 13, color: INK } },
        xaxis: { showgrid: true, gridcolor: HAIRLINE },
        yaxis: { autorange: "reversed" } },
    plotConfig);
}

function renderClinical(drug) {
  const drugColors = {
    DrugY: CLINICAL, DrugX: "#B98750", DrugA: "#D9C2A0",
    DrugB: "#A97748", DrugC: "#6E4A24",
  };
  const byDrug = {};
  drug.scatter_points.forEach(p => {
    byDrug[p.drug] = byDrug[p.drug] || { x: [], y: [] };
    byDrug[p.drug].x.push(p.age);
    byDrug[p.drug].y.push(p.na_to_k);
  });
  const traces = Object.entries(byDrug).map(([name, pts]) => ({
    x: pts.x, y: pts.y, mode: "markers", type: "scatter", name,
    marker: { color: drugColors[name] || "#999", size: 8, opacity: 0.85 },
  }));
  // threshold line
  traces.push({
    x: [10, 80], y: [15, 15], mode: "lines", type: "scatter",
    line: { color: FLAG, width: 1.5, dash: "dot" },
    name: "Na/K = 15", hoverinfo: "skip",
  });

  Plotly.newPlot("chart-scatter", traces, {
    ...baseLayout,
    title: { text: "Age vs. sodium-to-potassium ratio, by drug", font: { size: 14, color: INK } },
    xaxis: { title: "Age", showgrid: true, gridcolor: HAIRLINE },
    yaxis: { title: "Na to K ratio", showgrid: true, gridcolor: HAIRLINE },
    legend: { orientation: "h", y: -0.2 },
  }, plotConfig);

  const dd = Object.entries(drug.drug_distribution).sort((a, b) => b[1] - a[1]);
  Plotly.newPlot("chart-drug-dist", [{
    x: dd.map(d => d[1]), y: dd.map(d => d[0]), type: "bar", orientation: "h",
    marker: { color: dd.map(d => drugColors[d[0]] || CLINICAL) },
  }], { ...baseLayout, title: { text: "Patients per drug", font: { size: 13, color: INK } },
        xaxis: { showgrid: true, gridcolor: HAIRLINE },
        yaxis: { autorange: "reversed" } },
    plotConfig);
}

loadData();
