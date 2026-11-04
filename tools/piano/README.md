# The piano pages

How the voice-and-piano pages on the shelf were made. Nothing here runs on the site.

- `charts.py` reads each song's guitar arrangement page (its bars, chords, timing, where the voice sings) from the Fret Finder shelf (`/home/claude/fret-finder/songs`), or from the Key Finder page itself when the guitar page isn't there. `VOICES` lists the singer's mixes still at hand; a song without one keeps the singer's track it already has on the shelf.
- `arrange.py` turns a chart into the piano part for a beginner: the song's own chords played plainly (no 9ths, 11ths or 13ths; a major 7th under a sung root becomes a 6th), a shell in the left hand (root and 7th, or root and 5th; the bass alone under a slash chord), three close notes in the right hand (rootless on 7th and 6th chords, never four), chosen so the hand moves least, a fill only where the voice rests at the end of a bar and at most one every eight bars (twelve in fast songs), and a few short tips.
- `piano.py` plays it with the Salamander Grand Piano samples (Alexander Holm, CC BY 3.0). Put the samples in `samples/` as `A0.wav`, `C1.wav`, `Ds1.wav`, `Fs1.wav` and so on; they come from the `Salamander` folder of github.com/Tonejs/audio, decoded from mp3.
- `page.py` writes the page: keyboard diagrams labelled with chord tones, one per change ("continues" while a voicing keeps ringing; a voicing that comes back is drawn again), keys that light as they sound, the tracks.
- `build.py SLUG` does all of it for one song and writes `out/SLUG/`; `--no-audio` rewrites only the page. The singer's track is the guitar artifact's vocal mix with the guitar taken out, and goes up locked.
- `faure.py` is Après un rêve, taken note for note from the OpenScore Lieder score (CC0) instead of from a guitar page.
- `import_all.sh SLUG ...` puts built songs on the shelf with `tools/import_arrangement.py`.
- `design.py` makes the site's velvet (light and dark) from the Met velvet in Valve Finder's `assets/source`; `heroes.py DIR` cuts the title paintings of all three sites (Ragueneau's harpsichordist, Watteau's *Mezzetin*, Dou's *Trumpet Player*) from the originals in DIR.
