#!/usr/bin/env python3
"""Put a piano arrangement page made in conversation onto the Key Finder shelf.

    python3 tools/import_arrangement.py PAGE.html SLUG "Title" [--key "B♭ major"]
        [--file NAME=PATH ...] [--drop-alt] [--source URL [--singer]] [--added ISO-DATE]

Writes songs/SLUG/index.html (the page with Key Finder's look and a way back to the songs), copies
the media files it uses next to it, and writes songs/SLUG/song.json for the song list.

--key is the key the song is set in, as the library should show it ("B♭ major", "C minor").

--drop-alt removes the page's second audio track (audio_alt), for example a mix with a record's
own vocal, which mustn't go on a public site in the open.

Key Finder has no keys. Any ".locked" track a page lists is taken out: a mix with a record's own
singer can't be public, so it stays on the private page. --singer (with --source) puts a "With the
singer" link to that page in the bar at the top. --locked is still accepted, and ignored.

Piano pages light their own keys as the notes sound, so nothing like Fret Finder's ring.js is added.
"""
import argparse, datetime, html as htmllib, json, os, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shelf_tracks

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
    ap.add_argument("--locked", action="append", default=[], help="ignored: Key Finder has no keys")
    ap.add_argument("--singer", action="store_true", help="the private page (--source) has the singer: link to it")
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
    # No keys: a track with a record's singer stays on the private page, linked from the top bar.
    html = shelf_tracks.strip_locked(html)
    if (a.singer or a.locked) and a.source:
        html = shelf_tracks.singer_link(html, a.source)
    # Slower tracks for practising along: a row of speeds under every player, the pitch unchanged.
    speed = '<script src="../../assets/speed.js" defer></script>'
    html = html.replace(speed, "")
    html = html.replace("</body>", speed + "</body>", 1) if "</body>" in html else html + speed
    # The music stand, the note of the days the song was played, and the way to the shape book.
    practice = '<script src="../../assets/practice.js" defer></script>'
    html = html.replace(practice, "")
    html = html.replace("</body>", practice + "</body>", 1) if "</body>" in html else html + practice
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

    used = []
    for spec in a.file:
        name, _, path = spec.partition("=")
        if not name or not path or "/" in name or name.startswith("."):
            sys.exit("Bad --file %r" % spec)
        if name.endswith(".locked"):
            continue
        if a.drop_alt and name not in html:
            print("Skipped %s: the page no longer uses it." % name)
            continue
        shutil.copyfile(path, os.path.join(out, name))
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
