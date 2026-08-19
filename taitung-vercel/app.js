const state = { crops: [], selectedCrop: "", barChart: null, lineChart: null };
const $ = (selector) => document.querySelector(selector);
const formatNumber = (value) => Number(value || 0).toLocaleString("zh-TW", { maximumFractionDigits: 1 });

function showError(message) { $("#error-message").textContent = message; $("#error-message").hidden = false; }
function clearError() { $("#error-message").hidden = true; }

async function getJson(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.error || `API 請求失敗（${response.status}）`);
  return payload;
}

function renderCropButtons() {
  $("#crop-buttons").innerHTML = state.crops.map((crop) => `<button class="crop-btn ${crop === state.selectedCrop ? "active" : ""}" data-crop="${crop}">${crop}</button>`).join("");
  document.querySelectorAll(".crop-btn").forEach((button) => button.addEventListener("click", () => loadCrop(button.dataset.crop)));
}

function makeChartOptions(yTitle) {
  return { responsive: true, maintainAspectRatio: false, interaction: { mode: "index", intersect: false }, plugins: { legend: { position: "top" } }, scales: { y: { beginAtZero: true, title: { display: true, text: yTitle } } } };
}

function renderCharts(payload) {
  const data = payload.data || {};
  const records = data.records || [];
  const labels = records.map((row) => row.date);
  const wholesale = records.map((row) => row.origin_price);
  const retail = records.map((row) => row.market_price);
  const common = { labels, datasets: [] };
  if (state.barChart) state.barChart.destroy();
  if (state.lineChart) state.lineChart.destroy();
  state.barChart = new Chart($("#bar-chart"), { type: "bar", data: { ...common, datasets: [{ label: "批發價", data: wholesale, backgroundColor: "#5b7fff" }, { label: `估算零售價 (${data.multiplier || 1.4}x)`, data: retail, backgroundColor: "#ff7b63" }] }, options: makeChartOptions("價格（元／公斤）") });
  state.lineChart = new Chart($("#line-chart"), { type: "line", data: { ...common, datasets: [{ label: "批發價", data: wholesale, borderColor: "#6366f1", backgroundColor: "#6366f133", pointBackgroundColor: "#6366f1", tension: .3, fill: true }] }, options: makeChartOptions("價格（元／公斤）") });
}

function renderTable(payload) {
  const records = payload.data?.records || [];
  $("#price-table").innerHTML = records.map((row) => `<tr><td>${row.date}</td><td>${formatNumber(row.origin_price)}</td><td>${formatNumber(row.market_price)}</td><td>${formatNumber(row.market_price - row.origin_price)}</td><td>${row.source || "農業部農產品交易行情"}</td></tr>`).join("");
}

async function loadCrop(crop) {
  state.selectedCrop = crop; renderCropButtons(); clearError();
  $("#status-message").textContent = "資料抓取中…";
  try {
    const payload = await getJson(`/api/products/${encodeURIComponent(crop)}`);
    renderCharts(payload); renderTable(payload);
    const status = payload.data?.status || {};
    $("#status-message").textContent = `${status.icon || "✓"} ${status.title || "資料狀態："}${status.message || "資料已更新"}`;
    $("#status-message").className = `status-message ${status.class || "success"}`;
    $("#updated-at").textContent = `最後更新時間：${payload.data?.updated_at || "剛剛"}`;
  } catch (error) { $("#status-message").textContent = "資料載入失敗"; showError(error.message); }
}

(async function init() {
  try {
    const payload = await getJson("/api/crops");
    state.crops = payload.crops || [];
    state.selectedCrop = state.crops.includes("釋迦") ? "釋迦" : state.crops[0];
    renderCropButtons();
    await loadCrop(state.selectedCrop);
  } catch (error) { showError(error.message); }
})();
