(() => {
  const button = document.querySelector("[data-history-pdf]");
  if (!button) return;
  const majorCount = Number(window.APP_HISTORY_MAJOR_COUNT || 0);
  if (majorCount > 7) {
    button.classList.remove("is-muted");
    button.removeAttribute("aria-disabled");
    button.removeAttribute("disabled");
    button.setAttribute("href", document.documentElement.lang === "en" ? "history-full-en.pdf" : "history-full.pdf");
    button.textContent = document.documentElement.lang === "en" ? "Download full history (PDF)" : "??????? ?????? ??????? (PDF)";
  } else {
    button.classList.add("is-muted");
    button.setAttribute("aria-disabled", "true");
    button.setAttribute("disabled", "disabled");
    button.removeAttribute("href");
    button.title = document.documentElement.lang === "en" ? "The full PDF history becomes available after 7 major versions." : "?????? ??????? ? PDF ?????? ???????? ????? 7 major-??????.";
  }
})();
