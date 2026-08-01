// Màn Tiến độ — docs/plan.md §1.3 màn 9. 4 stat + phân bố theo mốc điểm/chủ đề
// tính THẬT từ words.json + Store. Biểu đồ 7 ngày GIỮ TĨNH như mockup (chốt ở
// M8, §12.3 Q4) — chỉ cột cuối (hôm nay) dùng số liệu thật (mastered.size),
// y hệt cách mockup làm.
import { Store } from "./store.js";

const WEEK_FAKE_SERIES = [3, 5, 2, 6, 4, 7];

const root = document.querySelector("[data-progress-stats]");
if (root) {
  init();
}

async function init() {
  const totalEntries = parseInt(root.getAttribute("data-total-entries"), 10) || 0;
  const masteredIds = Store.get("masteredIds") || [];
  const masteredCount = masteredIds.length;
  const reviewedCount = Object.keys(Store.get("srs") || {}).length;
  const pct = totalEntries ? Math.round((masteredCount / totalEntries) * 100) : 0;

  setText("[data-progress-mastered]", String(masteredCount));
  setText("[data-progress-pct]", String(pct));
  setText("[data-progress-reviewed]", String(reviewedCount));

  renderWeekChart(masteredCount);

  let words = [];
  try {
    const res = await fetch("../words/index.json");
    words = await res.json();
  } catch (e) {
    return;
  }

  const masteredSet = new Set(masteredIds);
  renderLevelDistribution(words, masteredSet);
  renderTopicDistribution(words, masteredSet);
}

function renderWeekChart(masteredCount) {
  const series = WEEK_FAKE_SERIES.concat([masteredCount]);
  const max = Math.max.apply(null, series.concat([1]));
  document.querySelectorAll("[data-week-bar]").forEach((bar, i) => {
    const pct = Math.round((series[i] / max) * 100);
    bar.style.height = pct + "%";
  });
}

function renderLevelDistribution(words, masteredSet) {
  const byLevel = {};
  words.forEach((w) => {
    byLevel[w.v] = byLevel[w.v] || { done: 0, total: 0 };
    byLevel[w.v].total += 1;
    if (masteredSet.has(w.k)) byLevel[w.v].done += 1;
  });

  document.querySelectorAll("[data-level-row]").forEach((row) => {
    const level = row.getAttribute("data-level-row");
    const stats = byLevel[level] || { done: 0, total: 0 };
    const pct = stats.total ? Math.round((stats.done / stats.total) * 100) : 0;
    row.querySelector("[data-level-fill]").style.width = pct + "%";
    row.querySelector("[data-level-count]").textContent = stats.done + "/" + stats.total;
  });
}

function renderTopicDistribution(words, masteredSet) {
  const byTopic = {};
  words.forEach((w) => {
    byTopic[w.t] = byTopic[w.t] || { done: 0, total: 0 };
    byTopic[w.t].total += 1;
    if (masteredSet.has(w.k)) byTopic[w.t].done += 1;
  });

  document.querySelectorAll("[data-topic-cell]").forEach((cell) => {
    const topic = cell.getAttribute("data-topic-cell");
    const stats = byTopic[topic] || { done: 0, total: 0 };
    const pct = stats.total ? Math.round((stats.done / stats.total) * 100) : 0;
    cell.querySelector("[data-topic-fill]").style.width = pct + "%";
    cell.querySelector("[data-topic-count]").textContent = stats.done + "/" + stats.total;
  });
}

function setText(selector, text) {
  const el = document.querySelector(selector);
  if (el) el.textContent = text;
}
