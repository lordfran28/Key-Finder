/* Slower tracks for practising along. Every audio player on a song page gets a row of speeds under it,
   from 100% down to 50%. The pitch stays where it is (the song keeps its key), and anything that follows
   the track (the keys or dots lighting, the bar that scrolls into view) follows the slower track too.
   Each song remembers its own speed on this device, so you can raise it a little day by day. */
(function () {
  "use strict";
  var STEPS = [1, 0.9, 0.8, 0.7, 0.6, 0.5];
  var PREFIX = /\/Fret-Finder\//i.test(location.pathname) ? "ff." : "kf.";
  var KEY = PREFIX + "speed:" + location.pathname.replace(/index\.html$/, "");
  function load() { try { var v = parseFloat(localStorage.getItem(KEY)); return STEPS.indexOf(v) >= 0 ? v : 1; } catch (e) { return 1; } }
  function save(v) { try { if (v === 1) localStorage.removeItem(KEY); else localStorage.setItem(KEY, String(v)); } catch (e) {} }
  var rate = load(), ctls = [];

  function apply(a) {
    try { a.preservesPitch = true; a.mozPreservesPitch = true; a.webkitPreservesPitch = true; } catch (e) {}
    try { a.defaultPlaybackRate = rate; if (Math.abs(a.playbackRate - rate) > 1e-3) a.playbackRate = rate; } catch (e) {}
  }
  function render() {
    ctls.forEach(function (c) {
      Array.prototype.forEach.call(c.querySelectorAll("button"), function (b) { b.setAttribute("aria-pressed", String(parseFloat(b.dataset.r) === rate)); });
    });
  }
  function setRate(v) {
    rate = v; save(v);
    Array.prototype.forEach.call(document.querySelectorAll("audio"), apply);
    render();
  }
  function style() {
    if (document.getElementById("sp-style")) return;
    var s = document.createElement("style"); s.id = "sp-style";
    s.textContent =
      ".sp-ctl{display:flex;flex-wrap:wrap;align-items:center;gap:4px 5px;margin:2px 0;flex:1 1 100%;width:100%;font-family:var(--body,var(--font-body,inherit))}" +
      ".sp-ctl .sp-lab{font-size:.95rem;font-style:italic;color:var(--muted,#776);margin-right:2px}" +
      ".sp-ctl button{font:600 .82rem/1 var(--body,var(--font-body,inherit));font-variant-numeric:lining-nums;cursor:pointer;border:1px solid var(--line,#ccb);" +
      "background:var(--sunk,var(--well,transparent));color:var(--ink,#222);border-radius:999px;padding:5px 7px;min-width:2.9em;-webkit-tap-highlight-color:transparent}" +
      ".sp-ctl button[aria-pressed=\"true\"]{background:var(--accent,#2D4A7F);color:var(--accent-ink,var(--surface,#fff));border-color:var(--accent,#2D4A7F)}" +
      ".sp-ctl button:focus-visible{outline:2px solid var(--accent,#2D4A7F);outline-offset:2px}";
    document.head.appendChild(s);
  }
  function attach(a) {
    if (a.dataset.speed) return;
    a.dataset.speed = "1";
    apply(a);
    a.addEventListener("loadedmetadata", function () { apply(a); });
    a.addEventListener("play", function () { apply(a); });
    var c = document.createElement("div");
    c.className = "sp-ctl"; c.setAttribute("role", "group"); c.setAttribute("aria-label", "Speed");
    c.innerHTML = '<span class="sp-lab">Speed</span>' + STEPS.map(function (v) {
      return '<button type="button" data-r="' + v + '" aria-pressed="false">' + Math.round(v * 100) + "%</button>";
    }).join("");
    c.addEventListener("click", function (e) { var b = e.target.closest("button[data-r]"); if (b) setRate(parseFloat(b.dataset.r)); });
    var p = a.parentNode;           // inside the player's own box, on a line of its own
    if (p.classList && (p.classList.contains("player") || p.classList.contains("pt-player"))) p.insertBefore(c, a.nextSibling);
    else if (p.classList && p.classList.contains("player-row")) p.appendChild(c);
    else p.parentNode.insertBefore(c, p.nextSibling);
    ctls.push(c); render();
  }
  function scan() { style(); Array.prototype.forEach.call(document.querySelectorAll("audio"), attach); }
  function start() {
    scan();
    if (window.MutationObserver) new MutationObserver(function (ms) {
      for (var i = 0; i < ms.length; i++) if (ms[i].addedNodes.length) { scan(); break; }
    }).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
