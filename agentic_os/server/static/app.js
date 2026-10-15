"use strict";
/* Agentic OS War Room: vanilla JS single-page app talking to the Agentic OS HTTP API (screens of mock-up C). */

const $ = (sel, root = document) => root.querySelector(sel);
const store = {
  get(k, d = null) { try { const v = localStorage.getItem(k); return v === null ? d : v; } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* storage unavailable */ } },
  del(k) { try { localStorage.removeItem(k); } catch { /* storage unavailable */ } },
};
let token = store.get("aos_token", "");
const state = {
  agents: [], tools: [], providers: [], presets: [], extPresets: [], def: {}, tab: "chat", timers: {},
  processes: [], schedules: [], docs: [], taskFilter: "all", deadlines: {}, seenApprovals: new Set(), modelCache: {},
};
const isApp = () => /AgenticOSApp/.test(navigator.userAgent);

/* ---------------------------------------------------------------- helpers */
function el(tag, attrs = {}, ...children) {
  const node = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") node.className = v;
    else if (k === "text") node.textContent = v;
    else if (k.startsWith("on")) node.addEventListener(k.slice(2), v);
    else node.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat()) if (c !== null && c !== undefined && c !== false) node.append(c.nodeType ? c : document.createTextNode(String(c)));
  return node;
}
const ICONS = {
  robot: '<rect x="5" y="7" width="14" height="11" rx="3"/><path d="M12 3v4"/>',
  pen: '<path d="M4 20h4L19 9l-4-4L4 16z"/>',
  plus: '<path d="M12 5v14M5 12h14"/>',
  shield: '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
  question: '<circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.6.3-1 .9-1 1.6M12 17h.01"/>',
  wrench: '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.4L3 18l3 3 6.3-6.3a4 4 0 0 0 5.4-5.4l-2.5 2.5-2.4-.6-.6-2.4z"/>',
  clock: '<circle cx="12" cy="12" r="8"/><path d="M12 8v4l3 2"/>',
  spark: '<path d="M12 3l2.2 5.8L20 11l-5.8 2.2L12 19l-2.2-5.8L4 11l5.8-2.2z"/>',
  wave: '<path d="M4 12h5l3-7 3 14 3-7h2"/>',
  chevDown: '<path d="M6 9l6 6 6-6"/>',
};
function icon(name, size = 20) {
  const wrap = document.createElement("span");
  wrap.innerHTML = `<svg viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${ICONS[name]}</svg>`;
  return wrap.firstChild;
}
function toast(msg, isErr = false) {
  const t = $("#toast");
  t.textContent = msg; t.classList.toggle("err", isErr); t.classList.add("show");
  clearTimeout(state.timers.toast); state.timers.toast = setTimeout(() => t.classList.remove("show"), 3400);
}
/* explainError() lives in errors.js: one place that turns every known error into plain Polish. */
function errorView(msg) {
  const hint = explainError(msg) || (msg ? "⚠️ Coś poszło nie tak. Spróbuj ponownie." : "⚠️ Nieznany błąd.");
  if (!msg) return [el("p", { text: hint })];
  return [el("p", { text: hint }), el("details", {}, el("summary", { text: "Szczegóły" }), el("pre", { class: "out", text: String(msg) }))];
}
/* Safe rich text: escape everything, then allow **bold** and `code` only. */
function richText(text) {
  const frag = document.createDocumentFragment();
  const parts = String(text || "").split(/(\*\*[^*]+\*\*|`[^`]+`)/g);
  for (const p of parts) {
    if (/^\*\*[^*]+\*\*$/.test(p)) frag.append(el("strong", { text: p.slice(2, -2) }));
    else if (/^`[^`]+`$/.test(p)) frag.append(el("code", { text: p.slice(1, -1) }));
    else if (p) frag.append(document.createTextNode(p));
  }
  return frag;
}
/* Polish plural: 1 plik, 2–4 pliki, 5+ plików (12–14 always the "many" form). */
function plural(n, one, few, many) {
  if (n === 1) return one;
  const d = n % 10; const t = n % 100;
  return d >= 2 && d <= 4 && (t < 12 || t > 14) ? few : many;
}
const countOf = (n, one, few, many) => `${n} ${plural(n, one, few, many)}`;
const fmtTime = (ms) => ms ? new Date(ms).toLocaleTimeString("pl-PL", { hour: "2-digit", minute: "2-digit" }) : "";
function dayDiff(ms) {
  const a = new Date(); a.setHours(0, 0, 0, 0);
  const b = new Date(ms); b.setHours(0, 0, 0, 0);
  return Math.round((a - b) / 864e5);
}
function relDay(ms) {
  const d = dayDiff(ms);
  if (d <= 0) return "dziś";
  if (d === 1) return "wczoraj";
  if (d < 7) return `${d} dni temu`;
  return new Date(ms).toLocaleDateString("pl-PL", { day: "numeric", month: "short" });
}
function dayLabel(ms) {
  const d = dayDiff(ms);
  const day = d <= 0 ? "Dziś" : d === 1 ? "Wczoraj" : new Date(ms).toLocaleDateString("pl-PL", { day: "numeric", month: "long" });
  return `${day}, ${fmtTime(ms)}`;
}
const PERM_SHORT = { ask: "Zawsze pyta", smart: "Agent decyduje", auto: "Autonomiczny", full: "Pełny dostęp" };
const PERMISSION_OPTIONS = [["ask", "✋ Zawsze pytaj"], ["smart", "🧠 Agent decyduje, kiedy zapytać"], ["auto", "🚀 Autonomiczny"], ["full", "🔓 Pełny dostęp"]];
const PERMISSION_CHOICES = [
  ["ask", "Zawsze pytaj", "Każde użycie narzędzia czeka na Twoją zgodę."],
  ["smart", "Agent decyduje", "Bezpieczne rzeczy robi sam, o zmiany prosi o zgodę i może zadać Ci pytanie."],
  ["auto", "Autonomiczny", "Sam podejmuje decyzje w ramach wybranych narzędzi."],
  ["full", "Pełny dostęp", "Wszystkie narzędzia, MCP, mody i agenci bez pytania. Tylko dla zaufanych zadań."],
];
const MODE_SHORT = { standard: "Standardowy", reflective: "Refleksyjny", adaptive: "Adaptacyjny" };
const MODE_OPTIONS = [["standard", "Standardowy"], ["reflective", "🔁 Refleksyjny"], ["adaptive", "🎯 Adaptacyjny"]];
const MODE_CHOICES = [
  ["standard", "Standardowy", "Odpowiada od razu."],
  ["reflective", "Refleksyjny", "Sam ocenia odpowiedź, krytykuje ją i poprawia (więcej zapytań do modelu)."],
  ["adaptive", "Adaptacyjny", "Uczy się z 👍/👎, który styl odpowiedzi działa u Ciebie najlepiej."],
];
const STRATEGIES = { zero_shot: "zwięzły", chain_of_thought: "krok po kroku", role: "ekspert" };
const options = (list, current) => list.map(([v, t]) => el("option", { value: v, text: t, selected: v === current }));

async function api(path, { method = "GET", body } = {}) {
  let res;
  try {
    res = await fetch(path, {
      method,
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: "Bearer " + token } : {}) },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    // "Failed to fetch": the phone lost signal, the tab was suspended or the tunnel blinked.
    throw Object.assign(new Error("Brak połączenia z serwerem"), { network: true });
  }
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  if (res.status === 401) { showLogin(); throw new Error("Wymagane logowanie"); }
  if (!res.ok) {
    const raw = (data && data.error) || `Błąd ${res.status}`;
    throw Object.assign(new Error(explainError(raw) || raw), { status: res.status, raw });
  }
  return data;
}
/* Raw file upload (knowledge files, memory exports): the body is the file itself. */
async function upload(path, file) {
  let res;
  try {
    res = await fetch(path, { method: "POST", headers: { "Content-Type": "application/octet-stream", ...(token ? { Authorization: "Bearer " + token } : {}) }, body: file });
  } catch { throw Object.assign(new Error("Brak połączenia z serwerem"), { network: true }); }
  let data = null;
  try { data = await res.json(); } catch { data = null; }
  if (res.status === 401) { showLogin(); throw new Error("Wymagane logowanie"); }
  if (!res.ok) { const raw = (data && data.error) || `Błąd ${res.status}`; throw Object.assign(new Error(explainError(raw) || raw), { status: res.status, raw }); }
  return data;
}
/* Sleep that ends early when the phone comes back online or the tab becomes visible again. */
function napUntilBack(ms) {
  return new Promise((resolve) => {
    const done = () => { clearTimeout(timer); window.removeEventListener("online", done); document.removeEventListener("visibilitychange", onVisible); resolve(); };
    const onVisible = () => { if (document.visibilityState === "visible") done(); };
    const timer = setTimeout(done, ms);
    window.addEventListener("online", done); document.addEventListener("visibilitychange", onVisible);
  });
}
async function waitForProcess(pid, onTick, onOffline) {
  // The agent keeps working on the server, so lost connections are waited out instead of losing the answer.
  for (let polls = 0; polls < 600;) {
    let p;
    try { p = await api(`/processes/${pid}`); } catch (err) {
      if (!err.network) throw err;
      if (onOffline) onOffline();
      await napUntilBack(4000);
      continue;
    }
    polls++;
    if (onTick) onTick(p);
    if (p.status === "completed" || p.status === "failed") return p;
    await new Promise((r) => setTimeout(r, polls < 10 ? 700 : 1500));
  }
  throw new Error("Przekroczono czas oczekiwania");
}
function withBusy(form, fn) {
  return async (e) => {
    e.preventDefault();
    const btn = form.querySelector("button[type=submit]");
    if (btn) btn.disabled = true;
    try { await fn(new FormData(form)); } catch (err) { toast(err.message, true); } finally { if (btn) btn.disabled = false; }
  };
}
function openDetails(id) {
  const d = document.getElementById(id);
  if (!d) return;
  d.open = true;
  setTimeout(() => d.scrollIntoView({ behavior: "smooth", block: "start" }), 60);
}

/* ------------------------------------------------------------ bottom sheet */
function openSheet(title, ...content) {
  $("#sheet-title").textContent = title;
  $("#sheet-body").replaceChildren(...content.flat().filter(Boolean));
  $("#sheet").classList.remove("hidden");
  $("#sheet-close").focus();
}
function closeSheet() { $("#sheet").classList.add("hidden"); $("#sheet-body").replaceChildren(); state.sheetPid = null; }
$("#sheet-close").addEventListener("click", closeSheet);
$("#sheet").addEventListener("click", (e) => { if (e.target.id === "sheet") closeSheet(); });
document.addEventListener("keydown", (e) => { if (e.key === "Escape" && !$("#sheet").classList.contains("hidden")) closeSheet(); });
function choiceSheet(title, choices, current, onPick) {
  const list = el("div", { class: "choices" }, ...choices.map(([value, label, hint]) => el("label", { class: "choice" + (value === "full" ? " danger" : "") },
    el("input", { type: "radio", name: "sheet-choice", value, checked: value === current, onchange: () => { closeSheet(); onPick(value); } }),
    el("span", {}, el("b", { text: label }), hint ? el("small", { text: hint }) : null))));
  openSheet(title, list);
}

/* ------------------------------------------------------------------ login */
function showLogin() {
  $("#app").classList.add("hidden"); $("#login").classList.remove("hidden");
  if (!$("#login-server").value) $("#login-server").value = location.origin;
  $("#login-token").focus();
}
function normalizeServer(value) {
  let v = String(value || "").trim().replace(/\\/g, "/");
  if (!v) return location.origin;
  if (!/^https?:\/\//i.test(v)) v = "https://" + v;
  try { return new URL(v).origin; } catch { return null; }
}
async function tryToken(candidate) {
  token = candidate;
  await api("/auth/check");
  store.set("aos_token", token);
  $("#login-error").textContent = "";
  start();
}
$("#login-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const server = normalizeServer($("#login-server").value);
  if (!server) { $("#login-error").textContent = "To nie wygląda na adres serwera. Przykład: https://twoj-serwer-8000.app.github.dev"; return; }
  if (server !== location.origin) {
    // The password belongs to the other server, so open it there.
    if (isApp()) { location.href = "agentic-os://settings"; return; }
    location.href = server + "/";
    return;
  }
  const btn = e.submitter || $(".login-submit"); btn.disabled = true;
  try { await tryToken($("#login-token").value.trim()); }
  catch (err) { $("#login-error").textContent = err.network ? "Nie mogę połączyć się z serwerem. Sprawdź, czy działa." : "Nieprawidłowe hasło."; }
  finally { btn.disabled = false; }
});
/* "Połącz telefon" QR codes carry https://server/#connect=<password>. */
async function useConnectLink(text) {
  let url;
  try { url = new URL(String(text).trim()); } catch { throw new Error("Ten kod QR nie pochodzi z Agentic OS."); }
  const m = /^#connect=(.*)$/.exec(url.hash);
  if (!m) throw new Error("Ten kod QR nie pochodzi z Agentic OS.");
  if (url.origin !== location.origin) {
    if (isApp()) { $("#login-server").value = url.origin; throw new Error(`Kod jest dla serwera ${url.host}. Ustaw ten adres w aplikacji (Adres serwera).`); }
    location.href = url.href; return;
  }
  await tryToken(decodeURIComponent(m[1]));
}
$("#login-qr").addEventListener("click", () => {
  if (!("BarcodeDetector" in window)) {
    $("#login-error").textContent = "Ta przeglądarka nie czyta kodów QR. Zeskanuj kod aparatem telefonu: link sam otworzy War Room.";
    return;
  }
  $("#login-qr-file").click();
});
$("#login-qr-file").addEventListener("change", async (e) => {
  const file = e.target.files[0]; e.target.value = "";
  if (!file) return;
  try {
    const bitmap = await createImageBitmap(file);
    const codes = await new BarcodeDetector({ formats: ["qr_code"] }).detect(bitmap);
    if (!codes.length) throw new Error("Nie widzę kodu QR na zdjęciu. Spróbuj jeszcze raz, bliżej ekranu.");
    await useConnectLink(codes[0].rawValue);
  } catch (err) { $("#login-error").textContent = err.message; }
});
(function readConnectHash() {
  const m = /^#connect=(.*)$/.exec(location.hash);
  if (!m) return;
  token = decodeURIComponent(m[1]); store.set("aos_token", token);
  history.replaceState(null, "", location.pathname + location.search);
})();

/* ------------------------------------------------------------ look & feel */
const THEMES = { light: "Jasny", dark: "Ciemny", system: "Systemowy" };
const ACCENTS = { teal: "Morski", indigo: "Indygo", amber: "Bursztyn", pink: "Malinowy" };
function currentTheme() { const t = store.get("aos_theme", "system"); return THEMES[t] ? t : "system"; }
function currentAccent() { const a = store.get("aos_accent", "teal"); return ACCENTS[a] ? a : "teal"; }
function applyTheme(mode) {
  if (mode === "system") { delete document.documentElement.dataset.theme; store.del("aos_theme"); }
  else { document.documentElement.dataset.theme = mode; store.set("aos_theme", mode); }
  const radio = document.querySelector(`#theme-choice input[value="${mode}"]`);
  if (radio) radio.checked = true;
  redrawBrain();
}
function applyAccent(accent) {
  if (accent === "teal") { delete document.documentElement.dataset.accent; store.del("aos_accent"); }
  else { document.documentElement.dataset.accent = accent; store.set("aos_accent", accent); }
  const radio = document.querySelector(`#accent-choice input[value="${accent}"]`);
  if (radio) radio.checked = true;
}
$("#theme-choice").addEventListener("change", (e) => { applyTheme(e.target.value); toast(`Motyw: ${THEMES[e.target.value]}`); });
$("#accent-choice").addEventListener("change", (e) => { applyAccent(e.target.value); toast(`Kolor akcentu: ${ACCENTS[e.target.value]}`); });
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", redrawBrain);
function redrawBrain() { if (state.tab === "brain" && brain.nodes.length) simulate(300); }

/* ------------------------------------------------------------------- tabs */
/* Five tabs in the bottom bar; the other screens open from them and keep their tab lit. */
const TAB_PARENT = { agents: "me", ext: "me", monitor: "me", brain: "knowledge", convo: "chat" };
const LOADERS = {
  chat: () => loadStart(), convo: () => openConvo(), agents: () => loadAgents(), tasks: () => loadTasks(), brain: () => loadBrain(),
  knowledge: () => loadKnowledge(), ext: () => loadExt(), models: () => loadModels(), monitor: () => loadMonitor(), me: () => loadMe(),
};
function showTab(name) {
  if (!document.getElementById("tab-" + name)) name = "chat";
  state.tab = name;
  const lit = TAB_PARENT[name] || name;
  document.querySelectorAll(".tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === lit));
  document.querySelectorAll(".panel").forEach((p) => p.classList.toggle("active", p.id === "tab-" + name));
  document.body.classList.toggle("in-convo", name === "convo");
  store.set("aos_tab", name);
  (LOADERS[name] || (() => {}))();
  const panel = document.getElementById("tab-" + name);
  if (name !== "convo") panel.scrollTop = 0;
  renderApprovals(state.approvals || [], true);
}
document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => showTab(t.dataset.tab)));
document.querySelectorAll("[data-go]").forEach((b) => b.addEventListener("click", () => showTab(b.dataset.go)));

/* --------------------------------------------------------------- shared */
function currentAgent() {
  const name = store.get("aos_chat_agent", "assistant");
  return state.agents.some((a) => a.name === name) ? name : "assistant";
}
const agentInfo = (name = currentAgent()) => state.agents.find((a) => a.name === name) || { name, kind: "native" };
function selectAgent(name) {
  store.set("aos_chat_agent", name);
  $("#chat-agent").value = name;
}
async function refreshAgents() {
  const data = await api("/agents");
  state.agents = data.agents; state.tools = data.tools; state.extPresets = data.external_presets;
  const opts = () => state.agents.map((a) => el("option", { value: a.name, text: `${a.name}${a.kind === "external" ? " (zewn.)" : ""}` }));
  $("#chat-agent").replaceChildren(...opts()); $("#chat-agent").value = currentAgent();
  const sa = $("#schedule-agent"); const keep = sa.value; sa.replaceChildren(...opts()); sa.value = keep || currentAgent();
}
function providerName(p) { return (p.label || p.id).replace(/^Google\s+/, ""); }
async function refreshProviders() {
  const data = await api("/providers");
  state.providers = data.providers; state.presets = data.presets; state.def = data.default;
  const d = data.default;
  // Without a configured provider the OS falls back to an offline demo model that cannot understand questions.
  const offline = !d.model && (!d.name || d.name === "heuristic");
  const p = state.providers.find((x) => x.id === d.provider);
  $("#model-pill-text").textContent = offline ? "brak modelu AI" : p ? providerName(p) : (d.model || d.name);
  $("#model-pill").classList.toggle("off", offline);
  $("#offline-banner").classList.toggle("hidden", !offline);
  return data;
}
/* Change an agent's permission or thinking mode at any time (applies immediately, even to a running task). */
async function changeAgent(name, changes, select) {
  const before = state.agents.find((a) => a.name === name) || {};
  if (changes.permission === "full" && before.permission !== "full" &&
      !confirm(`Pełny dostęp: ${name} użyje każdego narzędzia, serwera MCP, moda i agenta bez pytania. Kontynuować?`)) {
    if (select) select.value = before.permission || "auto";
    return;
  }
  try {
    const updated = await api(`/agents/${name}/settings`, { method: "POST", body: changes });
    Object.assign(before, updated);
    toast(`${name}: ${changes.permission ? PERM_SHORT[updated.permission] : MODE_SHORT[updated.mode] || "Standardowy"}`);
    renderConvoHead();
    if (state.tab === "agents") loadAgents();
    if (state.tab === "me") loadMe();
  } catch (err) {
    toast(err.message, true);
    if (select) select.value = changes.permission ? before.permission : before.mode;
  }
}

/* ------------------------------------------------------- chat: start (C1) */
function agentRole(a) {
  if (a.kind === "external") return "Zewnętrzny";
  if (a.name === "assistant") return "Ogólny";
  const d = String(a.description || "").trim();
  return d && d.length <= 22 ? d : (a.skills && a.skills[0]) || "Agent";
}
function renderAgentCards() {
  const current = currentAgent();
  const cards = state.agents.map((a, i) => el("button", { type: "button", role: "listitem", class: "agent-card" + (a.name === current ? " on" : ""),
    onclick: () => { selectAgent(a.name); showTab("convo"); } },
  el("span", { class: "tile " + (i % 2 ? "amber" : "soft") }, icon(i % 2 ? "pen" : "robot", 18)),
  el("strong", { text: a.name }), el("span", { text: agentRole(a) })));
  cards.push(el("button", { type: "button", role: "listitem", class: "agent-card new", onclick: () => { showTab("agents"); openDetails("agent-form-card"); } },
    el("span", { class: "tile" }, icon("plus", 18)), el("strong", { text: "Nowy" }), el("span", { text: "Agent" })));
  $("#agent-cards").replaceChildren(...cards);
}
function loadStart() {
  const h = new Date().getHours();
  $("#hello-greeting").textContent = h >= 18 || h < 5 ? "Dobry wieczór" : "Dzień dobry";
  renderAgentCards();
  Promise.all([refreshAgents(), refreshProviders()]).then(renderAgentCards).catch(() => {});
}
$("#start-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const text = $("#start-text").value.trim(); if (!text) { $("#start-text").focus(); return; }
  $("#start-text").value = "";
  showTab("convo"); sendMessage(text);
});
const QUICK = {
  notes: () => { showTab("convo"); sendMessage("Streść moje notatki z bazy wiedzy w kilku punktach."); },
  week: () => { showTab("convo"); sendMessage("Zaplanuj mi tydzień na podstawie moich zadań i notatek."); },
  crew: () => { showTab("agents"); openDetails("crew-form-card"); },
  import: () => { showTab("brain"); openDetails("mem-import-card"); },
};
document.querySelectorAll("[data-quick]").forEach((b) => b.addEventListener("click", () => QUICK[b.dataset.quick]()));
$("#offline-fix").addEventListener("click", () => showTab("models"));
/* Voice input (Web Speech API); the mic button only appears where the browser supports it. */
(function setupMic() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) return;
  const btn = $("#start-mic"); btn.classList.remove("hidden");
  let rec = null;
  btn.addEventListener("click", () => {
    if (rec) { rec.stop(); return; }
    rec = new Recognition(); rec.lang = "pl-PL"; rec.interimResults = true;
    const base = $("#start-text").value ? $("#start-text").value + " " : "";
    rec.onresult = (ev) => { $("#start-text").value = base + Array.from(ev.results).map((r) => r[0].transcript).join(""); };
    rec.onerror = (ev) => { if (ev.error === "not-allowed") toast("Zezwól na mikrofon w ustawieniach przeglądarki.", true); };
    rec.onend = () => { rec = null; btn.classList.remove("listening"); btn.setAttribute("aria-label", "Mów"); };
    btn.classList.add("listening"); btn.setAttribute("aria-label", "Zatrzymaj nagrywanie");
    rec.start();
  });
})();

/* -------------------------------------------------- chat: conversation (C3) */
const chatLog = $("#chat-log");
function sessionId(agent) {
  let s = store.get("aos_session_" + agent);
  if (!s) { s = Math.random().toString(36).slice(2, 10); store.set("aos_session_" + agent, s); }
  return s;
}
function renderConvoHead() {
  const a = agentInfo();
  $("#convo-name").textContent = a.name;
  const idx = state.agents.findIndex((x) => x.name === a.name);
  const av = $("#convo-avatar"); av.classList.toggle("amber", idx % 2 === 1); av.replaceChildren(icon(idx % 2 === 1 ? "pen" : "robot"));
  $("#convo-sub").textContent = a.kind === "external" ? `${a.protocol || "zewnętrzny"} · agent zewnętrzny`
    : `${a.model || state.def.model || "offline"} · ${PERM_SHORT[a.permission] || "Autonomiczny"}`;
  const native = a.kind !== "external";
  $("#chat-permission").closest("label").classList.toggle("hidden", !native);
  $("#chat-mode").closest("label").classList.toggle("hidden", !native);
  if (native) { $("#chat-permission").replaceChildren(...options(PERMISSION_OPTIONS, a.permission)); $("#chat-mode").replaceChildren(...options(MODE_OPTIONS, a.mode)); }
}
function openConvo() {
  $("#chat-agent").value = currentAgent();
  renderConvoHead(); renderChat();
  setTimeout(() => { if (window.innerWidth > 900) $("#chat-text").focus(); }, 50);
}
$("#convo-back").addEventListener("click", () => showTab("chat"));
$("#convo-settings").addEventListener("click", () => {
  const sheet = $("#convo-sheet"); const open = sheet.classList.toggle("hidden") === false;
  $("#convo-settings").setAttribute("aria-expanded", String(open));
});
$("#chat-agent").addEventListener("change", (e) => { selectAgent(e.target.value); renderConvoHead(); renderChat(); });
$("#chat-permission").addEventListener("change", (e) => changeAgent(currentAgent(), { permission: e.target.value }, e.target));
$("#chat-mode").addEventListener("change", (e) => changeAgent(currentAgent(), { mode: e.target.value }, e.target));
$("#chat-reset").addEventListener("click", async () => {
  const agent = currentAgent();
  try { await api("/chat/reset", { method: "POST", body: { agent, session: sessionId(agent) } }); } catch { /* ignore */ }
  store.del(chatKey(agent)); store.del("aos_session_" + agent); renderChat(); toast("Nowa rozmowa");
  $("#convo-sheet").classList.add("hidden");
});

function addMsg(role, text) {
  $(".empty", chatLog)?.remove();
  const m = el("div", { class: "msg " + role });
  if (text) m.append(richText(text));
  insertBeforeAsks(m);
  return m;
}
function insertBeforeAsks(node) {
  const firstAsk = $(".ask-card", chatLog);
  if (firstAsk) chatLog.insertBefore(node, firstAsk); else chatLog.append(node);
  chatLog.scrollTop = chatLog.scrollHeight;
}
function toolChipLabel(r) {
  const n = (r.tool_calls || []).length; const s = r.steps || 1;
  return [n ? countOf(n, "narzędzie", "narzędzia", "narzędzi") : null, countOf(s, "krok", "kroki", "kroków")].filter(Boolean).join(" · ");
}
function renderAgentReply(node, proc) {
  node.classList.remove("thinking"); node.replaceChildren();
  if (proc.status === "failed") { node.append(...errorView(proc.error)); return; }
  const r = proc.result || {};
  node.append(el("span", {}, richText(r.output || "(brak odpowiedzi)")));
  const detail = el("div", { class: "tool-detail hidden" });
  if (r.tool_calls && r.tool_calls.length) detail.append(...r.tool_calls.map((c) => el("pre", { text: `${c.tool}(${JSON.stringify(c.arguments)})\n→ ${c.result}` })));
  if (r.reflection) detail.append(el("div", { class: "meta", text: `🔁 Samoocena: ${Math.round(r.reflection.best_score * 100)}% (próby: ${r.reflection.attempts.length})` }));
  if (r.citations && r.citations.length) detail.append(el("div", { class: "meta", text: "📚 Źródła: " + r.citations.map((c) => `[${c.n}] ${c.source}`).join(", ") }));
  const usage = r.usage || {};
  detail.append(el("div", { class: "meta", text: `${r.agent || ""}${r.strategy ? ` · styl: ${STRATEGIES[r.strategy] || r.strategy}` : ""}${usage.input_tokens ? ` · tokeny: ${usage.input_tokens + usage.output_tokens}` : ""}` }));
  const fb = el("span", { class: "fb" });
  for (const [label, reward] of [["👍", 1], ["👎", -1]]) {
    fb.append(el("button", { type: "button", "aria-label": reward > 0 ? "Dobra odpowiedź" : "Zła odpowiedź", text: label, onclick: async (ev) => {
      try { await api(`/processes/${proc.pid}/feedback`, { method: "POST", body: { reward } }); fb.querySelectorAll("button").forEach((b) => b.classList.remove("on")); ev.currentTarget.classList.add("on"); toast("Dzięki, agent się uczy."); } catch (err) { toast(err.message, true); }
    } }));
  }
  detail.append(fb);
  const chip = el("button", { type: "button", class: "tool-chip", "aria-expanded": "false", onclick: () => {
    const open = detail.classList.toggle("hidden") === false; chip.setAttribute("aria-expanded", String(open));
  } }, icon("wrench", 15), toolChipLabel(r), icon("chevDown", 14));
  node.append(chip, detail);
}
/* The conversation is kept in this browser so a reload, a dropped connection or a closed tab never loses an answer. */
const CHAT_KEEP = 60;
const followed = new Set();
function chatKey(agent) { return `aos_chat_${agent}_${sessionId(agent)}`; }
function loadChat(agent) { try { return JSON.parse(store.get(chatKey(agent), "[]")) || []; } catch { return []; } }
function saveChat(agent, entries) {
  let keep = entries.slice(-CHAT_KEEP);
  // Drop the oldest messages when the browser storage is full.
  while (keep.length) { store.set(chatKey(agent), JSON.stringify(keep)); if (store.get(chatKey(agent)) === JSON.stringify(keep)) return; keep = keep.slice(Math.ceil(keep.length / 4)); }
}
function updateChat(agent, fn) { const entries = loadChat(agent); fn(entries); saveChat(agent, entries); }
function compactProc(p) {
  const r = p.result || {};
  const clip = (v) => { const t = typeof v === "string" ? v : JSON.stringify(v); return t && t.length > 1500 ? t.slice(0, 1500) + "…" : t; };
  return { pid: p.pid, status: p.status, error: p.error, result: { output: r.output, agent: r.agent, strategy: r.strategy, steps: r.steps, usage: r.usage,
    citations: r.citations, reflection: r.reflection, tool_calls: (r.tool_calls || []).map((c) => ({ tool: c.tool, arguments: c.arguments, result: clip(c.result) })) } };
}
function followReply(agent, pid, node) {
  if (followed.has(pid)) return;
  followed.add(pid);
  const offline = () => { if (node.isConnected) { node.classList.add("thinking"); node.textContent = "📶 Brak połączenia – agent pracuje dalej, pokażę odpowiedź, gdy wróci sieć…"; } };
  const tick = (p) => {
    if (!node.isConnected) return;
    const label = p.status === "waiting" ? "Czekam na Twoją decyzję…" : p.step > 1 ? `Pracuję… krok ${p.step} z ~${p.max_steps}` : "Myślę…";
    if (node.classList.contains("thinking")) node.textContent = label;
  };
  waitForProcess(pid, tick, offline).catch((err) => ({ pid, status: "failed",
    error: err.status === 404 ? "Ta odpowiedź przepadła (serwer został uruchomiony ponownie). Wyślij pytanie jeszcze raz." : err.message }))
    .then((done) => {
      followed.delete(pid);
      updateChat(agent, (entries) => { const e = entries.find((x) => x.pid === pid); if (e) e.done = compactProc(done); });
      if (node.isConnected) { renderAgentReply(node, done); chatLog.scrollTop = chatLog.scrollHeight; }
    });
}
function chatEmpty() {
  chatLog.replaceChildren(el("div", { class: "empty empty-note", style: "margin:auto;text-align:center" }, el("div", { text: "👋 Napisz, co mam zrobić." }),
    el("div", { class: "small", text: "Agent użyje narzędzi, pamięci i Twojej bazy wiedzy." })));
}
function renderChat() {
  const agent = currentAgent();
  const entries = loadChat(agent);
  chatLog.replaceChildren();
  if (!entries.length) chatEmpty();
  let lastDay = null;
  for (const e of entries) {
    if (e.at && (lastDay === null || dayDiff(e.at) !== lastDay)) { lastDay = dayDiff(e.at); chatLog.append(el("span", { class: "day-sep", text: dayLabel(e.at) })); }
    if (e.role === "user") { addMsg("user", e.text); continue; }
    if (e.role === "note") { addMsg("note", e.text); continue; }
    const node = addMsg("agent thinking", e.pid ? "Myślę…" : "⚠️ " + (e.error || "Błąd"));
    if (e.done) renderAgentReply(node, e.done);
    else if (e.pid) followReply(agent, e.pid, node);
    else node.classList.remove("thinking");
  }
  renderApprovals(state.approvals || [], true);
  chatLog.scrollTop = chatLog.scrollHeight;
}
async function sendMessage(text) {
  const agent = currentAgent();
  const entries = loadChat(agent);
  const last = entries.filter((e) => e.at).pop();
  if (!last || dayDiff(last.at) !== 0 || Date.now() - last.at > 30 * 60 * 1000) { $(".empty", chatLog)?.remove(); insertBeforeAsks(el("span", { class: "day-sep", text: dayLabel(Date.now()) })); }
  addMsg("user", text);
  updateChat(agent, (list) => list.push({ role: "user", text, at: Date.now() }));
  const reply = addMsg("agent thinking", "Myślę…");
  let proc;
  try {
    proc = await api("/chat", { method: "POST", body: { message: text, agent, session: sessionId(agent), async: true } });
  } catch (err) {
    reply.classList.remove("thinking"); reply.textContent = "⚠️ " + err.message + (err.network ? " – wiadomość nie dotarła, wyślij ją ponownie." : "");
    updateChat(agent, (list) => list.push({ role: "agent", error: reply.textContent.slice(2), at: Date.now() }));
    return;
  }
  updateChat(agent, (list) => list.push({ role: "agent", pid: proc.pid, at: Date.now() }));
  followReply(agent, proc.pid, reply);
}
$("#chat-form").addEventListener("submit", (e) => {
  e.preventDefault();
  const ta = $("#chat-text"); const text = ta.value.trim(); if (!text) { ta.focus(); return; }
  ta.value = ""; ta.style.height = "";
  sendMessage(text);
});
$("#chat-text").addEventListener("keydown", (e) => { if (e.key === "Enter" && !e.shiftKey && !e.isComposing && window.innerWidth > 900) { e.preventDefault(); $("#chat-form").requestSubmit(); } });
$("#chat-text").addEventListener("input", (e) => { e.target.style.height = ""; e.target.style.height = Math.min(e.target.scrollHeight, 140) + "px"; });
$("#chat-attach").addEventListener("click", () => $("#chat-file").click());
$("#chat-file").addEventListener("change", async (e) => {
  const file = e.target.files[0]; e.target.value = "";
  if (!file) return;
  const agent = currentAgent();
  const note = addMsg("note", `📎 Wgrywam ${file.name}…`);
  try {
    const r = await uploadKnowledge(file);
    const text = `📎 Dodano do wiedzy: ${file.name} (${countOf(r.chunks, "fragment", "fragmenty", "fragmentów")}). Agent może teraz z niego korzystać.`;
    note.textContent = text;
    updateChat(agent, (list) => list.push({ role: "note", text, at: Date.now() }));
  } catch (err) { note.textContent = "⚠️ " + err.message; }
});

/* ------------------------------------------------- approvals and questions */
function toolAction(name) {
  const n = String(name || "").toLowerCase();
  const rules = [[/write|save|zapis|create_file|append|file/, "zapisać plik"], [/delete|remove|usun|drop/, "coś usunąć"],
    [/mail|send|wysl|message|post|notify/, "wysłać wiadomość"], [/http|fetch|request|web|url|browse|download/, "połączyć się z internetem"],
    [/^ask_|delegate|agent/, "zlecić zadanie innemu agentowi"], [/calc/, "coś policzyć"], [/search|szukaj|find|query/, "coś wyszukać"],
    [/read|get|list|load/, "odczytać dane"]];
  const hit = rules.find(([re]) => re.test(n));
  return hit ? hit[1] : "użyć narzędzia";
}
function argsSummary(args) {
  const parts = Object.entries(args || {}).slice(0, 3).map(([k, v]) => {
    const t = typeof v === "string" ? v : JSON.stringify(v);
    return `${k}: ${t.length > 120 ? t.slice(0, 120) + "…" : t}`;
  });
  return parts.join(" · ") || "bez parametrów";
}
function deadlineText(id) {
  const left = Math.max(0, Math.round((state.deadlines[id] - Date.now()) / 1000));
  return `Czeka na Ciebie jeszcze ${Math.floor(left / 60)}:${String(left % 60).padStart(2, "0")}`;
}
function approvalCard(a, withAgent) {
  state.deadlines[a.id] ??= Date.now() + (a.expires_in ?? 300) * 1000;
  const wait = el("span", { "data-deadline": a.id, text: deadlineText(a.id) });
  const who = withAgent ? a.agent : "Agent";
  if (a.kind === "question") {
    const input = el("textarea", { placeholder: "Twoja odpowiedź…", "aria-label": "Odpowiedź dla agenta", rows: "2" });
    return el("section", { class: "ask-card", "aria-label": "Pytanie agenta", "data-ask": a.id },
      el("div", { class: "ask-top" }, el("span", { class: "tile soft" }, icon("question")), el("div", {}, el("strong", { text: `${who} pyta` }), wait)),
      el("div", { class: "ask-box" }, el("span", { text: "Pytanie" }), el("span", { text: a.arguments.question || "" })),
      input,
      el("div", { class: "ask-actions two" },
        el("button", { type: "button", class: "yes", text: "Odpowiedz", onclick: () => {
          if (!input.value.trim()) { toast("Wpisz odpowiedź albo pomiń", true); return; }
          decide(a.id, { answer: input.value.trim() });
        } }),
        el("button", { type: "button", text: "Pomiń", title: "Niech agent zdecyduje sam", onclick: () => decide(a.id, { answer: "" }) })));
  }
  return el("section", { class: "ask-card", "aria-label": "Prośba o zgodę", "data-ask": a.id },
    el("div", { class: "ask-top" }, el("span", { class: "tile soft" }, icon("shield")), el("div", {}, el("strong", { text: `${who} chce ${toolAction(a.tool)}` }), wait)),
    el("div", { class: "ask-box" }, el("span", { text: `Narzędzie: ${a.tool}` }), el("span", { text: argsSummary(a.arguments) })),
    el("div", { class: "ask-actions" },
      el("button", { type: "button", class: "yes", text: "Zezwól", onclick: () => decide(a.id, { approve: true }) }),
      el("button", { type: "button", text: "Zawsze", title: "Zezwalaj temu agentowi na to narzędzie bez pytania", onclick: () => decide(a.id, { approve: true, remember: true }) }),
      el("button", { type: "button", class: "no", text: "Odmów", onclick: () => decide(a.id, { approve: false }) })));
}
async function pollApprovals() {
  clearTimeout(state.timers.approvals);
  const visible = document.visibilityState === "visible";
  if (!$("#app").classList.contains("hidden") && (visible || notificationsOn())) {
    try {
      const { approvals } = await api("/approvals");
      for (const a of approvals) {
        if (!state.seenApprovals.has(a.id)) { state.seenApprovals.add(a.id); if (!visible) notify(a); }
      }
      renderApprovals(approvals);
    } catch { /* offline or logged out: try again later */ }
  }
  state.timers.approvals = setTimeout(pollApprovals, visible ? 2500 : 10000);
}
/* Approvals of the open conversation's agent appear inside the chat (as in the mock-up); the rest in a bar on top. */
function renderApprovals(list, force = false) {
  state.approvals = list;
  const inline = state.tab === "convo" ? list.filter((a) => a.agent === currentAgent()) : [];
  const elsewhere = list.filter((a) => !inline.includes(a));
  const key = `${state.tab}|${currentAgent()}|${list.map((a) => a.id).join(",")}`;
  if (key === state.approvalKey && !force) return; // keep a half-typed answer intact between polls
  state.approvalKey = key;
  chatLog.querySelectorAll(".ask-card").forEach((n) => { if (!inline.some((a) => a.id === n.dataset.ask)) n.remove(); });
  for (const a of inline) if (!chatLog.querySelector(`[data-ask="${a.id}"]`)) { chatLog.append(approvalCard(a, false)); chatLog.scrollTop = chatLog.scrollHeight; }
  const box = $("#approvals");
  box.classList.toggle("hidden", !elsewhere.length);
  box.querySelectorAll(".ask-card").forEach((n) => { if (!elsewhere.some((a) => a.id === n.dataset.ask)) n.remove(); });
  for (const a of elsewhere) if (!box.querySelector(`[data-ask="${a.id}"]`)) box.append(approvalCard(a, true));
}
setInterval(() => document.querySelectorAll("[data-deadline]").forEach((n) => { n.textContent = deadlineText(n.dataset.deadline); }), 1000);
async function decide(id, body) {
  try {
    await api(`/approvals/${id}`, { method: "POST", body });
    toast(body.answer !== undefined ? (body.answer ? "Odpowiedź wysłana" : "Agent zdecyduje sam") : body.approve ? (body.remember ? "Zezwolono na stałe" : "Zezwolono") : "Odmówiono");
  } catch (err) { toast(err.message, true); }
  document.querySelectorAll(`[data-ask="${id}"]`).forEach((n) => n.remove());
  state.approvalKey = null;
  pollApprovals();
}
document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible") pollApprovals(); });

/* "Powiadomienia o prośbach": a system notification when an agent waits for you and the app is in the background. */
const notificationsOn = () => store.get("aos_notify") === "1" && "Notification" in window && Notification.permission === "granted";
async function notify(a) {
  if (!notificationsOn()) return;
  const title = a.kind === "question" ? `${a.agent} pyta` : `${a.agent} czeka na Twoją zgodę`;
  const body = a.kind === "question" ? (a.arguments.question || "") : `Chce ${toolAction(a.tool)} (${a.tool})`;
  try {
    const reg = navigator.serviceWorker && await navigator.serviceWorker.getRegistration();
    if (reg) await reg.showNotification(title, { body, tag: a.id, icon: "/icon-192.png" });
    else new Notification(title, { body, tag: a.id });
  } catch { /* the browser refused: nothing else to do */ }
}

/* ----------------------------------------------------------------- agents */
async function loadAgents() {
  let skills = [];
  try { [, , { skills }] = await Promise.all([refreshAgents(), refreshProviders(), api("/skills")]); } catch (err) { toast(err.message, true); return; }
  $("#agent-skills").replaceChildren(...(skills.length ? skills.map((s) => el("label", { class: "chip" }, el("input", { type: "checkbox", name: "skills", value: s.name }), s.name)) : [el("span", { class: "muted small", text: "Dodaj skille w Ty → Rozszerzenia." })]));
  $("#agent-list").replaceChildren(...state.agents.map((a) => el("div", { class: "item" },
    el("div", { class: "item-head" }, el("span", { class: "item-title", text: (a.kind === "external" ? "🔌 " : "🤖 ") + a.name }),
      el("span", { class: "tag", text: a.kind === "external" ? a.protocol : `${a.provider} · ${a.model || "?"}` })),
    el("p", { class: "muted small", text: a.description || "" }),
    a.tools && a.tools.length ? el("p", { class: "small", text: "🛠 " + a.tools.join(", ") }) : null,
    a.skills && a.skills.length ? el("p", { class: "small", text: "🎓 " + a.skills.join(", ") }) : null,
    agentTraits(a),
    a.learning ? el("p", { class: "small", text: "📈 " + Object.entries(a.learning.strategies).map(([k, v]) => `${STRATEGIES[k] || k}: ${v.pulls ? `${v.mean_reward > 0 ? "+" : ""}${v.mean_reward} (${v.pulls}×)` : "–"}`).join(" · ") + (a.learning.best ? ` → najlepszy: ${STRATEGIES[a.learning.best] || a.learning.best}` : "") }) : null,
    el("div", { class: "actions" },
      el("button", { class: "btn small", type: "button", text: "💬 Czat", onclick: () => { selectAgent(a.name); showTab("convo"); } }),
      a.name !== "assistant" ? el("button", { class: "btn small ghost danger", type: "button", text: "Usuń", onclick: async () => {
        if (!confirm(`Usunąć agenta ${a.name}?`)) return;
        try { await api(`/agents/${a.name}`, { method: "DELETE" }); toast("Usunięto"); loadAgents(); } catch (err) { toast(err.message, true); }
      } }) : null))));
  const provSel = $("#agent-provider");
  provSel.replaceChildren(el("option", { value: "default", text: "Domyślny systemu" }), ...state.providers.map((p) => el("option", { value: p.id, text: p.label || p.id })));
  $("#agent-tools").replaceChildren(...state.tools.map((t) => el("label", { class: "chip" }, el("input", { type: "checkbox", name: "tools", value: t, checked: true }), t)));
  $("#agent-delegates").replaceChildren(...state.agents.map((a) => el("label", { class: "chip" }, el("input", { type: "checkbox", name: "delegates", value: a.name }), a.name)));
  $("#crew-agents").replaceChildren(...state.agents.map((a) => el("label", { class: "chip" }, el("input", { type: "checkbox", name: "agents", value: a.name }), a.name)));
  const ext = $("#ext-preset");
  if (!ext.options.length) {
    ext.replaceChildren(el("option", { value: "", text: "— wybierz —" }), ...state.extPresets.map((p, i) => el("option", { value: String(i), text: p.label })));
  }
}
function agentTraits(a) {
  if (a.kind === "external") return null;
  const perm = el("select", { "aria-label": `Uprawnienia ${a.name}`, onchange: (e) => changeAgent(a.name, { permission: e.target.value }, e.target) }, ...options(PERMISSION_OPTIONS, a.permission));
  const mode = el("select", { "aria-label": `Tryb myślenia ${a.name}`, onchange: (e) => changeAgent(a.name, { mode: e.target.value }, e.target) }, ...options(MODE_OPTIONS, a.mode));
  return el("div", {},
    el("div", { class: "agent-settings" },
      el("label", { class: "field" }, el("span", { text: "Uprawnienia" }), perm),
      el("label", { class: "field" }, el("span", { text: "Tryb myślenia" }), mode)),
    a.delegates && a.delegates.length ? el("p", { class: "small", text: "📨 zleca: " + a.delegates.join(", ") }) : null,
    a.always_allow && a.always_allow.length ? el("p", { class: "small" }, `✅ Zawsze dozwolone: ${a.always_allow.join(", ")} `,
      el("button", { class: "btn small ghost", type: "button", text: "Resetuj", onclick: async () => {
        try { await api(`/agents/${a.name}/allowed`, { method: "DELETE" }); toast("Zgody zresetowane"); loadAgents(); } catch (err) { toast(err.message, true); }
      } })) : null);
}
$("#ext-preset").addEventListener("change", (e) => {
  const p = state.extPresets[Number(e.target.value)]; const f = $("#ext-form");
  if (!p) { $("#ext-note").textContent = ""; return; }
  f.elements.name.value = p.name; f.elements.protocol.value = p.protocol; f.elements.url.value = p.url; $("#ext-note").textContent = p.note;
});
$("#agent-form").addEventListener("submit", withBusy($("#agent-form"), async (fd) => {
  const body = { name: fd.get("name"), instructions: fd.get("instructions") || undefined, provider: fd.get("provider"),
    model: fd.get("model") || undefined, tools: fd.getAll("tools"), skills: fd.getAll("skills"), conversational: fd.get("conversational") === "on",
    mode: fd.get("mode"), permission: fd.get("permission") || "auto", delegates: fd.getAll("delegates") };
  if (body.permission === "full" && !confirm("Pełny dostęp: agent użyje każdego narzędzia, serwera MCP, moda i agenta bez pytania. Kontynuować?")) return;
  await api("/agents", { method: "POST", body }); toast("Agent utworzony ✅"); $("#agent-form").reset(); loadAgents();
}));
$("#ext-form").addEventListener("submit", withBusy($("#ext-form"), async (fd) => {
  await api("/agents/external", { method: "POST", body: Object.fromEntries(fd) });
  toast("Agent podłączony ✅"); $("#ext-form").reset(); $("#ext-note").textContent = ""; loadAgents();
}));
$("#crew-form").addEventListener("submit", withBusy($("#crew-form"), async (fd) => {
  const agents = fd.getAll("agents"); if (!agents.length) throw new Error("Wybierz co najmniej jednego agenta");
  const proc = await api("/crew", { method: "POST", body: { task: fd.get("task"), agents, process: fd.get("process") } });
  toast("Zespół pracuje… wynik w Zadaniach"); showTab("tasks"); openTask(proc.pid);
}));

/* ------------------------------------------------------------ tasks (C2) */
const DAYS = { daily: "Codziennie", weekdays: "W dni robocze", weekends: "W weekendy" };
const STATUS = { running: ["info", "w toku"], queued: ["info", "w kolejce"], waiting: ["warn", "czeka na Ciebie"], completed: ["ok", "gotowe"], failed: ["warn", "błąd"] };
const isActive = (p) => ["running", "queued", "waiting"].includes(p.status);
const modelError = (msg) => /LLMError|HTTP \d{3}|quota|model|provider|API key|RESOURCE_EXHAUSTED|overloaded|credit|billing/i.test(String(msg || ""));
async function loadTasks() {
  try {
    const [{ processes }, { schedules }] = await Promise.all([api("/processes"), api("/schedules")]);
    state.processes = processes; state.schedules = schedules;
    renderTasks();
  } catch (err) { toast(err.message, true); }
  clearTimeout(state.timers.tasks);
  if (state.tab === "tasks") state.timers.tasks = setTimeout(loadTasks, state.processes.some(isActive) ? 2000 : 5000);
}
function taskTitle(p) {
  const s = state.schedules.find((x) => x.last_pid === p.pid);
  return s ? s.title : String(p.task || "").split("\n")[0].slice(0, 120);
}
function taskCard(p) {
  const [tone, label] = STATUS[p.status] || ["", p.status];
  const when = fmtTime((p.finished_at || p.started_at || p.created_at) * 1000);
  const kids = [el("div", { class: "task-top" }, el("strong", { text: taskTitle(p) }), el("span", { class: `pill-tag ${tone}`, text: label }))];
  if (isActive(p)) {
    const pct = p.max_steps ? Math.max(6, Math.round((p.step / p.max_steps) * 100)) : 6;
    kids.push(el("div", { class: "progress" }, el("div", { style: `width:${pct}%` })));
    kids.push(el("span", { class: "task-meta", text: `${p.agent} · ${p.status === "queued" ? "w kolejce" : `krok ${p.step || 1} z ~${p.max_steps || "?"}`} · ${fmtTime(p.created_at * 1000)}` }));
  } else if (p.status === "failed") {
    kids.push(el("span", { class: "task-out", text: explainError(p.error) || "Coś poszło nie tak." }));
    kids.push(el("div", { class: "task-actions" },
      modelError(p.error) ? el("button", { type: "button", class: "small-btn dark", text: "Wybierz inny model", onclick: (e) => { e.stopPropagation(); showTab("models"); } }) : null,
      el("button", { type: "button", class: "small-btn ghost-warn", text: "Szczegóły", onclick: (e) => { e.stopPropagation(); openTask(p.pid); } })));
  } else {
    const out = p.output || (p.result && p.result.output) || "";
    if (out) kids.push(el("span", { class: "task-out", text: out }));
    kids.push(el("span", { class: "task-meta", text: `${p.agent} · ${when}` }));
  }
  return el("article", { class: "task-card" + (p.status === "failed" ? " err" : ""), tabindex: "0", role: "button", onclick: () => openTask(p.pid),
    onkeydown: (e) => { if (e.key === "Enter") openTask(p.pid); } }, ...kids);
}
function scheduleCard(s) {
  return el("article", { class: "sched-card" },
    el("span", { class: "tile soft" }, icon("clock")),
    el("button", { type: "button", class: "sched-main", onclick: () => editSchedule(s) },
      el("strong", { text: s.title }), el("span", { text: `${DAYS[s.days] || s.days} ${s.time.replace(/^0/, "")} · ${s.agent}` })),
    el("input", { type: "checkbox", class: "big-check", checked: s.enabled, "aria-label": s.enabled ? "Włączone" : "Wyłączone", onchange: async (e) => {
      try { await api(`/schedules/${s.id}`, { method: "POST", body: { enabled: e.target.checked } }); toast(e.target.checked ? "Włączone" : "Wyłączone"); loadTasks(); }
      catch (err) { e.target.checked = !e.target.checked; toast(err.message, true); }
    } }));
}
function renderTasks() {
  const f = state.taskFilter;
  const running = state.processes.filter(isActive);
  $("#filter-running").textContent = running.length ? `W toku · ${running.length}` : "W toku";
  document.querySelectorAll(".filter").forEach((b) => { const on = b.dataset.filter === f; b.classList.toggle("on", on); b.setAttribute("aria-selected", String(on)); });
  const list = (f === "running" ? running : state.processes).slice().reverse().slice(0, 50);
  $("#task-list").classList.toggle("hidden", f === "scheduled");
  $("#task-list").replaceChildren(...(list.length ? list.map(taskCard)
    : [el("p", { class: "empty-note", text: f === "running" ? "Nic teraz nie pracuje." : "Brak zadań. Napisz coś w czacie albo zaplanuj zadanie." })]));
  const showSched = f !== "running";
  $("#schedule-title").classList.toggle("hidden", !showSched);
  $("#schedule-list").classList.toggle("hidden", !showSched);
  $("#schedule-list").replaceChildren(...(state.schedules.length ? state.schedules.map(scheduleCard)
    : [el("p", { class: "empty-note", text: "Brak zaplanowanych zadań. Dotknij „Zaplanuj”, żeby agent sam robił coś regularnie." })]));
}
document.querySelectorAll(".filter").forEach((b) => b.addEventListener("click", () => { state.taskFilter = b.dataset.filter; renderTasks(); }));
async function openTask(pid) {
  const body = el("div", { class: "stack" }, el("p", { class: "muted", text: "Wczytuję…" }));
  openSheet("Zadanie", body);
  state.sheetPid = pid;
  const show = (p) => {
    if (state.sheetPid !== pid) return;
    const r = p.result || {};
    const [tone, label] = STATUS[p.status] || ["", p.status];
    $("#sheet-title").textContent = taskTitle(p);
    body.replaceChildren(...[
      el("div", { class: "task-top" }, el("span", { class: "task-meta", text: `${p.agent} · ${fmtTime(p.created_at * 1000)}` }), el("span", { class: `pill-tag ${tone}`, text: label })),
      isActive(p) ? el("div", { class: "progress" }, el("div", { style: `width:${p.max_steps ? Math.max(6, Math.round((p.step / p.max_steps) * 100)) : 6}%` })) : null,
      isActive(p) ? el("p", { class: "muted small", text: p.status === "waiting" ? "Agent czeka na Twoją decyzję (u góry ekranu)." : `Krok ${p.step || 1} z ~${p.max_steps || "?"}…` }) : null,
      ...(p.error ? errorView(p.error) : []),
      p.status === "failed" && modelError(p.error) ? el("button", { class: "btn", type: "button", text: "Wybierz inny model", onclick: () => { closeSheet(); showTab("models"); } }) : null,
      r.output ? el("pre", { class: "out", text: r.output }) : null,
      el("details", {}, el("summary", { text: "Treść zadania" }), el("pre", { class: "out", text: p.task })),
      r.reflection ? el("details", {}, el("summary", { text: `🔁 Samoocena: ${Math.round(r.reflection.best_score * 100)}% (próby: ${r.reflection.attempts.length})` }), ...r.reflection.attempts.map((a, i) => el("pre", { class: "out", text: `Próba ${i + 1}: ${Math.round(a.score * 100)}%${a.critique ? "\n" + a.critique : ""}` }))) : null,
      r.strategy ? el("p", { class: "muted small", text: `🎯 Styl: ${STRATEGIES[r.strategy] || r.strategy}` }) : null,
      r.transcript ? el("details", {}, el("summary", { text: `Przebieg pracy zespołu (${r.transcript.length})` }), ...r.transcript.map((t) => el("pre", { class: "out", text: `${t.agent}: ${t.output || ""}` }))) : null,
      r.tool_calls && r.tool_calls.length ? el("details", {}, el("summary", { text: `Narzędzia (${r.tool_calls.length})` }), ...r.tool_calls.map((c) => el("pre", { class: "out", text: `${c.tool}(${JSON.stringify(c.arguments)}) → ${c.result}` }))) : null,
    ].filter(Boolean)); // replaceChildren() would print a skipped (null) section as the text "null"
  };
  try { show(await waitForProcess(pid, show)); } catch (err) { if (state.sheetPid === pid) body.replaceChildren(el("p", { class: "error", text: err.message })); }
}
/* Recurring tasks ("Zaplanowane") run on the server even when this app is closed. */
function editSchedule(s) {
  const f = $("#schedule-form"); const E = f.elements;
  f.reset();
  E.id.value = s ? s.id : ""; E.title.value = s ? s.title : ""; E.task.value = s ? s.task : "";
  E.time.value = s ? s.time : "07:30"; E.days.value = s ? s.days : "daily"; E.agent.value = s ? s.agent : currentAgent();
  $("#schedule-form-title").textContent = s ? "Zaplanowane zadanie" : "Nowe zaplanowane zadanie";
  $("#schedule-run").classList.toggle("hidden", !s); $("#schedule-delete").classList.toggle("hidden", !s);
  f.classList.remove("hidden");
  setTimeout(() => { f.scrollIntoView({ behavior: "smooth", block: "start" }); E.title.focus(); }, 30);
}
$("#schedule-new").addEventListener("click", () => editSchedule(null));
$("#schedule-cancel").addEventListener("click", () => $("#schedule-form").classList.add("hidden"));
$("#schedule-form").addEventListener("submit", withBusy($("#schedule-form"), async (fd) => {
  const body = { title: fd.get("title"), task: fd.get("task"), time: fd.get("time"), days: fd.get("days"), agent: fd.get("agent"),
    tz: (Intl.DateTimeFormat().resolvedOptions().timeZone || "") };
  const id = fd.get("id");
  await api(id ? `/schedules/${id}` : "/schedules", { method: "POST", body });
  toast(id ? "Zapisano ✅" : `Zaplanowano: ${DAYS[body.days].toLowerCase()} ${body.time} ✅`);
  $("#schedule-form").classList.add("hidden"); loadTasks();
}));
$("#schedule-run").addEventListener("click", async () => {
  const id = $("#schedule-form").elements.id.value;
  try { const p = await api(`/schedules/${id}/run`, { method: "POST", body: {} }); toast("Uruchomiono"); $("#schedule-form").classList.add("hidden"); await loadTasks(); openTask(p.pid); }
  catch (err) { toast(err.message, true); }
});
$("#schedule-delete").addEventListener("click", async () => {
  const id = $("#schedule-form").elements.id.value;
  if (!confirm("Usunąć to zaplanowane zadanie?")) return;
  try { await api(`/schedules/${id}`, { method: "DELETE" }); toast("Usunięto"); $("#schedule-form").classList.add("hidden"); loadTasks(); }
  catch (err) { toast(err.message, true); }
});

/* ------------------------------------------------------------------ brain */
const KIND = { document: ["#f5b84b", "Dokument"], chunk: ["#6ea8ff", "Fragment wiedzy"], fact: ["#3ecf8e", "Fakt"], episode: ["#8b7bff", "Epizod (przebieg zadania)"], lesson: ["#ff6b7a", "Lekcja"] };
$("#brain-legend").replaceChildren(...Object.values(KIND).map(([c, l]) => el("span", {}, el("i", { style: `background:${c}` }), l)));
const brain = { nodes: [], edges: [], raf: 0, sel: null };
async function loadBrain() {
  try {
    const g = await api("/graph");
    const canvas = $("#brain"); const w = canvas.clientWidth || 600; const h = canvas.clientHeight || 400;
    const idx = new Map();
    brain.nodes = g.nodes.map((n, i) => { const node = { ...n, x: w / 2 + Math.cos(i) * (40 + i * 3), y: h / 2 + Math.sin(i) * (40 + i * 3), vx: 0, vy: 0 }; idx.set(n.id, node); return node; });
    brain.edges = g.edges.map((e) => ({ ...e, a: idx.get(e.source), b: idx.get(e.target) })).filter((e) => e.a && e.b);
    $("#brain-detail").classList.add("hidden");
    if (!brain.nodes.length) { drawEmptyBrain(); return; }
    cancelAnimationFrame(brain.raf); simulate(0);
  } catch (err) { toast(err.message, true); }
}
function sizeCanvas(canvas) {
  const dpr = window.devicePixelRatio || 1; const w = canvas.clientWidth; const h = canvas.clientHeight;
  if (canvas.width !== Math.round(w * dpr)) { canvas.width = Math.round(w * dpr); canvas.height = Math.round(h * dpr); }
  const ctx = canvas.getContext("2d"); ctx.setTransform(dpr, 0, 0, dpr, 0, 0); return { ctx, w, h };
}
function drawEmptyBrain() {
  const { ctx, w, h } = sizeCanvas($("#brain")); ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = getComputedStyle(document.body).getPropertyValue("--muted"); ctx.textAlign = "center"; ctx.font = "14px system-ui";
  ctx.fillText("Mózg jest pusty: dodaj wiedzę albo porozmawiaj z agentem.", w / 2, h / 2);
}
function simulate(iter) {
  const canvas = $("#brain"); const { ctx, w, h } = sizeCanvas(canvas); const N = brain.nodes;
  if (iter < 300) {
    for (let i = 0; i < N.length; i++) for (let j = i + 1; j < N.length; j++) {
      const a = N[i], b = N[j]; let dx = a.x - b.x, dy = a.y - b.y; const d2 = dx * dx + dy * dy + 0.01; const f = 900 / d2;
      const d = Math.sqrt(d2); dx /= d; dy /= d; a.vx += dx * f; a.vy += dy * f; b.vx -= dx * f; b.vy -= dy * f;
    }
    for (const e of brain.edges) {
      const dx = e.b.x - e.a.x, dy = e.b.y - e.a.y; const d = Math.sqrt(dx * dx + dy * dy) + 0.01;
      const target = e.kind === "part" ? 40 : 90; const f = (d - target) * 0.02 * (e.weight || 0.5);
      e.a.vx += (dx / d) * f; e.a.vy += (dy / d) * f; e.b.vx -= (dx / d) * f; e.b.vy -= (dy / d) * f;
    }
    for (const n of N) {
      n.vx += (w / 2 - n.x) * 0.004; n.vy += (h / 2 - n.y) * 0.004;
      n.vx *= 0.82; n.vy *= 0.82; n.x = Math.max(12, Math.min(w - 12, n.x + n.vx)); n.y = Math.max(12, Math.min(h - 12, n.y + n.vy));
    }
  }
  ctx.clearRect(0, 0, w, h);
  ctx.lineWidth = 1;
  for (const e of brain.edges) {
    ctx.strokeStyle = e.kind === "part" ? "rgba(245,184,75,.35)" : `rgba(110,168,255,${0.15 + (e.weight || 0) * 0.5})`;
    ctx.beginPath(); ctx.moveTo(e.a.x, e.a.y); ctx.lineTo(e.b.x, e.b.y); ctx.stroke();
  }
  for (const n of N) {
    const [color] = KIND[n.kind] || ["#9aa5c4"]; const r = n.kind === "document" ? 9 : 6;
    ctx.fillStyle = color; ctx.beginPath(); ctx.arc(n.x, n.y, r, 0, Math.PI * 2); ctx.fill();
    if (brain.sel === n) { ctx.strokeStyle = getComputedStyle(document.body).getPropertyValue("--text"); ctx.lineWidth = 2; ctx.stroke(); ctx.lineWidth = 1; }
    if (n.kind === "document") { ctx.fillStyle = getComputedStyle(document.body).getPropertyValue("--text"); ctx.font = "12px system-ui"; ctx.textAlign = "center"; ctx.fillText(n.label, n.x, n.y - 13); }
  }
  if (iter < 300 && state.tab === "brain") brain.raf = requestAnimationFrame(() => simulate(iter + 1));
}
$("#brain").addEventListener("pointerdown", (e) => {
  const rect = e.target.getBoundingClientRect(); const x = e.clientX - rect.left; const y = e.clientY - rect.top;
  let best = null, bestD = 22 * 22;
  for (const n of brain.nodes) { const d = (n.x - x) ** 2 + (n.y - y) ** 2; if (d < bestD) { best = n; bestD = d; } }
  brain.sel = best; simulate(300);
  const box = $("#brain-detail");
  if (!best) { box.classList.add("hidden"); return; }
  box.classList.remove("hidden");
  box.replaceChildren(el("div", { class: "item-head" }, el("strong", { text: best.label }), el("span", { class: "tag", text: (KIND[best.kind] || [0, best.kind])[1] })), best.text ? el("p", { class: "small", text: best.text }) : null);
});
$("#brain-refresh").addEventListener("click", loadBrain);

/* -------------------------------------------------------- knowledge (C5) */
const MAX_FILE = 60 * 1024 * 1024;
function uploadKnowledge(file) {
  if (file.size > MAX_FILE) return Promise.reject(new Error(`${file.name}: plik jest za duży (max 60 MB)`));
  return upload(`/knowledge/upload?filename=${encodeURIComponent(file.name)}`, file);
}
async function loadKnowledge() {
  try { const { documents } = await api("/knowledge"); state.docs = documents; renderDocs(); } catch (err) { toast(err.message, true); }
}
function renderDocs() {
  const q = $("#kb-search").value.trim().toLowerCase();
  const docs = state.docs.slice().sort((a, b) => (b.added_at || 0) - (a.added_at || 0));
  const shown = q ? docs.filter((d) => String(d.source).toLowerCase().includes(q) || String(d.preview).toLowerCase().includes(q)) : docs;
  const chunks = docs.reduce((n, d) => n + d.chunks, 0);
  $("#kb-count").textContent = `${countOf(docs.length, "plik", "pliki", "plików")} · ${countOf(chunks, "fragment", "fragmenty", "fragmentów")}`;
  const list = $("#kb-list");
  if (!shown.length) { list.replaceChildren(el("p", { class: "empty-note", style: "padding:14px 16px", text: q ? "Żaden dokument nie pasuje." : "Brak dokumentów. Dodaj pierwszy plik powyżej." })); return; }
  list.replaceChildren(...shown.flatMap((d) => {
    const type = (d.type || (/\.(\w+)$/.exec(d.source) || [0, "txt"])[1]).toLowerCase();
    const menu = el("div", { class: "doc-menu hidden" },
      el("button", { type: "button", class: "small-btn", text: "Podgląd", onclick: () => preview.classList.toggle("hidden") }),
      el("button", { type: "button", class: "small-btn", text: "Zapytaj agenta", onclick: () => { showTab("convo"); sendMessage(`Streść dokument „${d.source}” z mojej bazy wiedzy.`); } }),
      el("button", { type: "button", class: "small-btn", style: "color:var(--err);border-color:var(--danger-border)", text: "Usuń", onclick: async () => {
        if (!confirm(`Usunąć „${d.source}” z wiedzy agentów?`)) return;
        try { await api(`/knowledge/${encodeURIComponent(d.id)}`, { method: "DELETE" }); toast("Usunięto"); loadKnowledge(); } catch (err) { toast(err.message, true); }
      } }));
    const preview = el("div", { class: "doc-preview hidden", text: d.preview + (d.preview.length >= 160 ? "…" : "") });
    return [el("div", { class: "doc-row" },
      el("span", { class: `doc-badge ${type}`, text: type.toUpperCase().slice(0, 4) }),
      el("span", { class: "doc-text" }, el("strong", { text: d.source }),
        el("span", { text: `${countOf(d.chunks, "fragment", "fragmenty", "fragmentów")}${d.added_at ? " · " + relDay(d.added_at * 1000) : ""}` })),
      el("button", { type: "button", class: "more-btn", "aria-label": "Więcej opcji", text: "⋮", onclick: () => { menu.classList.toggle("hidden"); if (menu.classList.contains("hidden")) preview.classList.add("hidden"); } })),
    menu, preview];
  }));
}
let searchTimer = 0;
$("#kb-search").addEventListener("input", () => {
  renderDocs();
  clearTimeout(searchTimer);
  const q = $("#kb-search").value.trim();
  const box = $("#kb-results");
  if (q.length < 2) { box.classList.add("hidden"); return; }
  searchTimer = setTimeout(async () => {
    try {
      const { results } = await api(`/knowledge/search?q=${encodeURIComponent(q)}`);
      if ($("#kb-search").value.trim() !== q) return;
      box.classList.remove("hidden");
      box.replaceChildren(el("h2", { class: "section-label", text: results.length ? "Najlepiej pasujące fragmenty" : "Nic nie znaleziono w treści dokumentów" }),
        ...results.slice(0, 5).map((r) => el("div", { class: "kb-hit" }, el("b", { text: r.source }), r.text.length >= 400 ? r.text + "…" : r.text)));
    } catch (err) { toast(err.message, true); }
  }, 350);
});
async function uploadFiles(files) {
  const list = Array.from(files); if (!list.length) return;
  const progress = $("#kb-progress"); progress.classList.remove("hidden");
  let ok = 0;
  for (const [i, file] of list.entries()) {
    progress.textContent = `Wgrywam ${i + 1}/${list.length}: ${file.name}…`;
    try { await uploadKnowledge(file); ok++; } catch (err) { toast(err.message, true); }
  }
  progress.classList.add("hidden");
  if (ok) toast(`Dodano ${countOf(ok, "plik", "pliki", "plików")} do wiedzy ✅`);
  loadKnowledge();
}
$("#kb-drop").addEventListener("click", () => $("#kb-files").click());
$("#kb-files").addEventListener("change", (e) => { uploadFiles(e.target.files); e.target.value = ""; });
["dragenter", "dragover"].forEach((t) => $("#kb-drop").addEventListener(t, (e) => { e.preventDefault(); $("#kb-drop").classList.add("drag"); }));
["dragleave", "drop"].forEach((t) => $("#kb-drop").addEventListener(t, () => $("#kb-drop").classList.remove("drag")));
$("#kb-drop").addEventListener("drop", (e) => { e.preventDefault(); uploadFiles(e.dataTransfer.files); });
$("#kb-import").addEventListener("click", () => { showTab("brain"); openDetails("mem-import-card"); });
$("#kb-form").addEventListener("submit", withBusy($("#kb-form"), async (fd) => {
  const r = await api("/knowledge", { method: "POST", body: { text: fd.get("text"), metadata: { source: fd.get("source") || "notatka", type: "txt" } } });
  toast(`Dodano ✅ (${countOf(r.chunks, "fragment", "fragmenty", "fragmentów")})`); $("#kb-form").reset(); loadKnowledge();
}));

/* ----------------------------------------------------------- models (C4) */
const POPULAR = ["gemini", "anthropic", "openrouter", "openai"];
async function loadModels() {
  let data;
  try { data = await refreshProviders(); } catch (err) { toast(err.message, true); return; }
  const def = data.default;
  const main = data.providers.find((p) => p.id === def.provider);
  const cards = [];
  if (main) cards.push(mainProviderCard(main, def));
  else if (def.provider === "env" && def.model) {
    cards.push(el("section", { class: "prov-main" }, el("div", { class: "prov-top" }, el("span", { class: "tile soft" }, icon("spark")),
      el("div", { class: "prov-name" }, el("strong", { text: def.model }), el("span", { text: "Z ustawień serwera · domyślny" })))));
  } else {
    cards.push(el("section", { class: "prov-main" }, el("div", { class: "prov-top" }, el("span", { class: "tile amber" }, icon("spark")),
      el("div", { class: "prov-name" }, el("strong", { text: "Brak modelu AI" }), el("span", { text: "Agenci nie rozumieją pytań, dopóki nie dodasz klucza." }))),
    el("div", { class: "two-btns" }, el("button", { type: "button", class: "yes", style: "grid-column:1/-1", text: "Dodaj klucz Gemini (darmowy)",
      onclick: () => fillProviderForm(data.presets.find((x) => x.id === "gemini") || data.presets[0], true) }))));
  }
  for (const p of data.providers) if (p !== main) cards.push(providerRow(p));
  for (const id of POPULAR) {
    const preset = data.presets.find((x) => x.id === id);
    if (preset && !data.providers.some((p) => p.id === id)) cards.push(presetRow(preset));
  }
  $("#provider-cards").replaceChildren(...cards);
  const sel = $("#provider-preset");
  if (!sel.options.length) sel.replaceChildren(...data.presets.map((p, i) => el("option", { value: String(i), text: p.label })));
}
const keyTail = (p) => p.has_key ? `Klucz ••••${/[•]/.test(p.api_key.slice(-4)) ? "" : p.api_key.slice(-4)}` : "Brak klucza";
function mainProviderCard(p, def) {
  const usage = p.usage || {}; const today = usage.today || 0; const limit = p.daily_limit || 0;
  const test = usage.last_test;
  const current = def.model || p.default_model;
  const set = el("fieldset", { class: "model-set" }, el("legend", { text: `Wybierz model (lista od ${p.kind === "gemini" ? "Google" : providerName(p)})` }));
  const optionsBox = el("div", { class: "stack", style: "gap:8px" });
  set.append(optionsBox);
  const renderModels = (models, all = false) => {
    const list = models.includes(current) || !current ? models.slice() : [current, ...models];
    list.sort((a, b) => (b === current) - (a === current));
    const shown = all ? list : list.slice(0, 5);
    optionsBox.replaceChildren(...shown.map((m) => el("label", { class: "model-opt" },
      el("input", { type: "radio", name: `model-${p.id}`, value: m, checked: m === current }),
      el("span", {}, m, /-latest$/.test(m) ? el("small", { text: "Zawsze najnowsza wersja" }) : null))));
    if (!all && list.length > shown.length) optionsBox.append(el("button", { type: "button", class: "model-more", text: `Pokaż wszystkie (${list.length})`, onclick: () => renderModels(models, true) }));
  };
  renderModels(current ? [current] : []);
  if (p.has_key || p.kind === "openai_compat") {
    const cached = state.modelCache[p.id];
    if (cached) renderModels(cached);
    else {
      optionsBox.append(el("span", { class: "muted small", text: "Wczytuję listę modeli…" }));
      api(`/providers/${p.id}/models`).then(({ models }) => { state.modelCache[p.id] = models; renderModels(models); })
        .catch((err) => { renderModels(current ? [current] : []); optionsBox.append(el("span", { class: "muted small", text: "Nie udało się pobrać listy: " + err.message })); });
    }
  }
  return el("section", { class: "prov-main" },
    el("div", { class: "prov-top" }, el("span", { class: "tile soft" }, icon("spark")),
      el("div", { class: "prov-name" }, el("strong", { text: p.label || p.id }), el("span", { text: `${keyTail(p)} · domyślny` })),
      test ? el("span", { class: `pill-tag ${test.ok ? "ok" : "warn"}`, text: test.ok ? "działa" : "nie działa" }) : null),
    el("div", { class: "usage" },
      el("div", { class: "usage-line" }, el("span", { text: limit ? "Darmowy plan · dzisiaj" : "Dzisiaj" }),
        el("span", { text: limit ? `${today} / ${limit} zapytań` : countOf(today, "zapytanie", "zapytania", "zapytań") })),
      limit ? el("div", { class: "progress" }, el("div", { style: `width:${Math.min(100, Math.round((today / limit) * 100))}%` })) : null),
    set,
    el("div", { class: "two-btns" },
      el("button", { type: "button", text: "Testuj", onclick: async (ev) => {
        const b = ev.currentTarget; b.disabled = true; b.textContent = "Testuję…";
        const model = set.querySelector("input:checked")?.value;
        try { const r = await api(`/providers/${p.id}/test`, { method: "POST", body: { model } }); toast(`✅ Działa (${r.model || model})`); }
        catch (err) { toast("❌ " + err.message, true); }
        finally { loadModels(); }
      } }),
      el("button", { type: "button", class: "yes", text: "Zapisz", onclick: async (ev) => {
        const model = set.querySelector("input:checked")?.value || "";
        ev.currentTarget.disabled = true;
        try {
          await api("/providers", { method: "POST", body: { id: p.id, kind: p.kind, base_url: p.base_url, label: p.label, default_model: model, make_default: true } });
          toast(`Model: ${model || "domyślny"} ✅`); loadModels();
        } catch (err) { toast(err.message, true); ev.currentTarget.disabled = false; }
      } })),
    el("div", { class: "prov-links" },
      el("button", { type: "button", text: "Edytuj klucz i limit", onclick: () => fillProviderForm(p) }),
      el("button", { type: "button", class: "danger", text: "Usuń", onclick: () => removeProvider(p) })));
}
function providerRow(p) {
  return el("article", { class: "prov-row" }, el("span", { class: "tile gray" }, icon("wave")),
    el("span", { class: "prov-name", role: "button", tabindex: "0", style: "cursor:pointer", onclick: () => fillProviderForm(p) },
      el("strong", { text: p.label || p.id }), el("span", { text: `${keyTail(p)}${p.default_model ? " · " + p.default_model : ""}` })),
    p.has_key || p.kind === "openai_compat"
      ? el("button", { type: "button", class: "small-btn", text: "Ustaw domyślny", onclick: async () => {
        try { await api("/settings/default", { method: "POST", body: { provider: p.id, model: p.default_model || undefined } }); toast("Ustawiono ✅"); loadModels(); } catch (err) { toast(err.message, true); }
      } })
      : el("button", { type: "button", class: "small-btn", text: "Dodaj klucz", onclick: () => fillProviderForm(p) }));
}
function presetRow(preset) {
  return el("article", { class: "prov-row" }, el("span", { class: "tile gray" }, icon("wave")),
    el("span", { class: "prov-name" }, el("strong", { text: preset.label }), el("span", { text: "Brak klucza" })),
    el("button", { type: "button", class: "small-btn", text: "Dodaj klucz", onclick: () => fillProviderForm(preset, true) }));
}
async function removeProvider(p) {
  if (!confirm(`Usunąć dostawcę ${p.label || p.id}? Klucz zostanie skasowany z serwera.`)) return;
  try { await api(`/providers/${p.id}`, { method: "DELETE" }); toast("Usunięto"); loadModels(); } catch (err) { toast(err.message, true); }
}
function fillProviderForm(p, isPreset = false) {
  const f = $("#provider-form"); const E = f.elements;
  const sel = $("#provider-preset");
  if (!sel.options.length) sel.replaceChildren(...state.presets.map((x, i) => el("option", { value: String(i), text: x.label })));
  const idx = state.presets.findIndex((x) => x.id === p.id);
  if (idx >= 0) sel.value = String(idx);
  E.id.value = p.id; E.kind.value = p.kind; E.base_url.value = p.base_url || ""; E.default_model.value = p.default_model || "";
  E.daily_limit.value = !isPreset && p.daily_limit ? p.daily_limit : "";
  E.api_key.value = ""; E.api_key.placeholder = !isPreset && p.has_key ? "zostaw puste, żeby nie zmieniać" : "wklej klucz API";
  E.make_default.checked = isPreset && !state.providers.length;
  openDetails("provider-form-card");
}
$("#provider-add").addEventListener("click", () => fillProviderForm(state.presets[0] || { id: "", kind: "openai_compat" }, true));
$("#provider-preset").addEventListener("change", (e) => fillProviderForm(state.presets[Number(e.target.value)], true));
$("#provider-form").addEventListener("submit", withBusy($("#provider-form"), async (fd) => {
  const body = Object.fromEntries(fd); body.make_default = fd.get("make_default") === "on";
  const preset = state.presets[Number($("#provider-preset").value)];
  const existing = state.providers.find((p) => p.id === body.id);
  body.label = existing ? existing.label : preset && preset.id === body.id ? preset.label : body.id;
  await api("/providers", { method: "POST", body }); toast("Zapisano ✅");
  $("#provider-form").elements.api_key.value = ""; $("#provider-form-card").open = false; delete state.modelCache[body.id]; loadModels();
}));

/* ------------------------------------------------------------- "Ty" (C6) */
function serverLabel() {
  const host = location.hostname;
  if (/\.app\.github\.dev$/.test(host) || /\.github\.dev$/.test(host)) return "Codespaces";
  if (/^(localhost|127\.|\[::1\])/.test(host)) return "ten komputer";
  return host;
}
function loadMe() {
  $("#me-server").textContent = `Połączono z serwerem · ${serverLabel()}`;
  const a = agentInfo();
  const native = a.kind !== "external";
  $("#me-permission-value").textContent = native ? PERM_SHORT[a.permission] || "Autonomiczny" : "zewnętrzny";
  $("#me-mode-value").textContent = native ? MODE_SHORT[a.mode] || "Standardowy" : "—";
  $("#me-agents-value").textContent = String(state.agents.length || "");
  const supported = "Notification" in window;
  const toggle = $("#notify-toggle"); const note = $("#notify-note");
  toggle.disabled = !supported;
  toggle.checked = notificationsOn();
  note.classList.toggle("hidden", supported && Notification.permission !== "denied");
  note.textContent = !supported ? (isApp() ? "Niedostępne w aplikacji – otwórz War Room w Chrome" : "Ta przeglądarka nie obsługuje powiadomień")
    : "Zablokowane w ustawieniach przeglądarki";
  $("#notify-desc").classList.toggle("hidden", !note.classList.contains("hidden"));
  refreshAgents().then(() => { if (state.tab === "me") { const b = agentInfo(); $("#me-permission-value").textContent = b.kind !== "external" ? PERM_SHORT[b.permission] || "Autonomiczny" : "zewnętrzny"; $("#me-mode-value").textContent = b.kind !== "external" ? MODE_SHORT[b.mode] || "Standardowy" : "—"; $("#me-agents-value").textContent = String(state.agents.length); } }).catch(() => {});
}
$("#me-permission").addEventListener("click", () => {
  const a = agentInfo();
  if (a.kind === "external") { toast("Agent zewnętrzny ma własne uprawnienia.", true); return; }
  choiceSheet(`Uprawnienia: ${a.name}`, PERMISSION_CHOICES, a.permission, (v) => changeAgent(a.name, { permission: v }));
});
$("#me-mode").addEventListener("click", () => {
  const a = agentInfo();
  if (a.kind === "external") { toast("Agent zewnętrzny ma własny tryb pracy.", true); return; }
  choiceSheet(`Tryb myślenia: ${a.name}`, MODE_CHOICES, a.mode || "standard", (v) => changeAgent(a.name, { mode: v }));
});
$("#notify-toggle").addEventListener("change", async (e) => {
  if (!e.target.checked) { store.del("aos_notify"); toast("Powiadomienia wyłączone"); return; }
  const perm = Notification.permission === "granted" ? "granted" : await Notification.requestPermission();
  if (perm !== "granted") { e.target.checked = false; loadMe(); toast("Przeglądarka nie zezwoliła na powiadomienia.", true); return; }
  store.set("aos_notify", "1"); toast("Powiadomię Cię, gdy agent będzie czekał na zgodę.");
});
$("#me-connect").addEventListener("click", () => {
  const link = `${location.origin}/#connect=${encodeURIComponent(token)}`;
  const box = el("div", { class: "qr-box" });
  try { box.innerHTML = QR.svg(link); } catch (err) { box.textContent = err.message; }
  openSheet("Połącz telefon", box,
    el("p", { class: "small", text: "Zeskanuj ten kod aparatem telefonu albo przyciskiem „Skanuj kod QR z komputera” na ekranie logowania. Telefon zaloguje się bez wpisywania hasła." }),
    el("p", { class: "small muted", text: "Kod zawiera hasło do War Room: nie pokazuj go innym osobom." }),
    el("button", { class: "btn", type: "button", text: "Kopiuj link", onclick: async () => {
      try { await navigator.clipboard.writeText(link); toast("Skopiowano"); } catch { toast("Nie udało się skopiować", true); }
    } }));
});
$("#logout-btn").addEventListener("click", () => {
  if (!confirm("Wylogować z War Room na tym urządzeniu?")) return;
  token = ""; store.del("aos_token"); showLogin();
});

/* ---------------------------------------------------------------- monitor */
async function loadMonitor() {
  try {
    const [s, m] = await Promise.all([api("/status"), api("/metrics")]);
    const c = m.counters || {};
    const stats = [["Agenci", s.agents.length], ["Zadania gotowe", (s.processes || {}).completed || 0], ["Błędy", (s.processes || {}).failed || 0],
      ["Wywołania narzędzi", c["tool.calls"] || 0], ["Tokeny wejściowe", c["llm.input_tokens"] || 0], ["Tokeny wyjściowe", c["llm.output_tokens"] || 0],
      ["Fragmenty wiedzy", s.knowledge_chunks], ["Wspomnienia", s.memories], ["Oceny", s.feedback]];
    $("#monitor-stats").replaceChildren(...stats.map(([l, v]) => el("div", { class: "stat" }, el("b", { text: String(v) }), el("span", { text: l }))));
    const rows = Object.entries(m.timings || {});
    $("#monitor-timings").replaceChildren(el("h3", { text: "Czasy odpowiedzi" }), rows.length ? el("div", { class: "table-wrap" }, el("table", {},
      el("thead", {}, el("tr", {}, ...["Operacja", "Liczba", "p50 ms", "p95 ms", "max ms"].map((t) => el("th", { text: t })))),
      el("tbody", {}, ...rows.map(([k, v]) => el("tr", {}, ...[k, v.count, v.p50_ms, v.p95_ms, v.max_ms].map((t) => el("td", { text: String(t) }))))))) : el("p", { class: "muted", text: "Brak pomiarów." }));
  } catch (err) { toast(err.message, true); }
}
$("#monitor-refresh").addEventListener("click", loadMonitor);

/* ------------------------------------------------------------ install/PWA */
let deferredInstall = null;
window.addEventListener("beforeinstallprompt", (e) => { e.preventDefault(); deferredInstall = e; $("#install-btn").classList.remove("hidden"); });
$("#install-btn").addEventListener("click", async () => { if (!deferredInstall) return; deferredInstall.prompt(); await deferredInstall.userChoice; deferredInstall = null; $("#install-btn").classList.add("hidden"); });
if ("serviceWorker" in navigator) window.addEventListener("load", () => navigator.serviceWorker.register("/sw.js").catch(() => {}));

/* ------------------------------------------------------------ extensions */
async function loadExt() {
  try {
    const [{ skills }, { mods }, { servers }] = await Promise.all([api("/skills"), api("/mods"), api("/mcp")]);
    $("#skill-list").replaceChildren(...(skills.length ? skills.map((s) => el("div", { class: "item" },
      el("div", { class: "item-head" }, el("span", { class: "item-title", text: "🎓 " + s.name }), s.tools.length ? el("span", { class: "tag", text: s.tools.join(", ") }) : null),
      el("p", { class: "muted small", text: s.description }),
      el("div", { class: "actions" }, delBtn(`/skills/${s.name}`, `skill ${s.name}`, loadExt)))) : [el("p", { class: "muted small", text: "Brak skilli." })]));
    $("#mod-list").replaceChildren(...(mods.length ? mods.map((m) => el("div", { class: "item" },
      el("div", { class: "item-head" }, el("span", { class: "item-title", text: "🛠 " + m.name }), el("span", { class: "tag", text: `${m.method} · ${m.tool}` })),
      el("p", { class: "muted small", text: `${m.description} · ${m.url}` }),
      el("div", { class: "actions" }, delBtn(`/mods/${m.name}`, `mod ${m.name}`, loadExt)))) : [el("p", { class: "muted small", text: "Brak modów." })]));
    $("#mcp-list").replaceChildren(...(servers.length ? servers.map((s) => el("div", { class: "item" },
      el("div", { class: "item-head" }, el("span", { class: "item-title", text: "🔗 " + s.name }), el("span", { class: "tag " + (s.connected ? "ok" : "err"), text: s.connected ? `połączony · ${s.tools.length} narz.` : "rozłączony" })),
      el("p", { class: "muted small", text: s.error ? "Błąd: " + s.error : (s.tools.join(", ") || (s.url || s.command)) }),
      el("div", { class: "actions" },
        el("button", { class: "btn small", type: "button", text: "Połącz ponownie", onclick: async (ev) => {
          ev.target.disabled = true;
          try { await api(`/mcp/${s.name}/reconnect`, { method: "POST", body: {} }); toast("Połączono ✅"); } catch (err) { toast(err.message, true); } finally { loadExt(); }
        } }),
        delBtn(`/mcp/${s.name}`, `serwer ${s.name}`, loadExt)))) : [el("p", { class: "muted small", text: "Brak serwerów MCP." })]));
  } catch (err) { toast(err.message, true); }
}
function delBtn(path, label, after) {
  return el("button", { class: "btn small ghost danger", type: "button", text: "Usuń", onclick: async () => {
    if (!confirm(`Usunąć ${label}?`)) return;
    try { await api(path, { method: "DELETE" }); toast("Usunięto"); after(); } catch (err) { toast(err.message, true); }
  } });
}
$("#skill-form").addEventListener("submit", withBusy($("#skill-form"), async (fd) => {
  const md = (fd.get("markdown") || "").trim();
  const body = md ? { markdown: md, name: fd.get("name") || undefined } : { name: fd.get("name"), description: fd.get("description"), instructions: fd.get("instructions"), tools: fd.get("tools") };
  await api("/skills", { method: "POST", body }); toast("Skill zapisany ✅"); $("#skill-form").reset(); loadExt();
}));
$("#mod-form").addEventListener("submit", withBusy($("#mod-form"), async (fd) => {
  const params = String(fd.get("params") || "").split("\n").map((l) => l.trim()).filter(Boolean).map((l) => {
    const [name, type = "string", ...desc] = l.split(":"); return { name: name.trim(), type: type.trim() || "string", description: desc.join(":").trim() };
  });
  const headers = fd.get("header_name") ? { [fd.get("header_name")]: fd.get("header_value") || "" } : {};
  await api("/mods", { method: "POST", body: { name: fd.get("name"), method: fd.get("method"), description: fd.get("description"), url: fd.get("url"), params, headers } });
  toast("Mod zapisany ✅"); $("#mod-form").reset(); loadExt();
}));
$("#mcp-form").addEventListener("submit", withBusy($("#mcp-form"), async (fd) => {
  const body = Object.fromEntries(fd); if (!body.token) delete body.token;
  toast("Łączę z serwerem MCP…");
  const s = await api("/mcp", { method: "POST", body }); toast(`Połączono ✅ (${s.tools.length} narzędzi)`); $("#mcp-form").reset(); loadExt();
}));

/* --------------------------------------------------------- memory import */
$("#mem-import").addEventListener("click", async (ev) => {
  const file = $("#mem-file").files[0]; const text = $("#mem-text").value.trim(); const distill = $("#mem-distill").checked;
  if (!file && !text) { toast("Wybierz plik albo wklej wspomnienia", true); return; }
  if (file && file.size > MAX_FILE) { toast("Plik jest za duży (max 60 MB)", true); return; }
  ev.target.disabled = true; $("#mem-result").textContent = "Importuję…" + (distill ? " (model analizuje rozmowy, to może potrwać)" : "");
  try {
    const r = file ? await upload(`/memory/import?filename=${encodeURIComponent(file.name)}&distill=${distill ? 1 : 0}`, file)
      : await api("/memory/import", { method: "POST", body: { text, distill } });
    $("#mem-result").textContent = `✅ Źródło: ${r.source}. Rozmowy: ${r.conversations_found}, dodane epizody: ${r.episodes_added}, fakty: ${r.facts_added}` + (r.distilled_facts ? `, wyciągnięte fakty: ${r.distilled_facts}` : "") + `. Wspomnień razem: ${r.memories_total}.`;
    $("#mem-file").value = ""; $("#mem-text").value = ""; loadBrain();
  } catch (err) { $("#mem-result").textContent = "❌ " + err.message; } finally { ev.target.disabled = false; }
});
$("#mem-file").addEventListener("change", (e) => { const f = e.target.files[0]; $("#mem-result").textContent = f ? `Wybrano: ${f.name} (${(f.size / 1024 / 1024).toFixed(1)} MB)` : ""; });

/* ------------------------------------------------------------------ start */
async function start() {
  $("#login").classList.add("hidden"); $("#app").classList.remove("hidden");
  try { await Promise.all([refreshAgents(), refreshProviders()]); } catch (err) { toast(err.message, true); }
  showTab(store.get("aos_tab", "chat"));
  pollApprovals();
}
applyTheme(currentTheme());
applyAccent(currentAccent());
(async () => {
  try { await api("/auth/check"); start(); } catch { showLogin(); }
})();
