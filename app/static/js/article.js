const ICON_PLAY_SVG = `<svg class="dfos-player-icon-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M9 6.5L18 12 9 17.5V6.5z" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/></svg>`;

const ICON_PAUSE_SVG = `<svg class="dfos-player-icon-svg" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M8 6v12M16 6v12" stroke="currentColor" stroke-width="1.75" stroke-linecap="round"/></svg>`;

const ICON_SPEAKER_SVG = `<svg class="dfos-player-icon-svg dfos-player-icon-svg--vol" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M11 5L6 9H3v6h3l5 4V5z" stroke="currentColor" stroke-width="1.75" stroke-linejoin="round"/><path d="M16 10a2 2 0 010 4M18 7.5a5.5 5.5 0 010 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>`;

function formatTime(sec) {
  if (!Number.isFinite(sec) || sec < 0) return "0:00";
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function initDfosPlayer() {
  const audio = document.getElementById("tts-audio");
  const playBtn = document.getElementById("tts-play");
  const progress = document.getElementById("tts-progress");
  const timeEl = document.getElementById("tts-time");
  const ffBtn = document.getElementById("tts-ff");
  const volEl = document.getElementById("tts-vol");
  if (!audio || !playBtn || !progress || !timeEl || !ffBtn) return;
  if (audio.dataset.dfosPlayerBound === "1") return;
  audio.dataset.dfosPlayerBound = "1";

  let isDragging = false;

  function syncProgressFromAudio() {
    if (!audio.duration || !Number.isFinite(audio.duration)) {
      progress.value = 0;
      timeEl.textContent = `0:00 / ${formatTime(0)}`;
      return;
    }
    if (!isDragging) {
      progress.value = (audio.currentTime / audio.duration) * 1000;
    }
    timeEl.textContent = `${formatTime(audio.currentTime)} / ${formatTime(audio.duration)}`;
  }

  function setPlayingUi(playing) {
    playBtn.setAttribute("aria-label", playing ? "暂停" : "播放");
    playBtn.innerHTML = playing ? ICON_PAUSE_SVG : ICON_PLAY_SVG;
  }

  audio.addEventListener("timeupdate", syncProgressFromAudio);
  audio.addEventListener("loadedmetadata", syncProgressFromAudio);
  audio.addEventListener("ended", () => setPlayingUi(false));
  audio.addEventListener("play", () => setPlayingUi(true));
  audio.addEventListener("pause", () => setPlayingUi(false));

  playBtn.addEventListener("click", () => {
    if (!audio.src) return;
    if (audio.paused) {
      audio.play().catch(() => {});
    } else {
      audio.pause();
    }
  });

  progress.addEventListener("pointerdown", () => {
    isDragging = true;
  });
  progress.addEventListener("pointerup", () => {
    isDragging = false;
    syncProgressFromAudio();
  });
  progress.addEventListener("pointercancel", () => {
    isDragging = false;
  });
  progress.addEventListener("change", () => {
    isDragging = false;
  });
  progress.addEventListener("input", () => {
    if (!audio.duration || !Number.isFinite(audio.duration)) return;
    audio.currentTime = (Number(progress.value) / 1000) * audio.duration;
  });

  ffBtn.addEventListener("click", () => {
    if (!audio.src) return;
    const dur = audio.duration && Number.isFinite(audio.duration) ? audio.duration : Infinity;
    audio.currentTime = Math.min(audio.currentTime + 15, dur);
  });

  if (volEl) {
    volEl.value = String(Math.round(audio.volume * 100));
    volEl.addEventListener("input", () => {
      const v = Number(volEl.value) / 100;
      audio.volume = Math.max(0, Math.min(1, v));
    });
  }

  function refreshChromeState() {
    const ready = Boolean(audio.src);
    setPlayerEnabled(ready);
    if (!ready) syncProgressFromAudio();
  }

  refreshChromeState();
}

function mountTtsBar(articleRoot) {
  const old = document.getElementById("dfos-tts-bar");
  if (old) old.remove();

  const wrap = document.createElement("div");
  wrap.id = "dfos-tts-bar";
  wrap.className = "dfos-player";
  wrap.innerHTML = `
    <div class="dfos-player-row">
      <span id="tts-status" class="dfos-player-status">语音：载入中…</span>
      <div id="tts-player-chrome" class="dfos-player-chrome dfos-player-chrome--disabled">
        <button type="button" id="tts-play" class="dfos-player-play" aria-label="播放" disabled>
          ${ICON_PLAY_SVG}
        </button>
        <span id="tts-time" class="dfos-player-time">0:00 / 0:00</span>
        <input type="range" id="tts-progress" class="dfos-player-scrub" min="0" max="1000" value="0" step="1" disabled />
        <button type="button" id="tts-ff" class="dfos-player-ff" disabled title="快进 15 秒">+15s</button>
        <label class="dfos-player-vol-wrap" title="音量">
          ${ICON_SPEAKER_SVG}
          <input type="range" id="tts-vol" class="dfos-player-vol" min="0" max="100" value="100" disabled />
        </label>
      </div>
    </div>
    <audio id="tts-audio" class="dfos-audio-el" preload="metadata"></audio>
  `;

  const h1 = articleRoot.querySelector("h1");
  if (h1) {
    h1.insertAdjacentElement("afterend", wrap);
  } else {
    articleRoot.insertBefore(wrap, articleRoot.firstChild);
  }

  initDfosPlayer();
}

function setPlayerEnabled(on) {
  const chrome = document.getElementById("tts-player-chrome");
  const playBtn = document.getElementById("tts-play");
  const ffBtn = document.getElementById("tts-ff");
  const progress = document.getElementById("tts-progress");
  const volEl = document.getElementById("tts-vol");
  if (chrome) {
    chrome.classList.toggle("dfos-player-chrome--disabled", !on);
    chrome.classList.toggle("dfos-player-chrome--ready", on);
  }
  if (playBtn) playBtn.disabled = !on;
  if (ffBtn) ffBtn.disabled = !on;
  if (progress) progress.disabled = !on;
  if (volEl) volEl.disabled = !on;
}

function setAudioSrc(url) {
  const audio = document.getElementById("tts-audio");
  if (!audio || !url) return;
  audio.src = url;
  setPlayerEnabled(true);
}


async function loadArticle() {
  const date = window.__ARTICLE_DATE__;
  const box = document.getElementById("article-container");
  const res = await fetch(`/api/article/${date}`);

  if (!res.ok) {
    const err = await res.json();
    box.innerHTML = `<p>加载失败：${err.detail || "未知错误"}</p>`;
    return false;
  }

  const data = await res.json();
  box.innerHTML = data.rendered_html;
  box.classList.add("dfos-article-prose");
  mountTtsBar(box);
  return true;
}

async function pollStatus(date, jobId) {
  const statusNode = document.getElementById("tts-status");

  let done = false;
  while (!done) {
    const res = await fetch(`/api/tts/${date}/status?job_id=${jobId}`);
    if (!res.ok) {
      if (statusNode) statusNode.textContent = "语音：状态查询失败";
      return;
    }

    const data = await res.json();

    if (data.status === "running") {
      if (statusNode) statusNode.textContent = "语音：正在合成（豆包 TTS）…";
      await new Promise((resolve) => setTimeout(resolve, 2000));
      continue;
    }

    if (data.status === "success" && data.audio_url) {
      if (statusNode) statusNode.textContent = "语音：已完成，可直接播放";
      setAudioSrc(`${data.audio_url}?t=${Date.now()}`);
    } else if (statusNode) {
      statusNode.textContent = `语音：${data.message || "生成失败"}`;
    }
    done = true;
  }
}

async function maybeUseExistingAudio(date) {
  const statusNode = document.getElementById("tts-status");

  try {
    const r = await fetch(`/api/audio/${date}/meta`);
    if (!r.ok) return false;
    const meta = await r.json();
    if (meta.exists) {
      if (statusNode) statusNode.textContent = "语音：检测到已有音频，可直接播放";
      setAudioSrc(`/api/audio/${date}?t=${Date.now()}`);
      return true;
    }
  } catch (_) {
    /* ignore */
  }
  return false;
}

async function autoStartTTS() {
  const date = window.__ARTICLE_DATE__;
  const statusNode = document.getElementById("tts-status");
  if (!statusNode) return;

  if (await maybeUseExistingAudio(date)) {
    return;
  }

  statusNode.textContent = "语音：正在提交合成任务…";
  const res = await fetch(`/api/tts/${date}`, { method: "POST" });
  if (!res.ok) {
    const err = await res.json();
    statusNode.textContent = `语音：启动失败（${err.detail || "未知错误"}）`;
    return;
  }
  const data = await res.json();
  await pollStatus(date, data.job_id);
}

async function main() {
  const ok = await loadArticle();
  if (!ok) {
    return;
  }
  const statusNode = document.getElementById("tts-status");
  if (statusNode) {
    statusNode.textContent = "语音：准备播放或生成…";
  }
  await autoStartTTS();
}

main();
