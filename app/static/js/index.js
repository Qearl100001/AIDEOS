function getDfosTheme() {
  return document.documentElement.getAttribute("data-theme") === "dark"
    ? "dark"
    : "light";
}

function injectBriefingStructure(iframe) {
  try {
    const doc = iframe.contentDocument;
    if (!doc) return;
    let style = doc.getElementById("dfos-briefing-chrome");
    if (!style) {
      style = doc.createElement("style");
      style.id = "dfos-briefing-chrome";
      doc.head.appendChild(style);
    }
    style.textContent = `
      .briefing-paper {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
      }
      .briefing-container {
        max-width: none !important;
        width: 100% !important;
        padding: 40px 80px 24px 80px !important;
        box-sizing: border-box !important;
      }
      .briefing-prose hr {
        display: none !important;
        margin: 0 !important;
        height: 0 !important;
        border: 0 !important;
        visibility: hidden !important;
      }
      body.briefing-page,
      .briefing-prose {
        font-family: "Source Han Serif SC", "Noto Serif SC", "Noto Serif CJK SC",
          "Songti SC", "STSong", "SimSun", Georgia, "Times New Roman", serif !important;
      }
    `;
  } catch (e) {
    console.warn("[dfos] briefing structure inject failed", e);
  }
}

function injectBriefingColors(iframe) {
  try {
    const doc = iframe.contentDocument;
    if (!doc) return;
    let st = doc.getElementById("dfos-briefing-colors");
    if (!st) {
      st = doc.createElement("style");
      st.id = "dfos-briefing-colors";
      doc.head.appendChild(st);
    }
    const dark = getDfosTheme() === "dark";
    if (dark) {
      st.textContent = `
        body.briefing-page {
          background: #252528 !important;
          color: #d1d1d6 !important;
        }
        .briefing-prose { color: #d1d1d6 !important; }
        .briefing-prose h1, .briefing-prose h2, .briefing-prose h3 {
          color: #f5f5f7 !important;
        }
        .briefing-prose a { color: #5eb0ff !important; }
        .briefing-prose p, .briefing-prose li { color: #d1d1d6 !important; }
        /* 覆盖 briefing.css：strong / URL 片段等单独声明了深色，需强制提亮 */
        .briefing-prose strong,
        .briefing-prose b {
          color: #e8eaed !important;
        }
        .briefing-prose .link-url,
        .briefing-prose a .link-url {
          color: #aeb0b6 !important;
        }
        .briefing-prose a:hover:not(.dfos-deep-dive-link),
        .briefing-prose a:focus-visible:not(.dfos-deep-dive-link) {
          color: #9ec8ff !important;
          background: rgba(94, 176, 255, 0.1) !important;
          text-decoration-color: rgba(158, 200, 255, 0.45) !important;
        }
        .briefing-prose .title-en {
          color: #aeb0b6 !important;
        }
        .briefing-prose li::marker {
          color: #8e8e93 !important;
        }
        .briefing-prose blockquote {
          color: #d1d1d6 !important;
          background: rgba(255, 255, 255, 0.06) !important;
          border-left-color: rgba(255, 255, 255, 0.22) !important;
        }
        .briefing-prose code {
          color: #ff9f9f !important;
          background: rgba(255, 255, 255, 0.08) !important;
        }
        .briefing-prose th {
          background: rgba(255, 255, 255, 0.07) !important;
          color: #aeb0b6 !important;
        }
        .briefing-prose td {
          color: #d1d1d6 !important;
        }
        .briefing-prose .deep-dive-tag {
          background: #1e3a4f !important;
          color: #9ecbff !important;
          border: 1px solid rgba(94, 176, 255, 0.35) !important;
          border-radius: 10px !important;
          font-weight: 600;
        }
        a.dfos-deep-dive-link {
          font-size: 14px !important;
          font-weight: 600 !important;
          color: #5eb0ff !important;
          text-decoration: none !important;
          white-space: nowrap !important;
          border: 2px solid #5eb0ff !important;
          border-radius: 10px !important;
          padding: 6px 14px !important;
          background: #2c2c30 !important;
        }
        a.dfos-deep-dive-link:hover {
          background: rgba(94, 176, 255, 0.12) !important;
          border-color: #5eb0ff !important;
        }
        button.dfos-deep-dive-btn--secondary {
          border: 1px solid rgba(255, 255, 255, 0.22) !important;
          background: #2c2c30 !important;
          color: #e8eaed !important;
        }
        button.dfos-deep-dive-btn--primary {
          border: 2px solid #5eb0ff !important;
          color: #5eb0ff !important;
          background: #2c2c30 !important;
        }
      `;
    } else {
      st.textContent = `
        body.briefing-page {
          background: #ffffff !important;
          color: #333333 !important;
        }
        .briefing-prose { color: #333333 !important; }
        .briefing-prose h1, .briefing-prose h2, .briefing-prose h3 {
          color: #1a1a1a !important;
        }
        .briefing-prose a { color: #0095ff !important; }
        .briefing-prose strong,
        .briefing-prose b {
          color: #1a1a1a !important;
        }
        .briefing-prose p, .briefing-prose li {
          color: #333333 !important;
        }
        .briefing-prose .link-url,
        .briefing-prose a .link-url {
          color: #666666 !important;
        }
        .briefing-prose a:hover:not(.dfos-deep-dive-link),
        .briefing-prose a:focus-visible:not(.dfos-deep-dive-link) {
          color: #0078d4 !important;
          background: rgba(0, 149, 255, 0.08) !important;
          text-decoration-color: rgba(0, 120, 212, 0.4) !important;
        }
        .briefing-prose .deep-dive-tag {
          background: #d1e9ff !important;
          color: #0066cc !important;
          border: 1px solid rgba(0, 149, 255, 0.25) !important;
          border-radius: 10px !important;
          font-weight: 600;
        }
        a.dfos-deep-dive-link {
          font-size: 14px !important;
          font-weight: 600 !important;
          color: #0095ff !important;
          text-decoration: none !important;
          white-space: nowrap !important;
          border: 2px solid #0095ff !important;
          border-radius: 10px !important;
          padding: 6px 14px !important;
          background: #ffffff !important;
        }
        a.dfos-deep-dive-link:hover {
          background: rgba(0, 149, 255, 0.08) !important;
          border-color: #0095ff !important;
        }
        button.dfos-deep-dive-btn--secondary {
          border: 1px solid rgba(55, 53, 47, 0.22) !important;
          background: #ffffff !important;
          color: #37352f !important;
        }
        button.dfos-deep-dive-btn--primary {
          border: 2px solid #0095ff !important;
          color: #0095ff !important;
          background: #ffffff !important;
        }
      `;
    }
  } catch (e) {
    console.warn("[dfos] briefing colors inject failed", e);
  }
}

function injectDeepDiveLayout(iframe) {
  try {
    const doc = iframe.contentDocument;
    if (!doc) return;
    let st = doc.getElementById("dfos-deep-dive-style");
    if (!st) {
      st = doc.createElement("style");
      st.id = "dfos-deep-dive-style";
      doc.head.appendChild(st);
    }
    st.textContent = `
      h3.dfos-has-action {
        display: flex;
        flex-direction: row;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        width: 100%;
        box-sizing: border-box;
      }
      .dfos-deep-dive-heading {
        display: inline-flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 8px;
        min-width: 0;
        flex: 1 1 auto;
      }
      a.dfos-deep-dive-link {
        flex: 0 0 auto;
        align-self: center;
      }
      .dfos-deep-dive-actions {
        display: inline-flex;
        align-items: center;
        gap: 10px;
        flex-shrink: 0;
      }
      button.dfos-deep-dive-btn {
        flex: 0 0 auto;
        align-self: center;
        margin: 0;
        padding: 6px 14px;
        font-size: 14px;
        font-weight: 600;
        border-radius: 10px;
        cursor: pointer;
        font-family: ui-sans-serif, system-ui, -apple-system, sans-serif;
        white-space: nowrap;
      }
      button.dfos-deep-dive-btn:disabled {
        opacity: 0.55;
        cursor: not-allowed;
      }
    `;
  } catch (e) {
    console.warn("[dfos] deep dive layout failed", e);
  }
}

async function postArticleGenerate(date) {
  const resp = await fetch("/api/article", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date }),
  });
  if (!resp.ok) {
    let detail = "请重试";
    try {
      const errBody = await resp.json();
      if (errBody.detail) detail = String(errBody.detail);
    } catch (_) {
      /* ignore */
    }
    throw new Error(detail);
  }
  return resp.json();
}

async function injectDeepDiveLinks(iframe, date) {
  try {
    const doc = iframe.contentDocument;
    if (!doc) return;

    let articleExists = false;
    try {
      const r = await fetch(`/api/article/${date}`);
      articleExists = r.ok;
    } catch (_) {
      articleExists = false;
    }

    injectDeepDiveLayout(iframe);

    doc.querySelectorAll("h3").forEach((h3) => {
      if (!h3.querySelector(".deep-dive-tag")) return;
      if (h3.dataset.dfosLinked === "1") return;
      h3.dataset.dfosLinked = "1";
      h3.classList.add("dfos-has-action");
      const leftWrap = doc.createElement("span");
      leftWrap.className = "dfos-deep-dive-heading";
      while (h3.firstChild) {
        leftWrap.appendChild(h3.firstChild);
      }
      h3.appendChild(leftWrap);

      const actionsWrap = doc.createElement("span");
      actionsWrap.className = "dfos-deep-dive-actions";

      if (articleExists) {
        const regen = doc.createElement("button");
        regen.type = "button";
        regen.className = "dfos-deep-dive-btn dfos-deep-dive-btn--secondary";
        regen.textContent = "重新生成";
        regen.addEventListener("click", async (ev) => {
          ev.preventDefault();
          ev.stopPropagation();
          const idle = regen.textContent;
          regen.disabled = true;
          regen.textContent = "生成中…";
          try {
            await postArticleGenerate(date);
            window.top.location.href = `/article/${date}`;
          } catch (e) {
            alert(`生成失败：${e.message || e}`);
            regen.disabled = false;
            regen.textContent = idle;
          }
        });
        actionsWrap.appendChild(regen);

        const a = doc.createElement("a");
        a.className = "dfos-deep-dive-link";
        a.href = `/article/${date}`;
        a.target = "_top";
        a.rel = "noopener";
        a.textContent = "查看";
        actionsWrap.appendChild(a);
      } else {
        const gen = doc.createElement("button");
        gen.type = "button";
        gen.className = "dfos-deep-dive-btn dfos-deep-dive-btn--primary";
        gen.textContent = "生成文章";
        gen.addEventListener("click", async (ev) => {
          ev.preventDefault();
          ev.stopPropagation();
          const idle = gen.textContent;
          gen.disabled = true;
          gen.textContent = "生成中…";
          try {
            await postArticleGenerate(date);
            window.top.location.href = `/article/${date}`;
          } catch (e) {
            alert(`生成失败：${e.message || e}`);
            gen.disabled = false;
            gen.textContent = idle;
          }
        });
        actionsWrap.appendChild(gen);
      }

      h3.appendChild(actionsWrap);
    });

    injectBriefingColors(iframe);
  } catch (e) {
    console.warn("[dfos] inject deep dive links failed", e);
  }
}

function resizeBriefingIframe(iframe) {
  try {
    const doc = iframe.contentDocument;
    if (doc?.body) {
      const h = Math.max(doc.body.scrollHeight, 480);
      iframe.style.height = `${h}px`;
    }
  } catch (_) {
    /* cross-origin or not ready */
  }
}

function setActiveDateButton(date) {
  document.querySelectorAll(".date-btn").forEach((btn) => {
    const on = btn.dataset.date === date;
    btn.classList.toggle("date-btn--active", on);
    if (on) {
      btn.setAttribute("aria-current", "page");
    } else {
      btn.removeAttribute("aria-current");
    }
  });
}

async function loadBriefing(date) {
  setActiveDateButton(date);
  const box = document.getElementById("briefing-container");
  const url = `/dist/briefing/${date}.html`;
  box.innerHTML = '<p class="briefing-placeholder">加载中…</p>';

  const head = await fetch(url, { method: "HEAD" });
  if (!head.ok) {
    box.innerHTML = `<p class="briefing-placeholder">未找到该日简报页：<code>${url}</code>（请先跑 pipeline 或执行简报 HTML 构建）</p>`;
    return;
  }

  box.innerHTML = `<iframe id="briefing-frame" class="briefing-frame" title="简报"></iframe>`;
  const frame = document.getElementById("briefing-frame");
  frame.src = url;
  frame.onload = async () => {
    injectBriefingStructure(frame);
    await injectDeepDiveLinks(frame, date);
    resizeBriefingIframe(frame);
  };
}

window.addEventListener("dfos-theme", () => {
  const fr = document.getElementById("briefing-frame");
  if (fr?.contentDocument) injectBriefingColors(fr);
});

document.querySelectorAll(".date-btn").forEach((btn) => {
  btn.addEventListener("click", () => loadBriefing(btn.dataset.date));
});

if (window.__INITIAL_DATE__) {
  loadBriefing(window.__INITIAL_DATE__);
} else {
  document.querySelectorAll(".date-btn").forEach((btn) => {
    btn.classList.remove("date-btn--active");
    btn.removeAttribute("aria-current");
  });
}
