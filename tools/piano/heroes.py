"""Title paintings for Key Finder and Fret Finder: a man playing each instrument, cut around him the way the
sites cut their Vermeers. python3 heroes.py DIR  (DIR holds ragueneau.jpg and mezzetin.jpg)"""
import sys
from PIL import Image
D = sys.argv[1]
JOBS = [  # source, crop box, longest side, output
    ('ragueneau.jpg', (40, 20, 864, 900), 1300, '/home/claude/key-finder/assets/harpsichord-ragueneau.jpg'),
    ('mezzetin.jpg', (290, 430, 1260, 1680), 1300, '/home/claude/fret-finder/assets/mezzetin-watteau.jpg'),
]
for src, box, side, out in JOBS:
    im = Image.open(f'{D}/{src}').convert('RGB').crop(box)
    if max(im.size) > side:
        im.thumbnail((side, side), Image.LANCZOS)
    im.save(out, quality=86, optimize=True, progressive=True)
    print(out, im.size)
