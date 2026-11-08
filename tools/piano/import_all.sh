#!/bin/bash
# Put every built piano page in tools/piano/out onto the Key Finder shelf.
set -e
cd /home/claude/key-finder
for slug in "$@"; do
  d=/home/claude/key-finder/tools/piano/out/$slug/
  [ -f "$d/meta.json" ] && [ -f "$d/index.html" ] || continue
  python3 - "$d" "$slug" <<'EOF' > /tmp/kf_args.$$
import json, sys, os
d, slug = sys.argv[1], sys.argv[2]
m = json.load(open(os.path.join(d, 'meta.json')))
args = [os.path.join(d, 'index.html'), slug, m['title'], '--key', m.get('key') or '']
if m.get('source'): args += ['--source', m['source']]
names = [t[1] for t in m.get('tracks') or []] or [f for f in os.listdir(d) if f.endswith('.mp3')]
for t in (m.get('tracks') or []):
    name, locked = t[1], t[2]
    if locked:
        args += ['--locked', name + '=' + os.path.join(d, name[:-len('.locked')])]
    else:
        args += ['--file', name + '=' + os.path.join(d, name)]
if not m.get('tracks'):
    for f in sorted(os.listdir(d)):
        if f.endswith('.mp3'): args += ['--file', f + '=' + os.path.join(d, f)]
print('\0'.join(args), end='')
EOF
  mapfile -d '' args < /tmp/kf_args.$$; rm -f /tmp/kf_args.$$
  python3 tools/import_arrangement.py "${args[@]}"
done
python3 .github/scripts/song_index.py
