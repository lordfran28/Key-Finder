# The piano pages

How the voice-and-piano pages on the shelf were made. Nothing here runs on the site.

- `charts.py` reads each song's guitar arrangement page (its bars, chords, timing, where the voice sings) from the artifact pages saved during the conversation. `SONGS` lists them; the paths point at that conversation's working folder, so a new session has to save the pages again first.
- `arrange.py` turns a chart into the piano part: the bass in the left hand, four-note rootless voicings in the right (A and B forms, chosen so the hand moves least), a fill only where the voice rests at the end of a bar and at most one every six bars (eight in fast songs), and a few short tips.
- `piano.py` plays it with the Salamander Grand Piano samples (Alexander Holm, CC BY 3.0). Put the samples in `samples/` as `A0.wav`, `C1.wav`, `Ds1.wav`, `Fs1.wav` and so on; they come from the `Salamander` folder of github.com/Tonejs/audio, decoded from mp3.
- `page.py` writes the page: keyboard diagrams labelled with chord tones, "back to" for a voicing that returns, keys that light as they sound, the tracks.
- `build.py SLUG` does all of it for one song and writes `out/SLUG/`; `--no-audio` rewrites only the page. The singer's track is the guitar artifact's vocal mix with the guitar taken out, and goes up locked.
- `faure.py` is Après un rêve, taken note for note from the OpenScore Lieder score (CC0) instead of from a guitar page.
- `import_all.sh SLUG ...` puts built songs on the shelf with `tools/import_arrangement.py`.
- `art.py RAW.jpg NAME` makes a painting's light and dark files for `assets/art`.
