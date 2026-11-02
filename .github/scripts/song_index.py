#!/usr/bin/env python3
"""Writes songs/index.json: the list of songs Key Finder shows.

Every folder under songs/ holding an index.html and a song.json is one arrangement made in
conversation; its page is the folder's index.html. song.json gives the title, the key and the date.
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
