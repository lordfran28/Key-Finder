"""Key Finder's damask and title painting, made the way the sister sites made theirs.
Damask: Italian velvet panel, 17th century, The Met 229429 (open access), a black-and-white photograph,
mirrored into a wider piece and recoloured: ultramarine on ivory for light, blue on ebony for dark.
The title paintings are cut by heroes.py."""
import sys
from PIL import Image, ImageOps, ImageFilter
SRC_TEX = '/home/claude/valve-finder/assets/source/met-229429-velvet-panel-italian-17c.jpg'
OUT = '/home/claude/key-finder/assets/'

g = Image.open(SRC_TEX).convert('L').crop((70, 90, 770, 1090))   # the woven part, without the cut edge and the label
g = ImageOps.autocontrast(g, cutoff=1)
tile = Image.new('L', (g.width * 2, g.height))
tile.paste(g, (0, 0)); tile.paste(ImageOps.mirror(g), (g.width, 0))
tile = tile.resize((1400, int(1400 * tile.height / tile.width)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))

def duotone(L, ground, pattern, gamma=1.0):
    lut = []
    for v in range(256):
        t = (1 - v / 255) ** gamma          # dark velvet = pattern
        lut.append(tuple(round(ground[i] * (1 - t) + pattern[i] * t) for i in range(3)))
    r = L.point([c[0] for c in lut]); g_ = L.point([c[1] for c in lut]); b = L.point([c[2] for c in lut])
    return Image.merge('RGB', (r, g_, b))

duotone(tile, (238, 233, 223), (84, 108, 160), 1.15).save(OUT + 'textile-light.jpg', quality=84, optimize=True, progressive=True)
duotone(tile, (17, 16, 15), (44, 60, 98), 1.0).save(OUT + 'textile-dark.jpg', quality=84, optimize=True, progressive=True)

print('textile', tile.size)
