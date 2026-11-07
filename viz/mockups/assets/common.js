/* Shared helpers for the Yerevan budget mockups. Data: window.BUDGET (data.js), amounts in million AMD. */
(function () {
  "use strict";
  const B = window.BUDGET;

  const PAGES = [
    ["index.html", "Tools & mockups"],
    ["overview.html", "At a glance"],
    ["treemap.html", "Where money goes"],
    ["flow.html", "Money flow"],
    ["execution.html", "Plan vs actual"],
    ["districts.html", "Districts"],
    ["receipt.html", "Tax receipt"],
  ];

  // Colour follows the functional section everywhere (fixed mapping, never by rank).
  const SECTION_SLOT = {
    "04": "--s1", "09": "--s2", "01": "--s3", "05": "--s4", "06": "--s5",
    "08": "--s6", "10": "--s7", "07": "--s8", "02": "--s-other", "03": "--s-other", "11": "--s-other",
  };
  const SECTION_ORDER = ["04", "09", "01", "05", "06", "08", "10", "07", "02", "03", "11"];

  const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  const sectionColor = (code) => css(SECTION_SLOT[code] || "--s-other");
  const sectionName = (code) => (B.sections && B.sections[code]) || code;
  const reduced = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  /* numbers: input in million AMD */
  function bn(m, d = 1) { return (m / 1000).toFixed(d); }
  function amd(m) {
    if (m == null || isNaN(m)) return "n/a";
    const a = Math.abs(m);
    if (a >= 1000) return `AMD ${(m / 1000).toFixed(1)} bn`;
    if (a >= 1) return `AMD ${m.toFixed(a >= 100 ? 0 : 1)} m`;
    return `AMD ${Math.round(m * 1000)} k`;
  }
  function short(m) {
    if (m == null || isNaN(m)) return "n/a";
    const a = Math.abs(m);
    if (a >= 1000) return `${(m / 1000).toFixed(1)} bn`;
    if (a >= 1) return `${m.toFixed(a >= 100 ? 0 : 1)} m`;
    return `${Math.round(m * 1000)} k`;
  }
  const dram = (v) => Math.round(v).toLocaleString("en-US");
  const pct = (x, d = 0) => (x == null || isNaN(x) ? "n/a" : `${(x * 100).toFixed(d)}%`);

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

  function header(active) {
    const nav = el("nav", { class: "nav", "aria-label": "Mockups" });
    for (const [href, label] of PAGES) {
      nav.append(el("a", { href, "aria-current": href === active ? "page" : null, text: label }));
    }
    const bar = el("header", { class: "topbar" }, el("div", { class: "topbar-inner" }, [
      el("a", { class: "brand", href: "index.html" }, [
        el("span", { class: "brand-mark", "aria-hidden": "true", text: "֏" }),
        el("span", null, ["Yerevan Budget", el("small", { text: "visualization mockups" })]),
      ]),
      nav,
    ]));
    document.body.prepend(bar);
    const foot = el("footer", { class: "foot" }, [
      el("p", { text: "Data: Yerevan Municipality, Finance section (budget decisions and form Հ-9 execution reports), collected into DuckDB by opendataam/arm-yerevan-budget. Amounts are nominal AMD." }),
      el("p", { text: `Mockup, not an official publication. Data snapshot ${B.generated}.` }),
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
        extraCssText: "box-shadow:0 6px 22px rgba(0,0,0,.14);border-radius:8px;",
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
    const t = el("table", { class: "data" });
    const thead = el("tr");
    for (const c of columns) thead.append(el("th", { class: c.num ? "num" : null, text: c.label }));
    t.append(el("thead", null, thead));
    const tb = el("tbody");
    for (const r of rows) {
      const tr = el("tr");
      for (const c of columns) {
        const v = r[c.key];
        tr.append(el("td", { class: c.num ? "num" : null, text: c.fmt ? c.fmt(v, r) : (v == null ? "" : v) }));
      }
      tb.append(tr);
    }
    t.append(tb);
    container.append(t);
  }
  function tableToggle(btn, wrap, fill) {
    btn.addEventListener("click", () => {
      const show = wrap.hidden;
      if (show && fill) fill();
      wrap.hidden = !show;
      btn.textContent = show ? "Hide table" : "Show table";
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
    if (rate == null || isNaN(rate)) return { cls: "", label: "n/a" };
    if (rate >= 0.95) return { cls: "good", label: "On plan" };
    if (rate >= 0.85) return { cls: "warning", label: "Behind" };
    if (rate >= 0.7) return { cls: "serious", label: "Lagging" };
    return { cls: "critical", label: "Far behind" };
  }

  window.YB = {
    B, PAGES, SECTION_ORDER, css, sectionColor, sectionName, esc, bn, amd, short, dram, pct, onTheme, el,
    header, base, axis, chart, tipRow, seg, table, tableToggle, tip, execStatus, reduced,
  };
})();
