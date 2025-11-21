/* Archivo javascript para estadisticas_geolocalizacion
   Depende de las siguientes variables globales definidas en la plantilla:
   - window.ESTADISTICAS_CONFIG  (objeto con URLs de la API)
 */

let map, heatmap, poligonoComuna;
let markers = [];
let chartDelitos, chartTorta, chartLinea, chartUnidades, chartComunas, chartCriticos;

function getFiltros() {
  return {
    comuna: document.getElementById("comunaSelect")?.value || "",
    delito: document.getElementById("delitoSelect")?.value || "",
    fecha_inicio: document.getElementById("fechaDesde")?.value || "",
    fecha_fin: document.getElementById("fechaHasta")?.value || ""
  };
}
function qs(params) {
  const p = new URLSearchParams();
  Object.entries(params).forEach(([k,v]) => { if (v) p.append(k,v); });
  const s = p.toString();
  return s ? ("?" + s) : "";
}
async function fetchJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status} en ${url}`);
  return await res.json();
}
function safeDestroy(chartRef) { if (chartRef) { chartRef.destroy(); } }

function construirURLHeatmap(comuna = "") {
  const f = getFiltros();
  if (!window.ESTADISTICAS_CONFIG) return '';
  if (comuna) {
    return window.ESTADISTICAS_CONFIG.api_eventos_por_comuna + qs({ comuna: comuna, delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
  }
  return window.ESTADISTICAS_CONFIG.api_eventos_geolocalizados + qs({ delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
}

async function cargarHeatmap(comuna = "") {
  try {
    if (heatmap) heatmap.setMap(null);
    markers.forEach(m => m.setMap(null));
    markers = [];

    const data = await fetchJSON(construirURLHeatmap(comuna));
    document.getElementById("kpi-total").textContent = Array.isArray(data) ? data.length : 0;
    document.getElementById("kpi-comuna").textContent = comuna || "Todas";

    const heatmapData = data.map(e => new google.maps.LatLng(e.lat, e.lng));
    data.forEach(evento => {
      const marker = new google.maps.Marker({ position: { lat: evento.lat, lng: evento.lng }, map, icon: { path: google.maps.SymbolPath.CIRCLE, scale: 4, fillColor: "#ff0000", fillOpacity: 0.0, strokeWeight: 0 } });
      const infowindow = new google.maps.InfoWindow({ content: `<div style="font-size:14px;"><strong>Delito:</strong> ${evento.delito || "-"}<br><strong>Dirección:</strong> ${evento.direccion || "-"}<br><strong>Unidad:</strong> ${evento.unidad || "-"}</div>` });
      marker.addListener("mouseover", () => infowindow.open(map, marker));
      marker.addListener("mouseout", () => infowindow.close());
      markers.push(marker);
    });

    heatmap = new google.maps.visualization.HeatmapLayer({ data: heatmapData, radius: 25 });
    heatmap.setMap(map);
  } catch (e) { console.error("Error en cargarHeatmap:", e); }
}

async function cargarPoligono(comuna = "") {
  try {
    if (poligonoComuna) { poligonoComuna.setMap(null); poligonoComuna = null; }
    if (!comuna) return;
    const url = window.ESTADISTICAS_CONFIG.geojson_comuna_nombre + qs({ comuna: comuna });
    const geojson = await fetchJSON(url);
    const feature = geojson?.features?.[0]; if (!feature) return;
    let coords = [];
    if (feature.geometry?.type === "Polygon") coords = feature.geometry.coordinates[0];
    else if (feature.geometry?.type === "MultiPolygon") coords = feature.geometry.coordinates[0][0];
    if (!coords.length) return;
    const path = coords.map(pair => ({ lng: pair[0], lat: pair[1] }));
    poligonoComuna = new google.maps.Polygon({ paths: path, strokeColor: "#1b5e20", strokeOpacity: 0.9, strokeWeight: 2, fillColor: "#66bb6a", fillOpacity: 0.08 });
    poligonoComuna.setMap(map);
    const bounds = new google.maps.LatLngBounds(); path.forEach(p => bounds.extend(p)); map.fitBounds(bounds);
  } catch (e) { console.error("Error en cargarPoligono:", e); }
}

// Funciones para graficos: requieren Chart.js y los endpoints configurados
async function cargarGraficoDelitos(comuna = "") {
  try {
    const f = getFiltros();
    const url = window.ESTADISTICAS_CONFIG.api_estadisticas_por_delito + qs({ comuna: comuna || "", delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
    const data = await fetchJSON(url);
    document.getElementById("kpi-delitos").textContent = Array.isArray(data) ? data.length : 0;
    const labels = data.map(d => d.nombre);
    const valores = data.map(d => d.total);
    const colores = data.map((_, i) => `hsl(${(i*57)%360},60%,60%)`);
    const ctxBar = document.getElementById("graficoDelitos").getContext("2d");
    const ctxPie = document.getElementById("graficoTorta").getContext("2d");
    safeDestroy(chartDelitos); safeDestroy(chartTorta);
    chartDelitos = new Chart(ctxBar, { type: "bar", data: { labels, datasets: [{ label: "Cantidad", data: valores, backgroundColor: "#66bb6a", borderColor: "#2e7d32" }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } } });
    chartTorta = new Chart(ctxPie, { type: "pie", data: { labels, datasets: [{ data: valores, backgroundColor: colores }] }, options: { plugins: { legend: { position: "bottom" } } } });
  } catch (e) { console.error("Error en cargarGraficoDelitos:", e); }
}

async function cargarGraficoLinea(comuna = "") {
  try {
    const f = getFiltros();
    const url = window.ESTADISTICAS_CONFIG.api_eventos_tiempo + qs({ comuna: comuna || "", delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
    const data = await fetchJSON(url);
    const ctx = document.getElementById("graficoLinea").getContext("2d"); safeDestroy(chartLinea);
    chartLinea = new Chart(ctx, { type: "line", data: { labels: data.fechas || [], datasets: [{ label: "Delitos por día", data: data.valores || [], borderColor: "#2e7d32", backgroundColor: "rgba(46,125,50,0.2)", tension: 0.3, fill: true }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } } });
  } catch (e) { console.error("Error en cargarGraficoLinea:", e); }
}

async function cargarTopUnidades(comuna = "") {
  try {
    const f = getFiltros();
    const url = window.ESTADISTICAS_CONFIG.api_top_unidades + qs({ comuna: comuna || "", delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
    const data = await fetchJSON(url);
    const labels = data.map(d => d.nombre_unidad);
    const valores = data.map(d => d.total);
    const ctx = document.getElementById("graficoTopUnidades").getContext("2d"); safeDestroy(chartUnidades);
    chartUnidades = new Chart(ctx, { type: "bar", data: { labels, datasets: [{ label: "Delitos", data: valores, backgroundColor: "#81c784" }] }, options: { responsive: true, indexAxis: 'y', plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } } });
  } catch (e) { console.error(e); }
}

async function cargarComunas() {
  try {
    const f = getFiltros();
    const url = window.ESTADISTICAS_CONFIG.api_top_comunas + qs({ delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
    const data = await fetchJSON(url);
    const labels = data.map(c => c.nombre_comuna);
    const valores = data.map(c => c.total);
    const ctx = document.getElementById("graficoComunas").getContext("2d"); safeDestroy(chartComunas);
    chartComunas = new Chart(ctx, { type: "bar", data: { labels, datasets: [{ label: "Cantidad de Delitos", data: valores, backgroundColor: "#a5d6a7", borderColor: "#2e7d32", borderWidth: 1 }] }, options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } } });
  } catch (e) { console.error(e); }
}

async function cargarGraficoHoras(comuna = "") {
  try {
    const f = getFiltros();
    const url = window.ESTADISTICAS_CONFIG.api_eventos_hora_dia + qs({ comuna: comuna || "", delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
    const data = await fetchJSON(url);
    const ctx = document.getElementById("graficoHoras").getContext("2d"); if (window.chartHoras) window.chartHoras.destroy();
    window.chartHoras = new Chart(ctx, { type: "line", data: { labels: data.horas || [], datasets: [{ label: "Delitos registrados por hora", data: data.valores || [], borderColor: "#1b5e20", backgroundColor: "rgba(46,125,50,0.2)", pointBackgroundColor: "#2e7d32", pointRadius: 4, tension: 0.35, fill: true }] }, options: { responsive: true, plugins: { legend: { display: false }, title: { display: true, text: "📈 Distribución horaria de delitos", color: "#1b5e20", font: { size: 16, weight: "bold" } }, tooltip: { callbacks: { label: function(context) { return ` ${context.parsed.y} delitos a las ${context.label}`; } } } }, scales: { x: { title: { display: true, text: "Hora del día", color: "#1b5e20" }, ticks: { color: "#2e7d32" } }, y: { beginAtZero: true, title: { display: true, text: "Cantidad de delitos", color: "#1b5e20" }, ticks: { stepSize: 1, color: "#2e7d32" }, grid: { color: "rgba(0,0,0,0.1)" } } } } });
  } catch (e) { console.error(e); }
}

async function cargarCriticos(comuna = "") {
  try {
    const f = getFiltros();
    const url = window.ESTADISTICAS_CONFIG.api_porcentaje_delitos_criticos + qs({ comuna: comuna || "", delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
    const data = await fetchJSON(url);
    const ctx = document.getElementById("graficoCriticos").getContext("2d"); safeDestroy(chartCriticos);
    const crit = Number(data.porcentaje || 0);
    chartCriticos = new Chart(ctx, { type: "doughnut", data: { labels: ["Críticos", "No críticos"], datasets: [{ data: [crit, Math.max(0, 100-crit)], backgroundColor: ["#d32f2f", "#81c784"] }] }, options: { plugins: { legend: { position: "bottom" } } } });
  } catch (e) { console.error(e); }
}

async function cargarGraficoDiaNoche(comuna = "") {
  try {
    const f = getFiltros();
    const url = window.ESTADISTICAS_CONFIG.api_eventos_dia_vs_noche + qs({ comuna: comuna, delito: f.delito, fecha_inicio: f.fecha_inicio, fecha_fin: f.fecha_fin });
    const data = await fetchJSON(url);
    const ctx = document.getElementById("graficoDiaNoche").getContext("2d"); if (window.chartDiaNoche) window.chartDiaNoche.destroy();
    window.chartDiaNoche = new Chart(ctx, { type: "doughnut", data: { labels: ["Día (06:00–18:00)", "Noche (18:00–06:00)"], datasets: [{ data: [data.dia, data.noche], backgroundColor: ["#81c784", "#388e3c"] }] }, options: { plugins: { legend: { position: "bottom" } } } });
  } catch(e) { console.error(e); }
}

async function cargarGraficoTendenciaMensual(comuna = "") {
  try {
    const url = window.ESTADISTICAS_CONFIG.api_tendencia_mensual;
    const data = await fetchJSON(url);
    const ctx = document.getElementById("graficoTendenciaMensual").getContext("2d"); if (window.chartTendencia) window.chartTendencia.destroy();
    window.chartTendencia = new Chart(ctx, { type: "line", data: { labels: data.labels, datasets: [{ label: "Total de delitos", data: data.valores, borderColor: "#1b5e20", backgroundColor: "rgba(46,125,50,0.2)", tension: 0.3, fill: true }] }, options: { plugins: { legend: { display: false } } } });
  } catch(e) { console.error(e); }
}

async function cargarTopDelitosMes() {
  try {
    const url = window.ESTADISTICAS_CONFIG.api_top_delitos_mes_actual;
    const data = await fetchJSON(url);
    const ctx = document.getElementById("graficoTopDelitosMes").getContext("2d"); if (window.chartTopMes) window.chartTopMes.destroy();
    window.chartTopMes = new Chart(ctx, { type: "bar", data: { labels: data.labels, datasets: [{ label: "Delitos", data: data.valores, backgroundColor: "#81c784" }] }, options: { indexAxis: 'y', plugins: { legend: { display: false } } } });
  } catch(e) { console.error(e); }
}

function exportarPDF() {
  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF();
  pdf.text("Reporte de Estadísticas", 10, 10);
  pdf.text("Generado: " + new Date().toLocaleString(), 10, 20);
  pdf.save("reporte_estadisticas.pdf");
}
function exportarExcel() {
  const tabla = document.getElementById("tablaUnidades");
  const wb = XLSX.utils.table_to_book(tabla, { sheet: "Resumen" });
  XLSX.writeFile(wb, "reporte_estadisticas.xlsx");
}

function aplicarFiltros() {
  const { comuna, fecha_inicio, fecha_fin } = getFiltros();
  document.getElementById("kpi-fechas").textContent = (fecha_inicio || "—") + " a " + (fecha_fin || "—");
  cargarPoligono(comuna);
  cargarHeatmap(comuna);
  cargarGraficoDelitos(comuna);
  cargarGraficoLinea(comuna);
  cargarTopUnidades(comuna);
  cargarComunas();
  cargarCriticos(comuna);
  cargarGraficoHoras(comuna);
  cargarGraficoDiaNoche();
  cargarGraficoTendenciaMensual();
  cargarTopDelitosMes();
}

function initMap() {
  map = new google.maps.Map(document.getElementById("map"), { center: { lat: -33.45, lng: -70.66 }, zoom: 12 });
  cargarHeatmap();
  cargarGraficoDelitos();
  cargarGraficoLinea();
  cargarTopUnidades();
  cargarComunas();
  cargarCriticos();
  cargarGraficoHoras();
  cargarGraficoDiaNoche();
  cargarGraficoTendenciaMensual();
  cargarTopDelitosMes();
}

window.initMap = initMap;

document.addEventListener('DOMContentLoaded', function () {
  // conectar botón aplicar filtros
  const btn = document.querySelector('.filtros-container button');
  if (btn) btn.addEventListener('click', aplicarFiltros);
});
