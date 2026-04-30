/**
 * 全局浅色 / 深色主题：切换 <html data-theme> + localStorage，并派发 dfos-theme。
 * 初始主题由 base 页首内联脚本从 localStorage 恢复。
 */
(function () {
  const STORAGE_KEY = "dfos-theme";

  function storedTheme() {
    const t = localStorage.getItem(STORAGE_KEY);
    if (t === "dark" || t === "light") return t;
    return "light";
  }

  function currentTheme() {
    const a = document.documentElement.getAttribute("data-theme");
    if (a === "dark" || a === "light") return a;
    return storedTheme();
  }

  function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    try {
      localStorage.setItem(STORAGE_KEY, theme);
    } catch (_) {
      /* ignore */
    }
    window.dispatchEvent(new CustomEvent("dfos-theme", { detail: theme }));
    updateToggleUi(theme);
  }

  function updateToggleUi(theme) {
    const btn = document.getElementById("dfos-theme-toggle");
    if (!btn) return;
    const dark = theme === "dark";
    btn.setAttribute(
      "aria-label",
      dark ? "切换为浅色模式" : "切换为深色模式",
    );
    btn.setAttribute("title", dark ? "浅色模式" : "深色模式");
    btn.innerHTML = dark ? ICON_SUN : ICON_MOON;
  }

  const ICON_MOON = `<svg class="dfos-theme-toggle__icon" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" d="M21.75 15A9.72 9.72 0 0 1 18 15.75c-5.38 0-9.75-4.37-9.75-9.75 0-1.33.27-2.6.75-3.75A9.75 9.75 0 0 0 3 11.25 9.75 9.75 0 0 0 12.75 21 9.75 9.75 0 0 0 21.75 15Z"/></svg>`;

  const ICON_SUN = `<svg class="dfos-theme-toggle__icon" width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><circle cx="12" cy="12" r="3.5" stroke="currentColor" stroke-width="1.75"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`;

  document.addEventListener("DOMContentLoaded", () => {
    const theme = currentTheme();
    if (document.documentElement.getAttribute("data-theme") !== theme) {
      document.documentElement.setAttribute("data-theme", theme);
    }
    updateToggleUi(theme);
    const btn = document.getElementById("dfos-theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
      setTheme(currentTheme() === "dark" ? "light" : "dark");
    });
  });
})();
