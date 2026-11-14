/* The singer's track on an arrangement page.
   A mix with a record's own singer can't be public, so it sits on the site locked (a ".locked" file, made
   with tools/lock_voice.mjs). On a device where the owner has entered the singer key (on the owner page,
   #owner), this script unlocks the file in the browser and the page plays it like any other track.
   Everywhere else the button for it ([data-locked]) is hidden, and a group of track buttons left with
   only one choice is hidden too.

   It works with any page: pages set audio.src to the ".locked" file name as they would an mp3, and this
   script swaps in the unlocked audio. Load it in <head>, before the page's own script. */
(function () {
  "use strict";
  var KEY = "ff.voicekey", base;
  try { base = new URL(".", document.currentScript.src).href; } catch (e) { base = "../../assets/"; }
  function key() { try { return localStorage.getItem(KEY) || ""; } catch (e) { return ""; } }
  var has = !!key();
  var root = document.documentElement;
  if (has) root.classList.add("ff-voice");

  var css = "html:not(.ff-voice) [data-locked],html:not(.ff-voice) .ff-lockonly{display:none!important}";
  var st = document.createElement("style"); st.textContent = css;
  (document.head || root).appendChild(st);

  /* ---------- unlocking ---------- */
  var S = window.crypto && window.crypto.subtle, INFO = new TextEncoder().encode("fret-finder voice");
  var pubP = null, cache = {};
  function pub() { return pubP || (pubP = fetch(base + "voice-key.json").then(function (r) { return r.json(); })); }
  /* The key can be a word (the owner's is a short word): it becomes the private key through PBKDF2. */
  var dMemo = {};
  function toD(w) {
    w = String(w || "").replace(/\s+/g, "");
    if (/^[A-Za-z0-9_-]{43}$/.test(w)) return Promise.resolve(w);
    w = w.toLowerCase();
    if (dMemo[w]) return dMemo[w];
    var te = new TextEncoder();
    return (dMemo[w] = S.importKey("raw", te.encode(w), "PBKDF2", false, ["deriveBits"])
      .then(function (k) { return S.deriveBits({ name: "PBKDF2", hash: "SHA-256", salt: te.encode("fret-finder voice key"), iterations: 100000 }, k, 256); })
      .then(function (b) { var s = ""; new Uint8Array(b).forEach(function (c) { s += String.fromCharCode(c); }); return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); }));
  }
  function open(buf, d) {
    var u = new Uint8Array(buf);
    if (u.length < 82 || String.fromCharCode(u[0], u[1], u[2], u[3]) !== "FFV1") return Promise.reject(new Error("not a locked file"));
    var epk = u.slice(4, 69), iv = u.slice(69, 81), ct = u.slice(81);
    return Promise.all([pub(), toD(d)]).then(function (pd) {
      var p = pd[0], d = pd[1];
      return Promise.all([
        S.importKey("jwk", { kty: "EC", crv: "P-256", x: p.x, y: p.y, d: d, ext: true }, { name: "ECDH", namedCurve: "P-256" }, false, ["deriveBits"]),
        S.importKey("raw", epk, { name: "ECDH", namedCurve: "P-256" }, false, [])
      ]);
    }).then(function (k) { return S.deriveBits({ name: "ECDH", public: k[1] }, k[0], 256); })
      .then(function (bits) { return S.importKey("raw", bits, "HKDF", false, ["deriveKey"]); })
      .then(function (hk) { return S.deriveKey({ name: "HKDF", hash: "SHA-256", salt: epk, info: INFO }, hk, { name: "AES-GCM", length: 256 }, false, ["decrypt"]); })
      .then(function (k) { return S.decrypt({ name: "AES-GCM", iv: iv }, k, ct); });
  }
  function unlock(url) {
    var abs = new URL(url, location.href).href;
    if (cache[abs]) return cache[abs];
    var d = key();
    if (!d || !S) return Promise.reject(new Error("no key on this device"));
    return (cache[abs] = fetch(abs).then(function (r) { if (!r.ok) throw new Error("missing " + url); return r.arrayBuffer(); })
      .then(function (b) { return open(b, d); })
      .then(function (pt) { return URL.createObjectURL(new Blob([pt], { type: /\.mp3\.locked$/i.test(abs) ? "audio/mpeg" : "audio/mp4" })); })
      .catch(function (e) { delete cache[abs]; throw e; }));
  }
  /* Checks a singer key against the small test file; used by the owner page. */
  window.ffVoice = {
    has: function () { return !!key(); },
    test: function (d) {
      if (!S) return Promise.resolve(false);
      return fetch(base + "voice-check.locked", { cache: "no-store" }).then(function (r) { return r.arrayBuffer(); })
        .then(function (b) { return open(b, d); })
        .then(function (pt) { return new TextDecoder().decode(pt) === "ok"; }, function () { return false; });
    },
    unlock: unlock
  };

  /* A saved key that no longer opens the test file (an old key) is thrown out, so the owner page asks again.
     Only when the file was fetched and would not open: being offline never removes a key. */
  if (has && S) {
    fetch(base + "voice-check.locked", { cache: "no-store" }).then(function (r) {
      if (!r.ok) return;
      return r.arrayBuffer().then(function (b) { return open(b, key()); }).then(function (pt) {
        if (new TextDecoder().decode(pt) !== "ok") throw new Error("wrong");
      }).catch(function () {
        try { localStorage.removeItem(KEY); } catch (e) {}
        has = false; root.classList.remove("ff-voice"); cache = {};
      });
    }, function () {});
  }

  /* ---------- audio elements take ".locked" sources ---------- */
  var M = window.HTMLMediaElement && HTMLMediaElement.prototype;
  if (!M) return;
  var desc = Object.getOwnPropertyDescriptor(M, "src");
  var isLocked = function (v) { return /\.locked(?:[?#].*)?$/i.test(String(v || "")); };
  function setLocked(el, v) {
    var prev = desc.get.call(el), token = {};
    el.__ffWant = token;
    el.__ffPending = unlock(v).then(function (u) {
      if (el.__ffWant === token) { desc.set.call(el, u); el.__ffShown = v; }
    }, function (e) {
      if (window.console) console.warn("Singer's track not played: " + e.message);
      if (el.__ffWant === token && prev) desc.set.call(el, prev);
    }).then(function () { if (el.__ffWant === token) el.__ffPending = null; });
  }
  if (desc && desc.set) {
    Object.defineProperty(M, "src", {
      configurable: true, enumerable: desc.enumerable,
      get: function () { return desc.get.call(this); },
      set: function (v) { if (isLocked(v)) setLocked(this, v); else { this.__ffWant = null; this.__ffPending = null; desc.set.call(this, v); } }
    });
    // pages that compare getAttribute('src') with the file they want see the ".locked" name
    var ga = Element.prototype.getAttribute;
    Element.prototype.getAttribute = function (n) {
      if (this.__ffShown && this.__ffWant !== null && String(n).toLowerCase() === "src" && this instanceof HTMLMediaElement) {
        var cur = ga.call(this, n);
        if (cur && cur.indexOf("blob:") === 0) return this.__ffShown;
      }
      return ga.call(this, n);
    };
    var sa = Element.prototype.setAttribute;
    Element.prototype.setAttribute = function (n, v) {
      if (this instanceof HTMLMediaElement && String(n).toLowerCase() === "src" && isLocked(v)) { setLocked(this, v); return; }
      return sa.call(this, n, v);
    };
  }
  var play = M.play;
  M.play = function () {
    var el = this;
    if (el.__ffPending) return el.__ffPending.then(function () { return play.call(el); });
    return play.call(el);
  };

  /* ---------- hiding what a visitor can't play ---------- */
  function tidy() {
    var bs = document.querySelectorAll("[data-locked]");
    for (var i = 0; i < bs.length; i++) {
      var g = bs[i].parentElement; if (!g || g.classList.contains("ff-lockonly")) continue;
      var open = 0, kids = g.children;
      for (var j = 0; j < kids.length; j++) if (!kids[j].hasAttribute("data-locked")) open++;
      if (open < 2) g.classList.add("ff-lockonly");
    }
    var as = document.querySelectorAll("audio[src$='.locked']");
    for (var k = 0; k < as.length; k++) { var s = as[k].getAttribute("src"); as[k].removeAttribute("src"); as[k].src = s; }
  }
  function start() {
    tidy();
    if (window.MutationObserver) new MutationObserver(function () { tidy(); }).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
