// Màn Reader — docs/plan.md §1.3 màn 6, §1.6. Toggle chêm/EN, hiện/ẩn nghĩa,
// popover từ (mở từ chip trong truyện VÀ từ danh sách "Từ mới"), tự set
// readIds khi mở chương.
import { Store } from "./store.js";

const POS_LABEL = {
  noun: "danh từ",
  verb: "động từ",
  adjective: "tính từ",
  adverb: "trạng từ",
  "phrasal verb": "cụm động từ",
  preposition: "giới từ",
};

const root = document.querySelector("[data-reader-root]");
if (root) {
  init();
}

async function init() {
  const lessonId = root.getAttribute("data-lesson-id");
  if (lessonId) Store.add("readIds", lessonId);

  initLangSwitch();
  initGlossToggle();
  await initPopover();
}

function initLangSwitch() {
  const switchEl = document.querySelector("[data-reader-lang-switch]");
  const glossToggle = document.querySelector("[data-reader-gloss-toggle]");
  if (!switchEl) return;

  switchEl.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-lang]");
    if (!btn) return;
    const lang = btn.getAttribute("data-lang");

    switchEl.querySelectorAll("[data-lang]").forEach((b) => {
      const active = b === btn;
      b.classList.toggle("is-active", active);
      b.setAttribute("aria-selected", String(active));
    });

    document.querySelectorAll("[data-reader-version]").forEach((v) => {
      v.hidden = v.getAttribute("data-reader-version") !== lang;
    });

    // "Hiện nghĩa" chỉ áp dụng bản chêm — bản tiếng Anh không có gloss (§1.3).
    if (glossToggle) glossToggle.hidden = lang !== "chem";
  });
}

function initGlossToggle() {
  const btn = document.querySelector("[data-reader-gloss-toggle]");
  if (!btn) return;

  btn.addEventListener("click", () => {
    const active = btn.getAttribute("aria-pressed") === "true";
    const next = !active;
    btn.setAttribute("aria-pressed", String(next));
    btn.textContent = next ? "Ẩn nghĩa" : "Hiện nghĩa";
    document.querySelectorAll(".reader-chip__gloss").forEach((g) => {
      g.hidden = !next;
    });
  });
}

async function initPopover() {
  const overlay = document.querySelector("[data-popover-overlay]");
  if (!overlay) return;

  const popover = overlay.querySelector(".popover");
  const wordEl = overlay.querySelector("[data-popover-word]");
  const levelEl = overlay.querySelector("[data-popover-level]");
  const metaEl = overlay.querySelector("[data-popover-meta]");
  const meaningEl = overlay.querySelector("[data-popover-meaning]");
  const speakBtn = overlay.querySelector("[data-popover-speak]");
  const detailLink = overlay.querySelector("[data-popover-detail-link]");
  const closeBtn = overlay.querySelector("[data-popover-close]");

  // a11y: trả focus về đúng phần tử đã mở popover khi đóng lại (bàn phím/
  // trình đọc màn hình không nên "mất dấu" sau khi popover biến mất).
  let lastTrigger = null;

  let words = [];
  try {
    const res = await fetch("../../words/index.json");
    words = await res.json();
  } catch (e) {
    words = [];
  }
  const byKey = {};
  words.forEach((w) => {
    byKey[w.k] = w;
  });

  document.addEventListener("click", (e) => {
    const trigger = e.target.closest("[data-popover-trigger]");
    if (!trigger) return;
    const key = trigger.getAttribute("data-popover-trigger");
    const w = byKey[key];
    if (!w) return;
    lastTrigger = trigger;
    open(w);
  });

  closeBtn.addEventListener("click", close);
  overlay.addEventListener("click", (e) => {
    if (e.target === overlay) close();
  });
  document.addEventListener("keydown", (e) => {
    if (overlay.hidden) return;
    if (e.key === "Escape") {
      close();
    } else if (e.key === "Tab") {
      trapFocus(e);
    }
  });

  function open(w) {
    wordEl.textContent = w.w;
    levelEl.textContent = "TOEIC " + w.v;
    levelEl.className = "badge-level badge-level--" + w.v;
    metaEl.textContent = (POS_LABEL[w.p] || w.p) + " · " + w.i;
    meaningEl.textContent = w.m;
    speakBtn.setAttribute("data-speak", w.w);
    detailLink.setAttribute("href", w.u);
    overlay.hidden = false;
    closeBtn.focus();
  }

  function close() {
    overlay.hidden = true;
    if (lastTrigger) lastTrigger.focus();
  }

  function trapFocus(e) {
    const focusable = popover.querySelectorAll("button, a[href]");
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
}
