#!/usr/bin/env python3
"""Put a piano arrangement page made in conversation onto the Key Finder shelf.

    python3 tools/import_arrangement.py PAGE.html SLUG "Title" [--key "B♭ major"]
        [--file NAME=PATH ...] [--locked NAME.mp3.locked=PATH ...] [--drop-alt]
        [--source URL] [--added ISO-DATE]

Writes songs/SLUG/index.html (the page with Key Finder's look and a way back to the songs), copies
the media files it uses next to it, and writes songs/SLUG/song.json for the song list.

--key is the key the song is set in, as the library should show it ("B♭ major", "C minor").

--drop-alt removes the page's second audio track (audio_alt), for example a mix with a record's
own vocal, which mustn't go on a public site in the open.

--locked puts a track with a record's own singer on the page locked (see assets/voice.js): PATH is the
mp3, NAME is what the page's data calls it and must end in ".mp3.locked". It plays only on devices
where the owner entered the singer key; everywhere else its button is hidden.

Piano pages light their own keys as the notes sound, so nothing like Fret Finder's ring.js is added.
"""
import argparse, datetime, html as htmllib, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shelf_voice

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("page")
    ap.add_argument("slug")
    ap.add_argument("title")
    ap.add_argument("--key", default="", help='the key it is set in, e.g. "B♭ major"')
    ap.add_argument("--file", action="append", default=[], help="NAME=PATH of a file the page uses")
    ap.add_argument("--drop-alt", action="store_true")
    ap.add_argument("--locked", action="append", default=[], help="NAME.mp3.locked=PATH of a singer's track")
    ap.add_argument("--source", default="")
    ap.add_argument("--added", default="")
    a = ap.parse_args()

    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", a.slug):
        sys.exit("The slug must be lower-case letters, digits and dashes.")
    out = os.path.join(ROOT, "songs", a.slug)
    os.makedirs(out, exist_ok=True)

    meta_path = os.path.join(out, "song.json")
    meta = {}
    if os.path.exists(meta_path):
        try:
            meta = json.load(open(meta_path, encoding="utf-8"))
        except ValueError:
            meta = {}
    key = a.key or meta.get("key", "")

    html = open(a.page, encoding="utf-8").read()
    if a.drop_alt:
        html, n = re.subn(r'"audio_alt"\s*:\s*"[^"]*"', '"audio_alt":""', html)
        print("Second audio track removed from %d place(s)." % n)

    # Key Finder's look goes in the head; a way back to the songs, over a band of keys, at the top of the body.
    mark = " · ".join(x for x in [key, "voice and piano"] if x)
    mark = mark[:1].upper() + mark[1:]
    shelf = '<link rel="stylesheet" href="../../assets/shelf.css">'
    bar = ('<header class="kf-shelf"><a href="../../">&larr; Key Finder</a><span class="kf-mark">%s</span>'
           '</header>' % htmllib.escape(mark))
    html = html.replace(shelf, "")
    html = re.sub(r'<header class="(?:kf|ff)-shelf">.*?</header>', "", html, flags=re.S)
    html = html.replace('<script src="../../assets/ring.js" defer></script>', "")
    if "</head>" in html:
        html = html.replace("</head>", shelf + "</head>", 1)
    else:
        html = shelf + html
    m = re.search(r"<body[^>]*>", html)
    html = html[:m.end()] + bar + html[m.end():] if m else bar + html
    # The singer's track, locked: playable only on the owner's devices.
    html = shelf_voice.mark_locked(shelf_voice.add_voice_script(html))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    used = []
    for spec in a.file:
        name, _, path = spec.partition("=")
        if not name or not path or "/" in name or name.startswith("."):
            sys.exit("Bad --file %r" % spec)
        if name.endswith(".locked"):
            sys.exit("%s is a singer's track: pass it with --locked NAME=PATH-to-the-mp3." % name)
        if a.drop_alt and name not in html:
            print("Skipped %s: the page no longer uses it." % name)
            continue
        shutil.copyfile(path, os.path.join(out, name))
        used.append(name)

    for spec in a.locked:
        name, _, path = spec.partition("=")
        if not name.endswith(".mp3.locked") or not path or "/" in name:
            sys.exit("Bad --locked %r" % spec)
        if name not in html:
            sys.exit("The page doesn't use %s; add it to the page's track list first." % name)
        shelf_voice.lock(path, os.path.join(out, name))
        used.append(name)

    meta.update({
        "title": a.title,
        "kind": "arrangement",
        "instrument": "piano",
        "files": ["index.html"] + used,
    })
    if key:
        meta["key"] = key
    if a.source:
        meta["source"] = a.source
    meta.setdefault("addedAt", a.added or datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("songs/%s: %s, %d media file(s)." % (a.slug, a.title, len(used)))


if __name__ == "__main__":
    main()
