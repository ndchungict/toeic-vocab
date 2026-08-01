// Nút "đã thuộc" / "yêu thích" — dùng chung ở màn Detail (M4) và Vocab (M6).
// Cũng đồng bộ badge "Đã đọc/Chưa đọc" trên card bài học (docs/plan.md §1.6) —
// readIds do reader.js (M6) ghi khi mở chương, ở đây chỉ ĐỌC để hiển thị.
import { Store } from "./store.js";

function setLabel(btn, active) {
  const label = btn.querySelector(".btn__label");
  if (!label) return;
  label.textContent = active ? label.dataset.labelOn : label.dataset.labelOff;
}

function syncMasteredButtons() {
  document.querySelectorAll("[data-mastered-toggle]").forEach((btn) => {
    const active = Store.has("masteredIds", btn.getAttribute("data-mastered-toggle"));
    btn.setAttribute("aria-pressed", String(active));
    setLabel(btn, active);
  });
}

function syncFavButtons() {
  document.querySelectorAll("[data-fav-toggle]").forEach((btn) => {
    const active = Store.has("favIds", btn.getAttribute("data-fav-toggle"));
    btn.setAttribute("aria-pressed", String(active));
    setLabel(btn, active);
  });
}

function syncReadBadges() {
  document.querySelectorAll("[data-lesson-card]").forEach((card) => {
    const lessonId = card.getAttribute("data-lesson-card");
    const badge = card.querySelector("[data-read-badge]");
    if (!badge) return;
    const isRead = Store.has("readIds", lessonId);
    badge.textContent = isRead ? "Đã đọc" : "Chưa đọc";
    badge.classList.toggle("badge-status--read", isRead);
  });
}

// Badge "Đã làm N/M" trên /exercises/ — results ghi bởi quiz.js (M7) khi nộp
// bài, ở đây chỉ ĐỌC để hiển thị (giống readIds ở trên).
function syncExerciseBadges() {
  document.querySelectorAll("[data-exercise-card]").forEach((card) => {
    const lessonId = card.getAttribute("data-exercise-card");
    const badge = card.querySelector("[data-exercise-result-badge]");
    if (!badge) return;
    const results = Store.get("results") || {};
    const result = results[lessonId];
    if (result) {
      badge.textContent = "Đã làm " + result.score + "/" + result.total;
      badge.classList.add("badge-status--read");
    } else {
      badge.textContent = "Chưa làm";
      badge.classList.remove("badge-status--read");
    }
  });
}

document.addEventListener("click", (e) => {
  const masteredBtn = e.target.closest("[data-mastered-toggle]");
  if (masteredBtn) {
    Store.toggle("masteredIds", masteredBtn.getAttribute("data-mastered-toggle"));
    syncMasteredButtons();
    return;
  }
  const favBtn = e.target.closest("[data-fav-toggle]");
  if (favBtn) {
    Store.toggle("favIds", favBtn.getAttribute("data-fav-toggle"));
    syncFavButtons();
  }
});

syncMasteredButtons();
syncFavButtons();
syncReadBadges();
syncExerciseBadges();
