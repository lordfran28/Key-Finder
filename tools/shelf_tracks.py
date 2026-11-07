"""What import_arrangement.py does to a page's tracks. Key Finder has no keys: a track with a record's own
singer, or with the tune of a song still under copyright, can't be on a public site, so it stays on the
song's private page. The shelf page keeps the open tracks and links to the private page.

    strip_locked(html)      takes out every ".locked" track (and the old voice.js) from a page
    singer_link(html, url)  puts a "With the singer" link to the private page in the bar at the top
"""
import re

VOICE_TAG = re.compile(r'<script src="\.\./\.\./assets/voice\.js"></script>')
L = r'"[^"\[\]]*\.locked"'
S = r'"[^"\[\]]*"'


def strip_locked(html):
    html = VOICE_TAG.sub("", html)
    for pair in (r'\[\s*' + S + r'\s*,\s*' + L + r'\s*\]', r'\[\s*' + L + r'\s*,\s*' + S + r'\s*\]'):
        html = re.sub(r',\s*' + pair, "", html)          # an entry after another
        html = re.sub(pair + r'\s*,\s*', "", html)        # the first entry
        html = re.sub(pair, "", html)                    # the only entry
    html = re.sub(r'("audio_alt"\s*:\s*)' + L, r'\1""', html)
    html = re.sub(r'<button\b[^>]*\bdata-src="[^"]*\.locked"[^>]*>.*?</button>', "", html, flags=re.S)
    return html


def singer_link(html, url):
    html = re.sub(r'<a class="kf-sing"[^>]*>.*?</a>', "", html)
    link = '<a class="kf-sing" href="%s" target="_blank" rel="noopener">With the singer</a>' % url
    return html.replace('<span class="kf-mark">', link + '<span class="kf-mark">', 1)
