#!/usr/bin/env node
// Locks a track (a mix with a record's own singer) so only the owner's devices can play it.
//
//   node tools/lock_voice.mjs IN.mp3 OUT.mp3.locked
//
// The file is encrypted to the public key in assets/voice-key.json. The matching private key (the
// "singer key") is never in this repository: the owner enters it once per device on the owner page
// (#owner), and assets/voice.js uses it there to play the track. Anyone else gets bytes they can't use.
//
// Format: "FFV1" | ephemeral P-256 public key (65 bytes, raw) | IV (12) | AES-256-GCM ciphertext.
// The AES key is HKDF-SHA256(ECDH(ephemeral, owner), salt = ephemeral key, info = "fret-finder voice").
import { webcrypto as wc } from "node:crypto";
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const S = wc.subtle, ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
const INFO = new TextEncoder().encode("fret-finder voice");

export async function lockBytes(plain, pubJwk) {
  const owner = await S.importKey("jwk", { kty: "EC", crv: "P-256", x: pubJwk.x, y: pubJwk.y, ext: true }, { name: "ECDH", namedCurve: "P-256" }, false, []);
  const eph = await S.generateKey({ name: "ECDH", namedCurve: "P-256" }, true, ["deriveBits"]);
  const epkRaw = new Uint8Array(await S.exportKey("raw", eph.publicKey));
  const bits = await S.deriveBits({ name: "ECDH", public: owner }, eph.privateKey, 256);
  const hk = await S.importKey("raw", bits, "HKDF", false, ["deriveKey"]);
  const key = await S.deriveKey({ name: "HKDF", hash: "SHA-256", salt: epkRaw, info: INFO }, hk, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
  const iv = wc.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await S.encrypt({ name: "AES-GCM", iv }, key, plain));
  const out = new Uint8Array(4 + 65 + 12 + ct.length);
  out.set(new TextEncoder().encode("FFV1"), 0); out.set(epkRaw, 4); out.set(iv, 69); out.set(ct, 81);
  return out;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const [, , inp, outp] = process.argv;
  if (!inp || !outp || !outp.endsWith(".locked")) { console.error("usage: node tools/lock_voice.mjs IN OUT.locked"); process.exit(2); }
  const pub = JSON.parse(readFileSync(join(ROOT, "assets", "voice-key.json"), "utf8"));
  writeFileSync(outp, await lockBytes(readFileSync(inp), pub));
  console.log("Locked " + inp + " -> " + outp);
}
