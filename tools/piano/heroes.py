"""Title paintings for the three Finder sites: a man playing each instrument, cut around him the way the
sites cut their Vermeers. python3 heroes.py DIR  (DIR holds traballesi.jpg, mezzetin.jpg, dou.jpg)"""
import sys
from PIL import Image
D = sys.argv[1]
JOBS = [  # source, crop box, longest side, output
    ('traballesi.jpg', (200, 330, 2750, 3600), 1300, '/home/claude/key-finder/assets/virginal-traballesi.jpg'),
    ('mezzetin.jpg', (290, 430, 1260, 1680), 1300, '/home/claude/fret-finder/assets/mezzetin-watteau.jpg'),
    ('dou.jpg', (50, 220, 870, 1060), 1000, '/home/claude/valve-finder/assets/trumpet-player-dou.jpg'),
]
for src, box, side, out in JOBS:
    im = Image.open(f'{D}/{src}').convert('RGB').crop(box)
    if max(im.size) > side:
        im.thumbnail((side, side), Image.LANCZOS)
    im.save(out, quality=86, optimize=True, progressive=True)
    print(out, im.size)
