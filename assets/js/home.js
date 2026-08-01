// Màn Home — docs/plan.md §1.3 màn 1. Đã thuộc/Tiến độ tính thật từ Store;
// streak & mục tiêu hôm nay GIỮ TĨNH (chốt ở M8, §12.3 Q4) nên render thẳng ở
// template, không cần JS. "Bài học hiện tại" = chương chưa đọc đầu tiên theo
// readIds, fallback chương 1 (§12.3 Q9).
import { Store } from "./store.js";

const statsRoot = document.querySelector("[data-home-stats]");
if (statsRoot) {
  const totalEntries = parseInt(statsRoot.getAttribute("data-total-entries"), 10) || 0;
  const masteredCount = (Store.get("masteredIds") || []).length;
  const pct = totalEntries ? Math.round((masteredCount / totalEntries) * 100) : 0;

  setText("[data-home-mastered]", String(masteredCount));
  setText("[data-home-progress-pct]", String(pct));
}

const currentLessonSection = document.querySelector("[data-home-current-lesson]");
const lessonsDataEl = document.getElementById("home-lessons");
if (currentLessonSection && lessonsDataEl) {
  const lessons = JSON.parse(lessonsDataEl.textContent);
  const readIds = Store.get("readIds") || [];
  const current = lessons.find((l) => readIds.indexOf(l.id) === -1) || lessons[0];

  if (current) {
    const link = currentLessonSection.querySelector("[data-home-current-lesson-link]");
    link.setAttribute("href", current.url);
    setText("[data-home-current-lesson-tag]", current.tag);
    setText("[data-home-current-lesson-title]", current.title);
    setText("[data-home-current-lesson-meta]", current.wordCount + " từ mới · truyện chêm");
    currentLessonSection.hidden = false;
  }
}

function setText(selector, text) {
  const el = document.querySelector(selector);
  if (el) el.textContent = text;
}
