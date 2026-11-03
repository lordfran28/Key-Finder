# Key Finder

The sister of Fret Finder and Valve Finder, for the piano. It holds the voice-and-piano arrangements we make together. Each song has its own page, with keyboard diagrams in place of sheet music.

It lives at **https://lordfran28.github.io/Key-Finder/**. GitHub Pages serves it from `main`, `/ (root)` (Settings → Pages → Deploy from a branch).

## Songs

Each song is a folder in `songs/` holding its page, its audio and a small `song.json`. Claude puts a song there with `tools/import_arrangement.py`. After you push, the list on the site updates itself a minute or two later.

## The singer key

It's the same key as Fret Finder's. A phone or computer that already has it on Fret Finder has it here too. To put it on another device, open the owner page (`…/Key-Finder/#owner`) and paste it, or scan *Connect your phone* from a device that already has it.

## The look

The same as Fret Finder and Valve Finder: a framed title with a Vermeer set into a 17th-century silk, songs on parchment cards, and a band of the same silk at the foot. Fret Finder is red, Valve Finder brass; Key Finder is ivory and ebony with Vermeer's blue. `tools/piano/design.py` made the velvet (`assets/textile-light.jpg`, `assets/textile-dark.jpg`) and the title painting (`assets/virginal-vermeer.jpg`).

## Credits

- Johannes Vermeer, *Lady Seated at a Virginal*, The National Gallery, London. Public domain.
- Velvet panel, Italian, 17th century, The Metropolitan Museum of Art, [229429](https://www.metmuseum.org/art/collection/search/229429). Public domain (Met Open Access). Mirrored and recoloured: blue on ivory, and blue on ebony.
- Piano sound: the Salamander Grand Piano by Alexander Holm, CC BY 3.0.
- EB Garamond and IM Fell French Canon, under the SIL Open Font License (the licences are in `assets/fonts`). QR codes by qrcode-generator (MIT).
