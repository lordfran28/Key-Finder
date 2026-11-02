"""Key Finder paintings: python3 art.py RAW.jpg NAME -> assets/art/NAME-light.webp and NAME-dark.webp.
Light: the painting as it is, a touch warmer so it sits on the ivory page. Dark: the same, dimmed and
softened so it doesn't glare on the near-black page."""
import sys
from PIL import Image, ImageEnhance

src, name = sys.argv[1], sys.argv[2]
out = '/home/claude/key-finder/assets/art/'
im = Image.open(src).convert('RGB')
if max(im.size) > 1400:
    im.thumbnail((1400, 1400), Image.LANCZOS)
r, g, b = im.split()
warm = Image.merge('RGB', (r.point(lambda v: min(255, v * 1.02)), g, b.point(lambda v: v * 0.97)))
light = ImageEnhance.Color(warm).enhance(0.92)
light.save(out + name + '-light.webp', 'WEBP', quality=82, method=6)
dark = ImageEnhance.Brightness(light).enhance(0.8)
dark = ImageEnhance.Contrast(dark).enhance(0.92)
dark.save(out + name + '-dark.webp', 'WEBP', quality=82, method=6)
print(name, im.size)
