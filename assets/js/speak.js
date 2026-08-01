// TTS phát âm — docs/plan.md §1.6: window.speechSynthesis, lang en-US, rate .9,
// xoá {…} trước khi đọc (marker highlight từ trong example.en), cancel() trước
// mỗi lần đọc mới (tránh chồng nhiều câu đọc cùng lúc khi bấm liên tiếp).
function speak(text) {
  if (!("speechSynthesis" in window)) return;
  const clean = text.replace(/[{}]/g, "");
  if (!clean) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.lang = "en-US";
  utterance.rate = 0.9;
  window.speechSynthesis.speak(utterance);
}

document.addEventListener("click", (e) => {
  const btn = e.target.closest("[data-speak]");
  if (!btn) return;
  const text = btn.getAttribute("data-speak");
  if (text) speak(text);
});
