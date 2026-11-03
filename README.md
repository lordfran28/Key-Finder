# Key Finder

The sister of Fret Finder and Valve Finder, for the piano. It holds the voice-and-piano arrangements we make together. Each song has its own page, with keyboard diagrams in place of sheet music.

It lives at **https://lordfran28.github.io/Key-Finder/**. GitHub Pages serves it from `main`, `/ (root)` (Settings → Pages → Deploy from a branch).

## Songs

Each song is a folder in `songs/` holding its page, its audio and a small `song.json`. Claude puts a song there with `tools/import_arrangement.py`. After you push, the list on the site updates itself a minute or two later.

## The singer key

It's the same key as Fret Finder's. A phone or computer that already has it on Fret Finder has it here too. To put it on another device, open the owner page (`…/Key-Finder/#owner`) and paste it, or scan *Connect your phone* from a device that already has it.

## Paintings

Put each painting in `assets/art` as two files, `<name>-light.webp` and `<name>-dark.webp`:

- `music-lesson`: the top of the page (Vermeer, *The Music Lesson*)
- `seated-virginal`: under the songs (Vermeer, *Lady Seated at a Virginal*)
- `standing-virginal`: the owner page (Vermeer, *Lady Standing at a Virginal*)

A painting that isn't there yet doesn't show at all, and its credit stays off the page until it arrives.

## Credits

- Johannes Vermeer, *The Music Lesson*, *Lady Seated at a Virginal* and *Lady Standing at a Virginal*. Public domain.
- EB Garamond and IM Fell French Canon, under the SIL Open Font License (the licences are in `assets/fonts`). QR codes by qrcode-generator (MIT).
