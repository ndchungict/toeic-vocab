// Màn Bài tập & Kết quả — docs/plan.md §1.3 màn 7-8, §4, §6.6. Kết quả KHÔNG
// phải trang riêng — cùng trang, chỉ đổi view. Đáp án đọc từ #ex-answers (nhúng
// sẵn lúc build, không obfuscate — công cụ tự học, không phải bài thi giám sát).
import { Store } from "./store.js";

const root = document.querySelector("[data-exercise-root]");
if (root) {
  init();
}

function init() {
  const lessonId = root.getAttribute("data-lesson-id");
  const total = parseInt(root.getAttribute("data-total"), 10);
  const answersData = JSON.parse(document.getElementById("ex-answers").textContent);

  const quizView = document.querySelector("[data-exercise-quiz]");
  const resultView = document.querySelector("[data-exercise-result]");
  const progressBar = document.querySelector("[data-exercise-progress]");
  const progressFill = document.querySelector("[data-exercise-progress-fill]");
  const submitBtn = document.querySelector("[data-exercise-submit]");
  const retryBtn = document.querySelector("[data-result-retry]");

  const selections = {};

  quizView.addEventListener("click", (e) => {
    const optBtn = e.target.closest(".exercise-option");
    if (!optBtn) return;
    selectOption(optBtn);
  });

  submitBtn.addEventListener("click", submit);
  retryBtn.addEventListener("click", retry);

  function selectOption(optBtn) {
    const qId = optBtn.getAttribute("data-question-id");
    const letter = optBtn.getAttribute("data-option-letter");
    selections[qId] = letter;

    document.querySelectorAll('.exercise-option[data-question-id="' + qId + '"]').forEach((b) => {
      b.classList.toggle("is-selected", b === optBtn);
    });

    const blank = document.querySelector('.exercise-blank[data-blank-id="' + qId + '"]');
    if (blank) {
      const text = optBtn.querySelector(".exercise-option__text");
      blank.textContent = text ? text.textContent : optBtn.textContent;
      blank.classList.add("is-answered");
    }

    updateProgress();
  }

  function updateProgress() {
    const answeredCount = Object.keys(selections).length;
    const pct = total ? Math.round((answeredCount / total) * 100) : 0;
    progressFill.style.width = pct + "%";
    document.querySelectorAll("[data-exercise-answered], [data-exercise-answered-2]").forEach((el) => {
      el.textContent = String(answeredCount);
    });
  }

  function partFromId(id) {
    const m = id.match(/-p(\d)-/);
    return m ? m[1] : "?";
  }

  function submit() {
    let correct = 0;
    const partScores = {};

    Object.keys(answersData).forEach((qId) => {
      const info = answersData[qId];
      const part = partFromId(qId);
      partScores[part] = partScores[part] || { c: 0, t: 0 };
      partScores[part].t += 1;

      const selected = selections[qId];
      const isCorrect = selected === info.a;
      if (isCorrect) {
        correct += 1;
        partScores[part].c += 1;
      }

      const card = document.querySelector('[data-result-card="' + qId + '"]');
      if (!card) return;

      const badge = card.querySelector("[data-result-badge]");
      badge.classList.remove("badge-status--correct", "badge-status--incorrect");
      if (!selected) {
        badge.textContent = "Chưa làm";
      } else if (isCorrect) {
        badge.textContent = "Đúng";
        badge.classList.add("badge-status--correct");
      } else {
        badge.textContent = "Sai";
        badge.classList.add("badge-status--incorrect");
      }

      card.querySelectorAll(".result-option").forEach((opt) => {
        const letter = opt.getAttribute("data-option-letter");
        const tag = opt.querySelector("[data-option-tag]");
        opt.classList.remove("is-correct", "is-selected-wrong");
        tag.textContent = "";
        if (letter === info.a) {
          opt.classList.add("is-correct");
          tag.textContent = "✓ Đáp án";
        } else if (letter === selected) {
          opt.classList.add("is-selected-wrong");
          tag.textContent = "Bạn chọn";
        }
      });
    });

    const pct = total ? Math.round((correct / total) * 100) : 0;
    setText("[data-result-score]", String(correct));
    setText("[data-result-pct]", String(pct));

    const partScoresEl = document.querySelector("[data-result-part-scores]");
    if (partScoresEl) {
      partScoresEl.innerHTML = Object.keys(partScores)
        .sort()
        .map((p) => {
          const s = partScores[p];
          return '<span class="result-hero__part">Part ' + p + ": " + s.c + "/" + s.t + "</span>";
        })
        .join("");
    }

    quizView.hidden = true;
    resultView.hidden = false;
    if (progressBar) progressBar.hidden = true;

    const results = Store.get("results") || {};
    results[lessonId] = { score: correct, total: total, at: Date.now() };
    Store.set("results", results);
  }

  function retry() {
    Object.keys(selections).forEach((k) => {
      delete selections[k];
    });
    document.querySelectorAll(".exercise-option.is-selected").forEach((b) => {
      b.classList.remove("is-selected");
    });
    document.querySelectorAll(".exercise-blank.is-answered").forEach((b) => {
      b.classList.remove("is-answered");
      b.textContent = b.getAttribute("data-placeholder") || "?";
    });
    updateProgress();

    quizView.hidden = false;
    resultView.hidden = true;
    if (progressBar) progressBar.hidden = false;
  }

  function setText(selector, text) {
    const el = document.querySelector(selector);
    if (el) el.textContent = text;
  }
}
