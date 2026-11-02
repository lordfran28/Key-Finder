"""The singer's track on shelf pages: what import_arrangement.py (and one-off fixes) do to a page so a
locked track (NAME.mp3.locked, made with tools/lock_voice.mjs) plays on the owner's devices and stays
out of sight everywhere else. See assets/voice.js.

    add_voice_script(html)  loads assets/voice.js first thing in <head>
    mark_locked(html)       gives every button for a ".locked" track the data-locked attribute,
                            in the button templates the arrangement pages use and in plain markup
    lock(src, dst)          locks one audio file with the owner's public key
"""
import os, re, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = '<script src="../../assets/voice.js"></script>'

# the button templates of the page kits, and what each becomes
TEMPLATES = [
    # versions list: ([label, file], i)
    ('data-src="${i}" aria-pressed="${i === 0}">${esc(l)}</button>',
     'data-src="${i}"${/\\.locked$/.test(f) ? \' data-locked\' : \'\'} aria-pressed="${i === 0}">${esc(l)}</button>'),
    # main / alt pair
    ('<button type="button" data-src="alt" aria-pressed="false">',
     '<button type="button" data-src="alt"${/\\.locked$/.test(T.audio_alt) ? \' data-locked\' : \'\'} aria-pressed="false">'),
    # audio list of [file, label] as a[0], a[1]
    ('data-src="${esc(a[0])}" aria-pressed="${i===0}">',
     'data-src="${esc(a[0])}"${/\\.locked$/.test(a[0]) ? \' data-locked\' : \'\'} aria-pressed="${i===0}">'),
    # audio list: ([src, lab], i)
    ('data-src="${src}" aria-pressed="${i === 0}">',
     'data-src="${src}"${/\\.locked$/.test(src) ? \' data-locked\' : \'\'} aria-pressed="${i === 0}">'),
]


def add_voice_script(html):
    html = html.replace(TAG, "")
    m = re.search(r"<head[^>]*>", html)
    return html[:m.end()] + TAG + html[m.end():] if m else TAG + html


def mark_locked(html):
    for a, b in TEMPLATES:
        html = html.replace(a, b)
    # plain markup: <button ... data-src="x.locked" ...>
    return re.sub(r'(<button\b[^>]*\bdata-src="[^"]*\.locked")(?![^>]*\bdata-locked)', r"\1 data-locked", html)


def lock(src, dst):
    if not dst.endswith(".locked"):
        raise ValueError("a locked file's name ends in .locked")
    subprocess.run(["node", os.path.join(HERE, "lock_voice.mjs"), src, dst], check=True, stdout=subprocess.DEVNULL)
