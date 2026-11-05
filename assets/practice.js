/* Practising on Key Finder.
   On a song page: the music stand (the chord you're on and the one coming next, large, following the
   track) and a note of the days the song was played and at what speed.
   On the library: the same keyboard drawing for the shape book, and the notes read back.
   Everything it keeps stays on this device, under names that start with "kf.". */
(function () {
  "use strict";
  var BLK = [1, 3, 6, 8, 10];
  var HERE = (document.currentScript && document.currentScript.src) || location.href;
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }

  /* ---------- What this device keeps ---------- */
  function get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function put(k, v) { try { if (v == null) localStorage.removeItem(k); else localStorage.setItem(k, v); } catch (e) {} }
  function getJSON(k, d) { try { var v = JSON.parse(get(k)); return v == null ? d : v; } catch (e) { return d; } }
  function songPath(p) { return String(p || location.pathname).replace(/index\.html$/, ""); }
  /* days counted in the device's own time, so "today" ends at midnight where he is */
  function today(d) { d = d || new Date(); return Math.floor((d.getTime() - d.getTimezoneOffset() * 60000) / 86400000); }
  function speedOf(path) { var v = parseFloat(get("kf.speed:" + songPath(path))); return v > 0 && v <= 1 ? v : 1; }
  function playedOf(path) {
    var L = getJSON("kf.played:" + songPath(path), {}), days = [];
    Object.keys(L).forEach(function (d) {
      var secs = 0, best = null;
      for (var sp in L[d]) { secs += L[d][sp]; if (best === null || L[d][sp] > L[d][best]) best = sp; }
      if (secs >= 20) days.push({ d: +d, secs: secs, speed: +best });
    });
    if (!days.length) return null;
    days.sort(function (a, b) { return a.d - b.d; });
    return { last: days[days.length - 1].d, days: days.length, first: days[0].speed, now: Math.round(speedOf(path) * 100) };
  }
  function whenText(d) {
    var n = today() - d;
    if (n <= 0) return "today";
    if (n === 1) return "yesterday";
    var dt = new Date(d * 86400000);
    if (n < 7) return "on " + dt.toLocaleDateString(undefined, { weekday: "long", timeZone: "UTC" });
    return "on " + dt.toLocaleDateString(undefined, { day: "numeric", month: "short", timeZone: "UTC" });
  }

  /* ---------- A keyboard with the keys to press ---------- */
  function span(all, minW) {
    var lo = Math.min.apply(null, all) - 1, hi = Math.max.apply(null, all) + 1;
    while (BLK.indexOf(((lo % 12) + 12) % 12) >= 0) lo--;
    while (BLK.indexOf(hi % 12) >= 0) hi++;
    while (lo % 12 !== 0 && lo % 12 !== 5) lo--;
    while (hi % 12 !== 4 && hi % 12 !== 11) hi++;
    function whites() { var n = 0; for (var m = lo; m <= hi; m++) if (BLK.indexOf(m % 12) < 0) n++; return n; }
    while (whites() < minW) { lo--; while (BLK.indexOf(lo % 12) >= 0) lo--; if (whites() < minW) { hi++; while (BLK.indexOf(hi % 12) >= 0) hi++; } }
    return [lo, hi];
  }
  function kb(o) {
    var lh = o.lh || [], rh = o.rh || [], fill = o.fill || [], tones = o.tones || {};
    var all = lh.concat(rh).concat(fill);
    if (!all.length) return "";
    var r = span(o.range ? all.concat(o.range) : all, o.minWhites || 10), lo = r[0], hi = r[1];
    var W = 9, H = 44, BW = 5.6, BH = 27, xs = {}, x = 0, m;
    for (m = lo; m <= hi; m++) if (BLK.indexOf(m % 12) < 0) { xs[m] = x; x += W; }
    for (m = lo; m <= hi; m++) if (BLK.indexOf(m % 12) >= 0) xs[m] = xs[m - 1] + W - BW / 2;
    var s = '<svg class="pk' + (o.cls ? " " + o.cls : "") + '" viewBox="-1 -1 ' + (x + 2) + " " + (H + 2) + '" role="img" aria-label="' + esc(o.label || "keyboard") + '">';
    for (m = lo; m <= hi; m++) if (BLK.indexOf(m % 12) < 0) s += '<rect class="w" x="' + xs[m] + '" y="0" width="' + W + '" height="' + H + '" rx="1"/>';
    for (m = lo; m <= hi; m++) if (BLK.indexOf(m % 12) >= 0) s += '<rect class="b" x="' + xs[m] + '" y="0" width="' + BW + '" height="' + BH + '" rx=".8"/>';
    if (xs[60] !== undefined) s += '<rect class="mc" x="' + (xs[60] + W / 2 - 2) + '" y="' + (H - 3) + '" width="4" height="1.4" rx=".7"/>';
    function dot(m, cls, lab) {
      var b = BLK.indexOf(m % 12) >= 0, cx = b ? xs[m] + BW / 2 : xs[m] + W / 2, cy = b ? BH - 6 : H - 9;
      return '<circle class="' + cls + '" data-m="' + m + '" data-h="' + cls + '" cx="' + cx + '" cy="' + cy + '" r="4.1"/><text x="' + cx + '" y="' + (cy + 0.2) + '">' + esc(lab) + "</text>";
    }
    lh.forEach(function (m) { s += dot(m, "L", tones[m] || ""); });
    rh.forEach(function (m) { s += dot(m, "R", tones[m] || ""); });
    fill.forEach(function (m, i) { s += dot(m, "F", String(i + 1)); });
    return s + "</svg>";
  }
  function style() {
    if (document.getElementById("pk-style")) return;
    var tl = new URL("textile-light.jpg", HERE).href, td = new URL("textile-dark.jpg", HERE).href;
    var s = document.createElement("style"); s.id = "pk-style";
    s.textContent = [
      ".pk{display:block;width:100%;height:auto;--pk-l:var(--accent,#2D4A7F);--pk-r:var(--brass,#8C6414);--pk-f:var(--voice,#8A3A1F);--pk-w:var(--key-white,#FBF8F1);--pk-e:var(--key-edge,#C9BA9E);--pk-b:var(--key-black,#1E1915);--pk-t:#fff}",
      "@media (prefers-color-scheme:dark){.pk{--pk-r:var(--brass,#E2BD6B);--pk-f:var(--voice,#E39A72);--pk-w:var(--key-white,#BDB29D);--pk-e:var(--key-edge,#7E7462);--pk-b:var(--key-black,#0B0A08);--pk-t:#13110E}}",
      ".pk .w{fill:var(--pk-w);stroke:var(--pk-e);stroke-width:.8}.pk .b{fill:var(--pk-b)}.pk .mc{fill:var(--muted,#776)}",
      ".pk circle.L{fill:var(--pk-l)}.pk circle.R{fill:var(--pk-r)}.pk circle.F{fill:var(--pk-f)}",
      ".pk text{font:700 6.2px var(--body,Georgia,serif);fill:var(--pk-t);text-anchor:middle;dominant-baseline:central;pointer-events:none}",
      ".pk circle.on{fill:#E3A008!important;stroke:#4A3000;stroke-width:1.2;transform-box:fill-box;transform-origin:center;transform:scale(1.25)}",
      "@media (prefers-color-scheme:dark){.pk circle.on{fill:#FFCB4D!important}}",
      /* the music stand */
      ".kfp-open{font:inherit;font-size:.95rem;border:1px solid var(--accent,#2D4A7F);background:var(--surface,#fff);color:var(--accent,#2D4A7F);border-radius:999px;padding:4px 12px;cursor:pointer}",
      ".kfp-open:hover{background:var(--accent-soft,#DFE5EF)}",
      "html.kfs-on,html.kfs-on body{overflow:hidden!important}",
      ".kfs{position:fixed;inset:0;z-index:2147483000;isolation:isolate;background:var(--bg,#F2EBDD);color:var(--ink,#211B16);display:flex;flex-direction:column;gap:8px;" +
        "padding:max(10px,env(safe-area-inset-top)) max(16px,env(safe-area-inset-right)) max(12px,env(safe-area-inset-bottom)) max(16px,env(safe-area-inset-left));font-family:var(--body,Georgia,serif)}",
      ".kfs::before{content:'';position:absolute;inset:0;z-index:-1;pointer-events:none;background:url(" + tl + ") center/cover no-repeat;opacity:.12}",
      "@media (prefers-color-scheme:dark){.kfs::before{background-image:url(" + td + ");opacity:.4}}",
      ".kfs[hidden]{display:none}",
      ".kfs button{font:inherit;color:inherit;-webkit-tap-highlight-color:transparent;cursor:pointer}",
      ".kfs-top{display:flex;align-items:center;gap:10px;min-height:44px}",
      ".kfs-x{border:0;background:none;padding:6px 10px 6px 0;font:400 1.25rem/1 var(--display,Georgia,serif)!important;color:var(--accent,#2D4A7F)!important}",
      ".kfs-where{flex:1;min-width:0;text-align:right;color:var(--muted,#6A5D4F);font-size:1.05rem;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}",
      ".kfs-where b{color:var(--ink,#211B16);font-weight:600}",
      ".kfs-main{flex:1;min-height:0;overflow:hidden;display:flex;flex-direction:column;justify-content:center;gap:18px}",
      ".kfs-now,.kfs-next{display:flex;flex-direction:column;align-items:center;text-align:center;min-width:0}",
      ".kfs-cn{font:400 clamp(3.2rem,15vw,7rem)/1 var(--display,Georgia,serif);color:var(--accent,#2D4A7F);letter-spacing:.01em}",
      ".kfs-form{font-size:.95rem;color:var(--muted,#6A5D4F);text-transform:uppercase;letter-spacing:.08em;margin-top:4px}",
      ".kfs-kb{width:100%;max-width:920px;margin-top:10px}.kfs-kb .pk{max-height:34vh}",
      ".kfs-names{font-size:1.05rem;color:var(--muted,#6A5D4F);margin-top:4px;font-variant-numeric:lining-nums}",
      ".kfs-fill{width:100%;max-width:920px;margin-top:8px;display:flex;flex-direction:column;align-items:center}.kfs-fill .pk{max-width:100%}",
      ".kfs-fh{font-size:.95rem;color:var(--voice,#8A3A1F)}",
      ".kfs-words{font-style:italic;font-size:1.2rem;color:var(--ink,#211B16);margin-top:8px;min-height:1.5em}",
      ".kfs-prog{width:100%;max-width:920px;height:4px;border-radius:2px;background:var(--line,#D6C8B0);margin-top:12px;overflow:hidden}",
      ".kfs-prog i{display:block;height:100%;width:0;background:var(--brass,#8C6414)}",
      ".kfs-next{opacity:.85}",
      ".kfs-lab{font-variant-caps:all-small-caps;letter-spacing:.12em;font-size:1.05rem;color:var(--muted,#6A5D4F);line-height:1}",
      ".kfs-cn2{font:400 clamp(2rem,8vw,3.4rem)/1.05 var(--display,Georgia,serif);color:var(--ink,#211B16);margin-top:2px}",
      ".kfs-kb2{width:72%;max-width:560px;margin-top:6px}.kfs-kb2 .pk{max-height:18vh}",
      ".kfs-ctl{display:flex;flex-direction:column;align-items:center;gap:8px}",
      ".kfs-row{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;gap:8px 10px}",
      ".kfs-ic{width:52px;height:52px;border-radius:50%;border:1px solid var(--line,#D6C8B0);background:var(--surface,#FAF6EE);display:inline-flex;align-items:center;justify-content:center}",
      ".kfs-ic svg{width:22px;height:22px;fill:var(--ink,#211B16)}",
      ".kfs-ic.play{width:64px;height:64px;background:var(--accent,#2D4A7F);border-color:var(--accent,#2D4A7F)}.kfs-ic.play svg{width:26px;height:26px;fill:var(--accent-ink,var(--surface,#fff))}",
      ".kfs-pills{display:flex;flex-wrap:wrap;justify-content:center;gap:5px}",
      ".kfs-pills button{font:600 .85rem/1 var(--body,Georgia,serif);font-variant-numeric:lining-nums;border:1px solid var(--line,#D6C8B0);background:var(--sunk,transparent);border-radius:999px;padding:6px 9px;min-width:3em}",
      ".kfs-pills button[aria-pressed=true]{background:var(--accent,#2D4A7F);border-color:var(--accent,#2D4A7F);color:var(--accent-ink,var(--surface,#fff))}",
      ".kfs button:focus-visible{outline:2px solid var(--accent,#2D4A7F);outline-offset:2px}",
      "@media (min-aspect-ratio:5/4) and (min-width:700px){.kfs-main{flex-direction:row;align-items:center;gap:4vw}.kfs-now{flex:3}.kfs-next{flex:2}.kfs-kb2{width:100%}.kfs-kb .pk{max-height:42vh}.kfs-kb2 .pk{max-height:26vh}}",
      "@media (max-height:560px){.kfs{gap:4px}.kfs-top{min-height:34px}.kfs-main{gap:10px}.kfs-cn{font-size:clamp(2.2rem,11vh,3.6rem)}.kfs-form{font-size:.8rem;margin-top:0}" +
        ".kfs-kb{margin-top:4px}.kfs-kb .pk{max-height:30vh}.kfs-names{font-size:.95rem;margin-top:0}.kfs-words{font-size:1.05rem;margin-top:2px}.kfs-prog{margin-top:6px}" +
        ".kfs-cn2{font-size:clamp(1.6rem,8vh,2.4rem)}.kfs-kb2 .pk{max-height:22vh}" +
        ".kfs-ctl{flex-direction:row;flex-wrap:wrap;justify-content:center;gap:6px 14px}.kfs-ic{width:42px;height:42px}.kfs-ic.play{width:50px;height:50px}}",
      "@media (prefers-reduced-motion:reduce){.pk circle.on{transform:none}}"
    ].join("\n");
    document.head.appendChild(s);
  }

  window.kfPractice = { kb: kb, span: span, style: style, today: today, speedOf: speedOf, playedOf: playedOf, whenText: whenText, songPath: songPath, getJSON: getJSON, put: put };

  /* ---------- Song pages ---------- */
  var dataEl = document.getElementById("kf-data");
  if (!dataEl) return;
  var D; try { D = JSON.parse(dataEl.textContent); } catch (e) { return; }
  if (!D || !D.bars || !D.bars.length) return;

  function start() {
    var audio = document.getElementById("audio") || document.querySelector("audio");
    if (!audio) return;
    style();
    logPlaying(audio);
    shapeLink();
    stand(audio);
  }

  /* The days this song was played, and at what speed, for the library's "where you left off". */
  function logPlaying(audio) {
    var KEY = "kf.played:" + songPath(), acc = 0, since = null;
    function tick() { if (since !== null) { var now = performance.now(); acc += (now - since) / 1000; since = now; } }
    function flush() {
      tick();
      if (acc < 1) return;
      var L = getJSON(KEY, {}), d = String(today()), sp = String(Math.round((audio.playbackRate || 1) * 100));
      L[d] = L[d] || {}; L[d][sp] = Math.round((L[d][sp] || 0) + acc); acc = 0;
      var keys = Object.keys(L).sort(function (a, b) { return a - b; });
      while (keys.length > 400) delete L[keys.shift()];
      put(KEY, JSON.stringify(L));
    }
    audio.addEventListener("play", function () { since = performance.now(); });
    ["pause", "ended", "emptied"].forEach(function (ev) { audio.addEventListener(ev, function () { flush(); since = null; }); });
    audio.addEventListener("ratechange", flush);
    setInterval(function () { if (since !== null) flush(); }, 15000);
    document.addEventListener("visibilitychange", function () { if (document.hidden) flush(); });
    window.addEventListener("pagehide", flush);
  }

  /* From the song's shapes to the shape book, with this song as the one being learned. */
  function shapeLink() {
    var sh = document.getElementById("shapes");
    if (!sh || document.getElementById("kfp-book")) return;
    var slug = songPath().replace(/\/$/, "").split("/").pop();
    var p = document.createElement("p"); p.id = "kfp-book";
    p.innerHTML = '<a href="../../#shapes/' + encodeURIComponent(slug) + '">Practise them in the shape book</a>';
    sh.parentNode.insertBefore(p, sh);
  }

  /* ---------- The music stand ---------- */
  function stand(audio) {
    /* every change of diagram, in time: a voicing that keeps going is one change; a fill rides on the chord it sounds over */
    var firstT = {}, EV = D.events || [];
    EV.forEach(function (e) { if (!(e[4] in firstT) || e[0] < firstT[e[4]]) firstT[e[4]] = e[0]; });
    var CH = [], prevKey = null;
    D.bars.forEach(function (b, bi) {
      var total = 0; (b.segs || []).forEach(function (s) { total += s.beats || 0; });
      var beat = total ? (b.end - b.start) / total : 0;
      (b.segs || []).forEach(function (s) {
        var dk = s.same || s.id, t = s.id in firstT ? firstT[s.id] : b.start + (s.at || 0) * beat;
        if (dk === prevKey && CH.length) { CH[CH.length - 1].ids[s.id] = 1; return; }
        prevKey = dk;
        var ids = {}; ids[s.id] = 1;
        CH.push({ t: t, bar: bi, s: s, ids: ids, fill: null });
      });
      if (b.fill) {
        var ft = b.fill.t != null ? b.fill.t : (b.fill.id in firstT ? firstT[b.fill.id] : b.end);
        for (var k = CH.length - 1; k >= 0; k--) if (CH[k].t <= ft + 0.05) { CH[k].fill = b.fill; CH[k].ids[b.fill.id] = 1; break; }
      }
    });
    CH.sort(function (a, b) { return a.t - b.t; });
    if (!CH.length) return;

    var ICON = {
      play: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 4.5v15l13-7.5z"/></svg>',
      pause: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 4h4.5v16H6zM13.5 4H18v16h-4.5z"/></svg>',
      prev: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 4h2.5v16H5zM20 4.5v15L9 12z"/></svg>',
      next: '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M16.5 4H19v16h-2.5zM4 4.5v15L15 12z"/></svg>'
    };
    var ov = document.createElement("div");
    ov.className = "kfs"; ov.hidden = true;
    ov.setAttribute("role", "dialog"); ov.setAttribute("aria-modal", "true"); ov.setAttribute("aria-label", "Music stand");
    ov.innerHTML =
      '<div class="kfs-top"><button type="button" class="kfs-x">&larr; Back</button><div class="kfs-where" aria-live="off"></div></div>' +
      '<div class="kfs-main">' +
        '<section class="kfs-now"><div class="kfs-cn"></div><div class="kfs-form"></div><div class="kfs-kb"></div><div class="kfs-names"></div>' +
          '<div class="kfs-fill" hidden></div><div class="kfs-words"></div><div class="kfs-prog"><i></i></div></section>' +
        '<section class="kfs-next" aria-label="Next"><div class="kfs-lab">Next</div><div class="kfs-cn2"></div><div class="kfs-kb2"></div></section>' +
      "</div>" +
      '<div class="kfs-ctl"><div class="kfs-row">' +
        '<button type="button" class="kfs-ic" data-go="-1" aria-label="Previous chord">' + ICON.prev + "</button>" +
        '<button type="button" class="kfs-ic play" aria-label="Play">' + ICON.play + "</button>" +
        '<button type="button" class="kfs-ic" data-go="1" aria-label="Next chord">' + ICON.next + "</button>" +
      '</div><div class="kfs-pills kfs-tracks" role="group" aria-label="Which track"></div><div class="kfs-pills kfs-speeds" role="group" aria-label="Speed"></div></div>';
    document.body.appendChild(ov);
    var q = function (c) { return ov.querySelector(c); };
    var playBtn = q(".play");

    var open = document.createElement("button");
    open.type = "button"; open.className = "kfp-open"; open.textContent = "Music stand";
    var sw = document.querySelector(".player .sw");
    if (sw && sw.parentNode) sw.parentNode.insertBefore(open, sw.nextSibling);
    else if (audio.parentNode) audio.parentNode.insertBefore(open, audio.nextSibling);

    function names(s) {
      var n = (s.names || []).map(function (x) { return String(x).replace(/\d+$/, ""); });
      var l = n.slice(0, s.lh.length), r = n.slice(s.lh.length);
      return (l.length ? "Left " + l.join(" ") : "") + (l.length && r.length ? " · " : "") + (r.length ? "Right " + r.join(" ") : "");
    }
    function barLabel(b) { var n = String(b.n); return /^\d+$/.test(n) ? "Bar " + n : n; }
    var cur = -1, lit = [];
    function draw(i) {
      cur = i;
      var c = CH[i], n = CH[i + 1], s = c.s;
      q(".kfs-cn").textContent = s.c;
      q(".kfs-form").textContent = s.form || "";
      q(".kfs-kb").innerHTML = kb({ lh: s.lh, rh: s.rh, tones: s.tones, minWhites: 12, label: s.c });
      q(".kfs-names").textContent = names(s);
      var f = q(".kfs-fill");
      if (c.fill) {
        f.hidden = false;
        f.innerHTML = '<div class="kfs-fh">Fill into ' + esc(c.fill.into) + (c.fill.scale ? " · " + esc(c.fill.scale) : "") + "</div>" + kb({ fill: c.fill.notes, minWhites: 7, label: "fill" });
      } else { f.hidden = true; f.innerHTML = ""; }
      words();
      if (n) { q(".kfs-cn2").textContent = n.s.c; q(".kfs-kb2").innerHTML = kb({ lh: n.s.lh, rh: n.s.rh, tones: n.s.tones, minWhites: 12, label: n.s.c }); q(".kfs-next").hidden = false; }
      else { q(".kfs-next").hidden = true; }
      lit = [];
      fit();
    }
    /* the fill's keys drawn the same size as the chord's, so the two read as one hand */
    function fitFill() {
      var a = q(".kfs-kb svg"), f = q(".kfs-fill svg");
      if (!a || !f) return;
      var r = a.getBoundingClientRect(), va = a.viewBox.baseVal, vf = f.viewBox.baseVal;
      if (!r.width || !va.width) return;
      var ppu = Math.min(r.width / va.width, r.height / va.height);
      f.style.width = Math.round(vf.width * ppu) + "px";
    }
    /* on a short screen the keyboards come down in size until everything fits, the chord's name included */
    function fit() {
      var main = q(".kfs-main"), svgs = ov.querySelectorAll(".kfs-kb .pk, .kfs-kb2 .pk");
      Array.prototype.forEach.call(svgs, function (x) { x.style.maxHeight = ""; });
      fitFill();
      for (var i = 0; i < 12 && main.scrollHeight > main.clientHeight + 2; i++) {
        Array.prototype.forEach.call(svgs, function (x) { x.style.maxHeight = Math.max(34, Math.floor(x.getBoundingClientRect().height * 0.86)) + "px"; });
        fitFill();
      }
    }
    window.addEventListener("resize", function () { if (!ov.hidden) fit(); });
    var wordsBar = -1;
    function words() {
      var tt = Math.max(audio.currentTime, CH[cur].t), bi = CH[cur].bar;
      for (var i = bi; i < D.bars.length; i++) { if (D.bars[i].start <= tt + 0.03) bi = i; else break; }
      if (bi === wordsBar) return;
      wordsBar = bi;
      var b = D.bars[bi];
      q(".kfs-words").textContent = b.words || "";
      q(".kfs-where").innerHTML = (b.sec && !/[a-z]/i.test(String(b.n)) ? esc(b.sec) + " · " : "") + "<b>" + esc(barLabel(b)) + "</b>";
    }
    function at(t) { var k = 0; for (var i = 0; i < CH.length; i++) { if (CH[i].t <= t + 0.06) k = i; else break; } return k; }
    var raf = 0;
    function frame() {
      var t = audio.currentTime, k = at(t);
      if (k !== cur) { wordsBar = -1; draw(k); }
      words();
      var c = CH[cur], end = CH[cur + 1] ? CH[cur + 1].t : (D.bars[D.bars.length - 1].end || c.t + 4);
      q(".kfs-prog i").style.width = Math.max(0, Math.min(100, (t - c.t) / Math.max(0.1, end - c.t) * 100)) + "%";
      lit.forEach(function (el) { el.classList.remove("on"); }); lit = [];
      for (var j = 0; j < EV.length; j++) {
        var e = EV[j]; if (e[0] > t + 0.02) break;
        if (e[0] <= t && t < Math.min(e[3], e[0] + 0.9) && c.ids[e[4]]) {
          var el = ov.querySelector((e[2] === "F" ? ".kfs-fill" : ".kfs-kb") + ' circle[data-m="' + e[1] + '"][data-h="' + e[2] + '"]');
          if (el) { el.classList.add("on"); lit.push(el); }
        }
      }
      if (!audio.paused && !ov.hidden) raf = requestAnimationFrame(frame);
    }
    function playState() {
      var p = !audio.paused;
      playBtn.innerHTML = p ? ICON.pause : ICON.play;
      playBtn.setAttribute("aria-label", p ? "Pause" : "Play");
    }
    function shown(b) { return b && !b.hidden && getComputedStyle(b).display !== "none"; }
    function pills() {
      var tr = Array.prototype.filter.call(document.querySelectorAll(".player .sw button[data-src]"), shown);
      q(".kfs-tracks").innerHTML = tr.length > 1 ? tr.map(function (b, i) {
        return '<button type="button" data-i="' + i + '" aria-pressed="' + (b.getAttribute("aria-pressed") === "true") + '">' + esc(b.textContent) + "</button>"; }).join("") : "";
      q(".kfs-tracks").hidden = tr.length < 2;
      q(".kfs-tracks").onclick = function (e) { var x = e.target.closest("button[data-i]"); if (x && tr[+x.dataset.i]) { tr[+x.dataset.i].click(); setTimeout(pills, 0); } };
      var ctl = document.querySelector(".sp-ctl"), sp = ctl ? Array.prototype.slice.call(ctl.querySelectorAll("button[data-r]")) : [];
      q(".kfs-speeds").innerHTML = sp.map(function (b, i) {
        return '<button type="button" data-i="' + i + '" aria-pressed="' + (b.getAttribute("aria-pressed") === "true") + '">' + esc(b.textContent) + "</button>"; }).join("");
      q(".kfs-speeds").hidden = !sp.length;
      q(".kfs-speeds").onclick = function (e) { var x = e.target.closest("button[data-i]"); if (x && sp[+x.dataset.i]) { sp[+x.dataset.i].click(); pills(); } };
    }
    var lock = null;
    function wake() {
      if (!navigator.wakeLock || ov.hidden || document.hidden) return;
      navigator.wakeLock.request("screen").then(function (l) { lock = l; }).catch(function () {});
    }
    var opener = null;
    function show() {
      opener = document.activeElement;
      ov.hidden = false; document.documentElement.classList.add("kfs-on");
      pills(); playState(); wordsBar = -1; draw(at(audio.currentTime)); frame();
      if (!audio.paused) { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); }
      wake(); playBtn.focus();
      try { history.pushState({ kfs: 1 }, ""); } catch (e) {}
    }
    function hide(fromHistory) {
      if (ov.hidden) return;
      ov.hidden = true; document.documentElement.classList.remove("kfs-on");
      cancelAnimationFrame(raf);
      if (lock) { try { lock.release(); } catch (e) {} lock = null; }
      if (opener && opener.focus) opener.focus();
      if (!fromHistory) { try { if (history.state && history.state.kfs) history.back(); } catch (e) {} }
      var bar = document.getElementById("bar-" + CH[Math.max(0, cur)].bar);
      if (bar) bar.scrollIntoView({ block: "center" });
    }
    function go(d) {
      var k = at(audio.currentTime);
      if (d < 0 && audio.currentTime - CH[k].t > 1.2 && !audio.paused) d = 0;   /* back to the start of this chord first */
      k = Math.max(0, Math.min(CH.length - 1, k + d));
      audio.currentTime = Math.max(0, CH[k].t - 0.03);
      wordsBar = -1; draw(k); frame();
    }
    open.addEventListener("click", show);
    q(".kfs-x").addEventListener("click", function () { hide(false); });
    playBtn.addEventListener("click", function () { if (audio.paused) { var p = audio.play(); if (p && p.catch) p.catch(function () {}); } else audio.pause(); });
    ov.querySelectorAll("[data-go]").forEach(function (b) { b.addEventListener("click", function () { go(+b.dataset.go); }); });
    audio.addEventListener("play", function () { playState(); if (!ov.hidden) { cancelAnimationFrame(raf); raf = requestAnimationFrame(frame); } });
    audio.addEventListener("pause", playState);
    audio.addEventListener("seeked", function () { if (!ov.hidden) frame(); });
    audio.addEventListener("ratechange", function () { if (!ov.hidden) pills(); });
    window.addEventListener("popstate", function () { hide(true); });
    document.addEventListener("visibilitychange", function () { if (!document.hidden) wake(); });
    ov.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { e.preventDefault(); hide(false); }
      else if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
      else if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
      else if (e.key === " " && !(e.target.closest && e.target.closest("button"))) { e.preventDefault(); playBtn.click(); }
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
