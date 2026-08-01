// Màn Flashcard — docs/plan.md §1.3 màn 4, §1.6. Leitner box: again→0,
// hard→max(1,box), good→box+1, easy→box+2; box>=3 + rating good/easy => tự
// đánh dấu đã thuộc. Phiên = 8 thẻ random. srs = {id: {box, seen}}.
import { Store } from "./store.js";

const SESSION_SIZE = 8;

const root = document.querySelector("[data-flashcard-root]");
if (root) {
  init();
}

async function init() {
  const doneScreen = document.querySelector("[data-flashcard-done]");
  const card = document.querySelector("[data-flashcard-card]");
  const inner = document.querySelector("[data-flashcard-inner]");
  const progressFill = document.querySelector("[data-flashcard-progress-fill]");
  const indexEl = document.querySelector("[data-flashcard-index]");
  const totalEl = document.querySelector("[data-flashcard-total]");
  const levelEl = document.querySelector("[data-flashcard-level]");
  const wordEl = document.querySelector("[data-flashcard-word]");
  const ipaEl = document.querySelector("[data-flashcard-ipa]");
  const speakBtn = document.querySelector("[data-flashcard-speak]");
  const meaningEl = document.querySelector("[data-flashcard-meaning]");
  const exampleEl = document.querySelector("[data-flashcard-example]");
  const exampleViEl = document.querySelector("[data-flashcard-example-vi]");
  const revealBtn = document.querySelector("[data-flashcard-reveal]");
  const ratings = document.querySelector("[data-flashcard-ratings]");
  const restartBtn = document.querySelector("[data-flashcard-restart]");

  // words.json chỉ sinh ở /words/ (content/words/_index.md, §6.5) — trang
  // /flashcard/ không có output riêng, phải trỏ sang bằng đường dẫn tương đối.
  let words = [];
  try {
    const res = await fetch("../words/index.json");
    words = await res.json();
  } catch (e) {
    return;
  }

  let session = [];
  let position = 0;
  let flipped = false;

  startSession();

  card.addEventListener("click", flip);
  revealBtn.addEventListener("click", flip);
  restartBtn.addEventListener("click", startSession);

  ratings.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-rating]");
    if (!btn) return;
    rate(btn.getAttribute("data-rating"));
  });

  function startSession() {
    session = pickRandom(words, SESSION_SIZE);
    position = 0;
    root.hidden = false;
    doneScreen.hidden = true;
    totalEl.textContent = String(session.length);
    renderCard();
  }

  function renderCard() {
    flipped = false;
    inner.classList.remove("is-flipped");
    ratings.hidden = true;

    const w = session[position];
    indexEl.textContent = String(position + 1);
    progressFill.style.width = Math.round(((position + 1) / session.length) * 100) + "%";

    levelEl.textContent = "TOEIC " + w.v;
    levelEl.className = "badge-level badge-level--" + w.v;
    wordEl.textContent = w.w;
    ipaEl.textContent = w.i;
    speakBtn.setAttribute("data-speak", w.w);
    meaningEl.textContent = w.m;
    exampleEl.innerHTML = escapeHTML(w.ex).replace(/\{([^}]+)\}/g, "<mark>$1</mark>");
    exampleViEl.textContent = w.exv;
  }

  function flip() {
    if (flipped) return;
    flipped = true;
    inner.classList.add("is-flipped");
    ratings.hidden = false;
  }

  function rate(rating) {
    const w = session[position];
    const srs = Store.get("srs") || {};
    const prevBox = srs[w.k] ? srs[w.k].box : 0;
    const prevSeen = srs[w.k] ? srs[w.k].seen : 0;

    let box = prevBox;
    if (rating === "again") box = 0;
    else if (rating === "hard") box = Math.max(1, prevBox);
    else if (rating === "good") box = prevBox + 1;
    else if (rating === "easy") box = prevBox + 2;

    srs[w.k] = { box, seen: prevSeen + 1 };
    Store.set("srs", srs);

    if (box >= 3 && (rating === "good" || rating === "easy")) {
      Store.add("masteredIds", w.k);
    }

    position += 1;
    if (position >= session.length) {
      root.hidden = true;
      doneScreen.hidden = false;
    } else {
      renderCard();
    }
  }
}

function pickRandom(arr, n) {
  const copy = arr.slice();
  for (let i = copy.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [copy[i], copy[j]] = [copy[j], copy[i]];
  }
  return copy.slice(0, Math.min(n, copy.length));
}

function escapeHTML(str) {
  return String(str).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
