// Màn Vocab — docs/plan.md §1.3 màn 2, §1.6, §7.4. Fetch words.json 1 lần, lọc/
// tìm/phân trang hoàn toàn ở client. Đồng bộ trạng thái lọc vào ?query để chia
// sẻ được (§5.2). 558 từ không đáng kể để lọc bằng mảng JS thuần — chỉ giới hạn
// SỐ CARD RENDER (§7.4: "quy mô bắt buộc do 558 vs 27 từ trong mockup").
import { Store } from "./store.js";

const PAGE_SIZE = 60;

const POS_LABEL = {
  noun: "danh từ",
  verb: "động từ",
  adjective: "tính từ",
  adverb: "trạng từ",
  "phrasal verb": "cụm động từ",
  preposition: "giới từ",
};

const root = document.querySelector("[data-vocab-grid]");
if (root) {
  init();
}

async function init() {
  const grid = root;
  const countEl = document.querySelector("[data-vocab-count]");
  const emptyEl = document.querySelector("[data-vocab-empty]");
  const loadMoreBtn = document.querySelector("[data-vocab-load-more]");
  const searchInput = document.querySelector("[data-vocab-search]");
  const clearBtn = document.querySelector("[data-vocab-clear-filters]");
  const filterGroups = document.querySelectorAll("[data-filter-group]");
  const subtopicGroups = document.querySelectorAll("[data-subtopic-group]");

  let words = [];
  try {
    const res = await fetch("index.json");
    words = await res.json();
  } catch (e) {
    if (emptyEl) {
      emptyEl.hidden = false;
      emptyEl.textContent = "Không tải được dữ liệu từ vựng.";
    }
    return;
  }

  const state = { q: "", topic: "", subtopic: "", level: "", pos: "", lesson: "" };
  let visibleCount = PAGE_SIZE;

  hydrateFromURL();
  applyPillStates();
  render();

  searchInput.addEventListener("input", () => {
    state.q = searchInput.value.trim().toLowerCase();
    visibleCount = PAGE_SIZE;
    syncURL();
    render();
  });

  filterGroups.forEach((group) => {
    const field = group.getAttribute("data-filter-group");
    group.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill");
      if (!btn || !group.contains(btn)) return;
      state[field] = btn.getAttribute("data-filter-value");
      if (field === "topic") {
        state.subtopic = "";
        showSubtopicGroup(state.topic);
      }
      visibleCount = PAGE_SIZE;
      applyPillStates();
      syncURL();
      render();
    });
  });

  subtopicGroups.forEach((group) => {
    group.addEventListener("click", (e) => {
      const btn = e.target.closest(".pill");
      if (!btn || !group.contains(btn)) return;
      state.subtopic = btn.getAttribute("data-filter-value");
      visibleCount = PAGE_SIZE;
      applyPillStates();
      syncURL();
      render();
    });
  });

  clearBtn.addEventListener("click", () => {
    state.q = "";
    state.topic = "";
    state.subtopic = "";
    state.level = "";
    state.pos = "";
    state.lesson = "";
    searchInput.value = "";
    visibleCount = PAGE_SIZE;
    subtopicGroups.forEach((g) => {
      g.hidden = true;
    });
    applyPillStates();
    syncURL();
    render();
  });

  loadMoreBtn.addEventListener("click", () => {
    visibleCount += PAGE_SIZE;
    render();
  });

  // Card cả khối là 1 thẻ <a> (điều hướng sang trang chi tiết), nhưng 2 nút
  // yêu thích/đã thuộc nằm bên trong nó phải chặn điều hướng khi bấm. KHÔNG tự
  // gọi Store.toggle ở đây — word-actions.js đã lắng nghe [data-mastered-toggle]/
  // [data-fav-toggle] trên toàn document (kể cả phần tử thêm sau), gọi thêm ở
  // đây sẽ toggle 2 lần/lượt bấm. Không stopPropagation để sự kiện vẫn nổi lên
  // tới document cho word-actions.js xử lý.
  grid.addEventListener("click", (e) => {
    if (e.target.closest("[data-mastered-toggle], [data-fav-toggle]")) {
      e.preventDefault();
    }
  });

  function showSubtopicGroup(topic) {
    subtopicGroups.forEach((g) => {
      g.hidden = g.getAttribute("data-subtopic-group") !== topic;
    });
  }

  function applyPillStates() {
    filterGroups.forEach((group) => {
      const field = group.getAttribute("data-filter-group");
      group.querySelectorAll(".pill").forEach((btn) => {
        btn.classList.toggle("is-active", btn.getAttribute("data-filter-value") === state[field]);
      });
    });
    subtopicGroups.forEach((group) => {
      group.querySelectorAll(".pill").forEach((btn) => {
        btn.classList.toggle("is-active", btn.getAttribute("data-filter-value") === state.subtopic);
      });
    });
    clearBtn.hidden = !(state.q || state.topic || state.subtopic || state.level || state.pos || state.lesson);
  }

  function matches(w) {
    if (state.q && !(w.w.toLowerCase().includes(state.q) || w.m.toLowerCase().includes(state.q))) return false;
    if (state.topic && w.t !== state.topic) return false;
    if (state.subtopic && w.s !== state.subtopic) return false;
    if (state.level && String(w.v) !== state.level) return false;
    if (state.pos && w.p !== state.pos) return false;
    if (state.lesson && w.l.indexOf(state.lesson) === -1) return false;
    return true;
  }

  function render() {
    const filtered = words.filter(matches);
    countEl.textContent = filtered.length + " từ";
    emptyEl.hidden = filtered.length !== 0;

    const visible = filtered.slice(0, visibleCount);
    grid.innerHTML = visible.map(cardHTML).join("");
    loadMoreBtn.hidden = visibleCount >= filtered.length;
  }

  function cardHTML(w) {
    const mastered = Store.has("masteredIds", w.k);
    const fav = Store.has("favIds", w.k);
    const posLabel = POS_LABEL[w.p] || w.p;
    return (
      '<a class="vocab-card" href="' + w.u + '">' +
      '<div class="vocab-card__head"><span class="vocab-card__word">' + escapeHTML(w.w) + '</span>' +
      '<span class="badge-level badge-level--' + w.v + '">TOEIC ' + w.v + "</span></div>" +
      '<p class="vocab-card__pos">' + escapeHTML(posLabel) + " · " + escapeHTML(w.i) + "</p>" +
      '<p class="vocab-card__meaning">' + escapeHTML(w.m) + "</p>" +
      '<div class="vocab-card__actions">' +
      '<button type="button" class="icon-toggle" data-fav-toggle="' + w.k + '" aria-pressed="' + fav + '" aria-label="Yêu thích">' +
      heartIcon() +
      "</button>" +
      '<button type="button" class="icon-toggle" data-mastered-toggle="' + w.k + '" aria-pressed="' + mastered + '" aria-label="Đánh dấu đã thuộc">' +
      checkIcon() +
      "</button>" +
      "</div></a>"
    );
  }

  function hydrateFromURL() {
    const params = new URLSearchParams(location.search);
    ["q", "topic", "subtopic", "level", "pos", "lesson"].forEach((field) => {
      if (params.has(field)) state[field] = params.get(field);
    });
    if (state.q) searchInput.value = state.q;
    if (state.topic) showSubtopicGroup(state.topic);
  }

  function syncURL() {
    const params = new URLSearchParams();
    Object.keys(state).forEach((field) => {
      if (state[field]) params.set(field, state[field]);
    });
    const qs = params.toString();
    history.replaceState(null, "", qs ? "?" + qs : location.pathname);
  }
}

function escapeHTML(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function heartIcon() {
  return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M12 20.2s-7.5-4.6-9.7-9.3C.7 7.5 2.4 4 6 4c2 0 3.4 1 4.7 2.6C12 5 13.4 4 15.4 4c3.6 0 5.3 3.5 3.7 6.9-2.2 4.7-9.1 9.3-9.1 9.3Z"/></svg>';
}

function checkIcon() {
  return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12.5 9.5 18l10-12"/></svg>';
}
