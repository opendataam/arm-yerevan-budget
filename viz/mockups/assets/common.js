/* Shared helpers for the Yerevan budget mockups. Data: window.BUDGET (data.js), amounts in million AMD.

   Languages: every language of the database (data.js "languages"). The interface strings are in
   assets/i18n/<lang>/common.js (shared) and assets/i18n/<lang>/<page>.js; English is the fallback.
   A page runs its code in YB.ready("<page>", fn): the strings of the chosen language are loaded first, the
   names of data.js are localised in place (B.class_names, B.district_names, B.hierarchy, ... become plain
   strings of that language) and the elements marked data-i18n / data-i18n-html / data-i18n-attr are
   translated. Arabic and Persian switch the page to right-to-left; charts stay left-to-right. */
(function () {
  "use strict";
  const B = window.BUDGET;

  /* languages, in the order of the switcher; names in the language itself */
  const LANGS = [
    ["hy", "Հայերեն"], ["en", "English"], ["ru", "Русский"], ["fr", "Français"], ["es", "Español"],
    ["pt", "Português"], ["de", "Deutsch"], ["ar", "العربية"], ["fa", "فارسی"],
  ].filter(([c]) => !B.languages || B.languages.includes(c));
  const CODES = LANGS.map((l) => l[0]);
  const RTL = new Set(["ar", "fa"]);
  // number formatting: the conventions of the language, but always the digits 0–9 (as in the data)
  // (browsers without Armenian locale data fall back to ru-RU: the same separators, 1 086 677,5)
  const LOCALE = { hy: ["hy-AM", "ru-RU"], en: "en-GB", ru: "ru-RU", fr: "fr-FR", es: "es-ES", pt: "pt-BR", de: "de-DE",
    ar: "ar-u-nu-latn", fa: "fa-u-nu-latn" };
  const STORE = "yb-lang";

  function pickLang() {
    const q = new URLSearchParams(location.search).get("lang");
    if (CODES.includes(q)) return q;
    try { const s = localStorage.getItem(STORE); if (CODES.includes(s)) return s; } catch (e) { /* storage off */ }
    for (const l of navigator.languages || [navigator.language || ""]) {
      const c = String(l).slice(0, 2).toLowerCase();
      if (CODES.includes(c)) return c;
    }
    return "en";
  }
  const lang = pickLang();
  const rtl = RTL.has(lang);

  /* interface strings */
  const STR = {};
  function strings(l, obj) { STR[l] = Object.assign(STR[l] || {}, obj); }
  function has(key) { return (STR[lang] && STR[lang][key] != null) || (STR.en && STR.en[key] != null); }
  function t(key, vars) {
    let s = STR[lang] && STR[lang][key];
    if (s == null) s = STR.en && STR.en[key];
    if (s == null) { console.warn("i18n: no string", key); s = key; }
    if (vars) s = s.replace(/\{(\w+)\}/g, (m, k) => (vars[k] != null ? vars[k] : m));
    return s;
  }
  /* a multilingual name of data.js ({"hy": ..., "en": ...} or an index into B.names) in the language */
  function name(x) {
    if (typeof x === "number" && B.names) x = B.names[x];
    if (x == null || typeof x !== "object") return x;
    return x[lang] || x.en || x.hy || "";
  }
  function localizeData() {
    if (B._lang === lang) return;
    B._lang = lang;
    if (B.sections) for (const c of Object.keys(B.sections)) B.sections[c] = t(`section.${c}`);
    if (B.class_names) for (const c of Object.keys(B.class_names)) B.class_names[c] = name(B.class_names[c]);
    for (const d of B.district_names || []) d.name = name(d.name);
    for (const g of B.econ_groups || []) g.label = t(`econ.${g.key}`);
    for (const r of B.revenue || []) for (const g of r.groups) g.label = t(`rev.${g.key}`);
    for (const tree of Object.values(B.hierarchy || {})) {
      for (const s of tree) {
        s.name = t(`section.${s.code}`);
        for (const c of s.children) {
          c.name = name(c.name);
          for (const p of c.children) p.name = p.key ? t(`data.${p.key}`) : name(p.name);
        }
      }
    }
  }

  /* links between the pages keep the language */
  function withLang(href) {
    if (!href || /^([a-z]+:|#|\/\/)/i.test(href) || !/\.html(\?|#|$)/.test(href)) return href;
    const [path, hash] = href.split("#");
    const [file, query] = path.split("?");
    const p = new URLSearchParams(query || "");
    p.set("lang", lang);
    return `${file}?${p}${hash != null ? `#${hash}` : ""}`;
  }
  function setLang(l) {
    try { localStorage.setItem(STORE, l); } catch (e) { /* storage off */ }
    const u = new URL(location.href);
    u.searchParams.set("lang", l);
    location.assign(u.toString());
  }

  function translateDom(root) {
    const r = root || document;
    for (const n of r.querySelectorAll("[data-i18n]")) n.textContent = t(n.dataset.i18n);
    for (const n of r.querySelectorAll("[data-i18n-html]")) n.innerHTML = t(n.dataset.i18nHtml);
    for (const n of r.querySelectorAll("[data-i18n-attr]")) {
      for (const pair of n.dataset.i18nAttr.split(";")) {
        const [attr, key] = pair.split(":").map((s) => s.trim());
        if (attr && key) n.setAttribute(attr, t(key));
      }
    }
    for (const a of r.querySelectorAll("a[href]")) a.setAttribute("href", withLang(a.getAttribute("href")));
  }

  function load(src) {
    return new Promise((resolve) => {
      const s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = () => { console.warn("i18n: cannot load", src); resolve(); };
      document.head.append(s);
    });
  }
  /* run the code of a page once the strings of the language are loaded */
  function ready(page, fn) {
    document.documentElement.lang = lang;
    document.documentElement.dir = rtl ? "rtl" : "ltr";
    const files = [...new Set(["en", lang])].flatMap((l) => [`assets/i18n/${l}/common.js`, `assets/i18n/${l}/${page}.js`]);
    Promise.all(files.map(load)).then(() => {
      localizeData();
      translateDom();
      fn();
    });
  }

  const PAGES = ["index", "overview", "treemap", "flow", "execution", "districts", "receipt"];

  // Colour follows the functional section everywhere (fixed mapping, never by rank).
  const SECTION_SLOT = {
    "04": "--s1", "09": "--s2", "01": "--s3", "05": "--s4", "06": "--s5",
    "08": "--s6", "10": "--s7", "07": "--s8", "02": "--s-other", "03": "--s-other", "11": "--s-other",
  };
  const SECTION_ORDER = ["04", "09", "01", "05", "06", "08", "10", "07", "02", "03", "11"];

  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
  const sectionColor = (code) => css(SECTION_SLOT[code] || "--s-other");
  const sectionName = (code) => (B.sections && B.sections[code]) || code;
  const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* numbers in the conventions of the language; input amounts in million AMD */
  const NF = {};
  function num(x, d = 0) {
    if (x == null || isNaN(x)) return t("fmt.na");
    const f = NF[d] || (NF[d] = new Intl.NumberFormat(LOCALE[lang] || lang, { minimumFractionDigits: d, maximumFractionDigits: d }));
    return f.format(x);
  }
  function bn(m, d = 1) { return num(m / 1000, d); }
  function amd(m) {
    if (m == null || isNaN(m)) return t("fmt.na");
    const a = Math.abs(m);
    if (a >= 1000) return t("fmt.amd_bn", { n: num(m / 1000, 1) });
    if (a >= 1) return t("fmt.amd_m", { n: num(m, a >= 100 ? 0 : 1) });
    return t("fmt.amd_k", { n: num(Math.round(m * 1000)) });
  }
  function short(m) {
    if (m == null || isNaN(m)) return t("fmt.na");
    const a = Math.abs(m);
    if (a >= 1000) return t("fmt.bn", { n: num(m / 1000, 1) });
    if (a >= 1) return t("fmt.m", { n: num(m, a >= 100 ? 0 : 1) });
    return t("fmt.k", { n: num(Math.round(m * 1000)) });
  }
  const dram = (v) => num(Math.round(v));
  const pct = (x, d = 0) => (x == null || isNaN(x) ? t("fmt.na") : t("fmt.pct", { n: num(x * 100, d) }));

  function onTheme(cb) {
    const mq = window.matchMedia("(prefers-color-scheme: dark)");
    if (mq.addEventListener) mq.addEventListener("change", cb);
    new MutationObserver(cb).observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme", "class"] });
  }

  function el(tag, attrs, children) {
    const n = document.createElement(tag);
    if (attrs) for (const [k, v] of Object.entries(attrs)) {
      if (v == null) continue;
      if (k === "text") n.textContent = v;
      else if (k === "class") n.className = v;
      else if (k === "style") n.style.cssText = v;
      else if (k.startsWith("on")) n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v);
    }
    for (const c of [].concat(children || [])) if (c != null) n.append(c);
    return n;
  }

  function langSwitch() {
    const sel = el("select", { class: "lang", "aria-label": t("ui.language"), title: t("ui.language") });
    for (const [c, label] of LANGS) sel.append(el("option", { value: c, lang: c, dir: RTL.has(c) ? "rtl" : "ltr", text: label }));
    sel.value = lang;
    sel.addEventListener("change", () => setLang(sel.value));
    return sel;
  }

  function header(active) {
    const nav = el("nav", { class: "nav", "aria-label": t("ui.pages") });
    for (const p of PAGES) {
      const href = `${p}.html`;
      nav.append(el("a", { href: withLang(href), "aria-current": href === active ? "page" : null, text: t(`nav.${p}`) }));
    }
    const bar = el("header", { class: "topbar" }, el("div", { class: "topbar-inner" }, [
      el("a", { class: "brand", href: withLang("index.html") }, [
        el("span", { class: "brand-mark", "aria-hidden": "true", text: "֏" }),
        el("span", null, [t("brand.title"), el("small", { text: t("brand.subtitle") })]),
      ]),
      nav,
      langSwitch(),
    ]));
    document.body.prepend(bar);
    const foot = el("footer", { class: "foot" }, [
      el("p", { text: t("foot.data") }),
      el("p", { text: t("foot.mockup", { date: B.generated }) }),
      lang !== "en" ? el("p", { text: t("foot.translation") }) : null,
    ]);
    document.body.append(foot);
  }

  /* ECharts */
  function base() {
    return {
      animationDuration: reduced() ? 0 : 450,
      animationDurationUpdate: reduced() ? 0 : 350,
      textStyle: { fontFamily: css("--font-body") || "system-ui", color: css("--ink-2") },
      tooltip: {
        backgroundColor: css("--surface"), borderColor: css("--line"), borderWidth: 1,
        textStyle: { color: css("--ink"), fontSize: 12.5 },
        extraCssText: `box-shadow:0 6px 22px rgba(0,0,0,.14);border-radius:8px;direction:${rtl ? "rtl" : "ltr"};text-align:start;`,
        confine: true,
      },
    };
  }
  function axis(extra) {
    return Object.assign({
      axisLine: { lineStyle: { color: css("--axis") } },
      axisTick: { show: false },
      axisLabel: { color: css("--muted"), fontSize: 12 },
      splitLine: { lineStyle: { color: css("--line") } },
    }, extra || {});
  }
  function chart(node, build, opts) {
    const c = echarts.init(node, null, Object.assign({ renderer: "svg" }, opts || {}));
    const render = () => { c.setOption(build(), true); };
    render();
    onTheme(render);
    if (window.ResizeObserver) new ResizeObserver(() => c.resize()).observe(node);
    return { chart: c, render };
  }
  /* tooltip row: value first, then the series name, keyed by a short stroke */
  function tipRow(color, value, label) {
    return `<div style="display:flex;align-items:center;gap:8px;margin-top:3px">` +
      `<span style="width:12px;height:2px;background:${color};display:inline-block;border-radius:1px"></span>` +
      `<b style="font-variant-numeric:tabular-nums">${esc(value)}</b>` +
      `<span style="color:${css("--ink-2")}">${esc(label)}</span></div>`;
  }

  /* segmented control */
  function seg(container, options, value, onChange, label) {
    const g = el("div", { class: "seg", role: "group", "aria-label": label || null });
    const buttons = options.map(([v, text]) => {
      const b = el("button", { type: "button", "aria-pressed": String(v === value), text });
      b.addEventListener("click", () => {
        buttons.forEach((x) => x.setAttribute("aria-pressed", "false"));
        b.setAttribute("aria-pressed", "true");
        onChange(v);
      });
      g.append(b);
      return b;
    });
    container.append(g);
    return g;
  }

  /* table view: columns [{key,label,num,fmt}] */
  function table(container, columns, rows) {
    container.replaceChildren();
    const tbl = el("table", { class: "data" });
    const thead = el("tr");
    for (const c of columns) thead.append(el("th", { class: c.num ? "num" : null, text: c.label }));
    tbl.append(el("thead", null, thead));
    const tb = el("tbody");
    for (const r of rows) {
      const tr = el("tr");
      for (const c of columns) {
        const v = r[c.key];
        tr.append(el("td", { class: c.num ? "num" : null, text: c.fmt ? c.fmt(v, r) : (v == null ? "" : v) }));
      }
      tb.append(tr);
    }
    tbl.append(tb);
    container.append(tbl);
  }
  function tableToggle(btn, wrap, fill) {
    btn.textContent = t("ui.show_table");
    btn.addEventListener("click", () => {
      const show = wrap.hidden;
      if (show && fill) fill();
      wrap.hidden = !show;
      btn.textContent = show ? t("ui.hide_table") : t("ui.show_table");
      btn.setAttribute("aria-expanded", String(show));
    });
  }

  /* floating tooltip for plain-HTML views */
  let tipNode;
  function tip(e, nodes) {
    if (!tipNode) { tipNode = el("div", { class: "tip", role: "tooltip" }); document.body.append(tipNode); }
    if (!nodes) { tipNode.classList.remove("on"); return; }
    tipNode.replaceChildren(...nodes);
    const r = tipNode.getBoundingClientRect();
    let x = e.clientX + 14, y = e.clientY + 14;
    if (x + r.width > window.innerWidth - 8) x = e.clientX - r.width - 14;
    if (y + r.height > window.innerHeight - 8) y = e.clientY - r.height - 14;
    tipNode.style.left = `${Math.max(8, x)}px`;
    tipNode.style.top = `${Math.max(8, y)}px`;
    tipNode.classList.add("on");
  }

  /* status of an execution rate */
  function execStatus(rate) {
    if (rate == null || isNaN(rate)) return { cls: "", label: t("fmt.na") };
    if (rate >= 0.95) return { cls: "good", label: t("status.good") };
    if (rate >= 0.85) return { cls: "warning", label: t("status.warning") };
    if (rate >= 0.7) return { cls: "serious", label: t("status.serious") };
    return { cls: "critical", label: t("status.critical") };
  }

  window.YB = {
    B, LANGS, lang, rtl, PAGES, SECTION_ORDER, css, sectionColor, sectionName, esc, num, bn, amd, short, dram, pct,
    onTheme, el, header, base, axis, chart, tipRow, seg, table, tableToggle, tip, execStatus, reduced,
    t, has, name, strings, ready, translateDom, withLang,
  };
})();
