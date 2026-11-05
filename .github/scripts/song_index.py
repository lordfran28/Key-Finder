#!/usr/bin/env python3
"""Writes songs/index.json, the list of songs Key Finder shows, and songs/shapes.json, the shape book.

Every folder under songs/ holding an index.html and a song.json is one arrangement made in
conversation; its page is the folder's index.html. song.json gives the title, the key and the date.

The shape book gathers every hand shape (a chord with its left- and right-hand keys) from the songs'
pages, once, with the songs it comes in, where it first sounds in each song's piano track, and each
song's shapes in the order they first come.
"""
import datetime, json, os, re, subprocess, unicodedata

ROOT = "songs"
OUT = os.path.join(ROOT, "index.json")


def first_added(path):
    try:
        out = subprocess.run(["git", "log", "--diff-filter=A", "--follow", "--format=%aI", "--", path],
                             capture_output=True, text=True, check=True).stdout.split()
        if out:
            return out[-1]
    except Exception:
        pass
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def utc(stamp):
    # a plain day becomes noon of that day, so it reads as the same day in America and in Europe
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(stamp or "")):
        return str(stamp) + "T12:00:00Z"
    try:
        d = datetime.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
        if d.tzinfo is None:
            d = d.replace(tzinfo=datetime.timezone.utc)
        return d.astimezone(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "song"


DATA = re.compile(r'<script id="kf-data" type="application/json">(.*?)</script>', re.S)
TRACK = re.compile(r'<div class="sw"[^>]*>\s*<button[^>]*data-src="([^"]+)"')


def page_shapes(html):
    """The song's bars and events from its page, or None when the page carries none."""
    m = DATA.search(html)
    if not m:
        return None
    try:
        return json.loads(m.group(1).replace("<\\/", "</"))
    except ValueError:
        return None


def shape_book(songs):
    shapes, book = {}, {}
    for s in songs:
        try:
            with open(os.path.join(s["page"], "index.html"), encoding="utf-8") as f:
                html = f.read()
        except OSError:
            continue
        d = page_shapes(html)
        if not d or not d.get("bars"):
            continue
        tm = TRACK.search(html)
        when = {}
        for e in d.get("events", []):
            t, off, seg = e[0], e[3], e[4]
            a = when.setdefault(seg, [t, off])
            a[0], a[1] = min(a[0], t), max(a[1], off)
        order = []
        for i, b in enumerate(d["bars"]):
            for g in b.get("segs", []):
                lh, rh = g.get("lh") or [], g.get("rh") or []
                if not rh and not lh:
                    continue
                sid = "%s|%s|%s" % (g["c"], ".".join(map(str, lh)), ".".join(map(str, rh)))
                if sid in order:
                    continue
                order.append(sid)
                sh = shapes.get(sid)
                if not sh:
                    tones = g.get("tones") or {}
                    sh = shapes[sid] = {"c": g["c"], "f": g.get("form") or "", "lh": lh, "rh": rh,
                                        "t": [tones.get(str(m), "") for m in lh + rh],
                                        "n": [re.sub(r"\d+$", "", x) for x in (g.get("names") or [])], "in": []}
                t0, t1 = when.get(g.get("same") or g["id"]) or when.get(g["id"]) or [b["start"], b["end"]]
                sh["in"].append([s["id"], i, str(b.get("n", i + 1)), round(t0, 2), round(min(t1, t0 + 2.6), 2)])
        book[s["id"]] = {"track": s["page"] + tm.group(1) if tm else "", "shapes": order}
    return {"songs": book, "shapes": shapes}


def write_if_changed(path, data, label):
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n"
    try:
        with open(path, encoding="utf-8") as f:
            if f.read() == text:
                print("%s unchanged." % label)
                return
    except OSError:
        pass
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Wrote %s." % label)


def main():
    songs, used = [], set()
    os.makedirs(ROOT, exist_ok=True)
    for folder, dirs, files in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if not d.startswith("."))
        if folder == ROOT or "song.json" not in files or "index.html" not in files:
            continue
        try:
            with open(os.path.join(folder, "song.json"), encoding="utf-8") as f:
                meta = json.load(f) or {}
        except (OSError, ValueError):
            meta = {}
        rel = folder.replace(os.sep, "/")
        sid = slug(rel[len(ROOT) + 1:])
        while sid in used:
            sid += "-2"
        used.add(sid)
        entry = {
            "id": sid,
            "page": rel + "/",
            "title": str(meta.get("title") or os.path.basename(folder)),
            "kind": "arrangement",
            "instrument": str(meta.get("instrument") or "piano"),
            "addedAt": utc(meta.get("addedAt") or first_added(os.path.join(folder, "song.json"))),
        }
        if meta.get("key"):
            entry["key"] = str(meta["key"])
        songs.append(entry)
        dirs[:] = []
    songs.sort(key=lambda s: (s["title"].casefold(), s["page"]))

    book = shape_book(songs)
    write_if_changed(os.path.join(ROOT, "shapes.json"), book, "the shape book (%d shapes)" % len(book["shapes"]))

    try:
        with open(OUT, encoding="utf-8") as f:
            if json.load(f).get("songs") == songs:
                print("Song list unchanged (%d songs)." % len(songs))
                return
    except (OSError, ValueError, AttributeError):
        pass
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"app": "Key Finder", "generatedAt": now, "songs": songs}, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print("Wrote %d songs." % len(songs))


if __name__ == "__main__":
    main()
