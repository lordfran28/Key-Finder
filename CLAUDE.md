# Key Finder: working instructions

Draft 1, 2 November 2026. Built from Fret Finder's shelf; still to be revised with the owner before it is treated as settled.

These are the standing instructions for anyone, person or Claude, changing this site. Read them before touching `index.html` or adding a song.

## What the site is for

The owner is a baritone who sings and plays the piano at the same time. He is learning the piano through songs and doesn't read sheet music. Key Finder is the shelf for the voice-and-piano arrangements made with him in conversation with Claude. Each song is a page he can play and sing from:

- **Keyboard diagrams, not sheet music.** Each diagram shows the keys to press, labelled with chord tones (R, 3, 5, 7, 9, 11, 13, altered tones), not finger numbers.
- **Rootless voicings** (and shells where they fit), so the hands move as little as possible from chord to chord. Each diagram says which kind of voicing it is.
- **The singing on top.** Every bar shows where the voice sings, with each chord change against the word it falls on, and the words sit under each diagram so he always knows where he is.
- **Keys light up as they sound** in the track. Piano pages do this themselves; nothing like Fret Finder's `ring.js` is added here.
- **Sound to check it by ear,** with the voice in by default where possible (locked, see below).
- **Tips only when they are clear and immediately useful at the keyboard.** No theory lessons, no general advice, nothing he has to read twice.
- Repertoire: mostly old jazz standards and showtunes with great harmony and good lyrics, in keys for a baritone.

He learns by playing along with the tracks slowly, day after day, until the shapes become habit. The site helps with that in three ways, all kept on his device:

- **The music stand.** A *Music stand* button in every song's player opens a full-screen view for a phone or tablet on the piano: the chord he's on, very large, with its keys lighting, any fill under it on keys the same size, the words for public-domain songs, and the next chord smaller, all following the track. It has play, previous and next chord, the track choice and the speeds, and keeps the screen awake.
- **The shape book** (`#shapes`, or `#shapes/SLUG` from a song's "Practise them in the shape book" link). Every shape in the songs (a chord with its left- and right-hand keys) once. Each day it gives him a few by name ("C♯m7 · Shell + rootless · top note B", with the song and bar); he plays, shows the keys (which also plays the moment from the song's piano track) and says *Got it* or *Not yet*. A shape that came back right returns after 1, 3, 7, 14, 30 and 60 days; one that didn't returns at the end of the round and the next day. New shapes come five a day from the song he's learning, in the order the song plays them. Below, every shape of that song, or of all songs with the most used first, marked new, learning or known (right on two different days).
- **The library shows where he is.** Under each song: the key and how many shapes it has, and once he knows some, how many are new to him; for songs he has played, when, at what speed, up from what, and on how many days. The songs can be put in order A to Z, by fewest new shapes (the next song to learn) or by last played.

## The owner's rules for arranging

These come from his own corrections over many arrangements (on guitar, piano and trumpet). They outrank anything an algorithm or a habit prefers.

**Layout**
- The full arrangement goes at the top, bar 1, bar 2 and on, in playing order, with no repeats or jumps left for the player to follow. Explanations, road maps and alternatives go at the bottom.
- A diagram means a change, so never repeat one. A voicing that keeps going gets one diagram; the bars after it show none. A voicing that comes back after a different one is drawn again in full; never replace it with a name like "back to Dm9". Each part opens with its own diagrams.
- Only runs and scales get numbers (the order they're played in).

**Arranging**
- Never stuffed. Add a run, an inner line or an extra chord only where it's truly beautiful.
- Never simplify. Don't drop or thin a part on the assumption it's too hard; don't assume what he can or can't play. Write the real part.
- It must be easy to play while singing. When two choices are equal, take the one with the fuller, nicer sound that is also easier to reach.
- Follow the song's real chord changes. Reharmonize only where it still sounds like the song.
- Lines from the record (bass moves, horn and string lines) go in only where they fit, mostly where the voice rests.
- His suggestions ("add a walking bass here") are pointers, not literal requirements; use the whole toolbox where it fits without being told each time.

**Keys**
- Keep the key he asks for, in baritone range.

## The shelf

- Each arrangement is a folder `songs/<slug>/` holding the page (`index.html`), the audio it uses, and `song.json`: `title`, `kind` ("arrangement"), `instrument` ("piano"), `key`, `files`, `source` (the artifact it came from) and `addedAt`.
- Put one there with:

  `python3 tools/import_arrangement.py PAGE.html SLUG "Title" --key "E♭ major" --source ARTIFACT-URL --file NAME=PATH ... [--locked NAME.mp3.locked=PATH ...] [--drop-alt]`

  It adds Key Finder's look (`assets/shelf.css`, which only sets the page's colour and type variables), a bar at the top like Fret Finder's ("← Key Finder", then the key and "voice and piano"), `assets/voice.js` first thing in `<head>`, and `assets/speed.js` and `assets/practice.js` at the end; it marks the buttons of locked tracks `data-locked`. Running it again on the same slug replaces the page and keeps the date and key.
- **Slower tracks.** `assets/speed.js` puts a row of speeds (100% down to 50%) inside every track player on a song page. The pitch stays the same, the keys keep lighting with the slower track, and each song remembers its own speed on the device (`kf.speed:` + the page's path), so the owner can play along slowly and raise it day by day. The import tool adds it to every page. Fret Finder has the same file; keep the two in step.
- **Practising.** `assets/practice.js` reads the page's own data (`<script id="kf-data">`: bars, segments, events) for the music stand, and notes how long the track played each day and at what speed. The library loads it too, for its keyboard drawing and those notes. It needs nothing from the arranger beyond that data, so pages rebuilt by `tools/piano` keep working.
- `.github/scripts/song_index.py` lists every such folder in `songs/index.json` and writes the shape book, `songs/shapes.json`, from the songs' pages: each shape once (chord, form, keys, tones, note names) with the songs it's in and where it first sounds in each song's piano track, and each song's shapes in the order they come. The *Song list* workflow runs it on every push that touches `songs/`. Run it locally too before committing, so both are right at once.
- The library lists the songs A to Z (or by fewest new shapes, or last played) with the key and the number of shapes under each title, and links straight to the page. A *Shapes* card at the top says how many are due today. A search box appears from six songs up. It has no way to add a song.
- What a device keeps: `kf.speed:` + page path (speed), `kf.played:` + page path (seconds played per day and speed), `kf.shapes` (each shape's run of right answers and the day it's due), `kf.newtoday`, `kf.learning`, `kf.sort`. Nothing leaves the device.
- Titles of classical pieces start with the composer: "Bach – Prelude and Fugue, BWV 867". The library sets the composer in small capitals.
- Keyboard diagrams should colour their keys with `--key-white`, `--key-black` and `--key-edge`, which `shelf.css` sets for light and dark. Drawn with `--ink`, black keys turn ivory in dark mode. `shelf.css` also sets the variables Fret Finder's pages use (`--bg`, `--surface`, `--ink`, `--accent`, `--voice` and the rest). When the first piano pages arrive, check them against it and add any variable they use that isn't there.

## Copyright and the singer's track

The same rules as Fret Finder.

- The site is public. Never put a record's own audio (a vocal mix, a stem) or copyrighted lyrics on it in the open; `--drop-alt` removes a page's second audio track. Pages for songs still under copyright need their lyrics taken out, or a private way to serve them, before they go up.
- **The singer's track goes up locked.** Every song that had a track with the singer on its artifact gets it on the shelf too. Add it to the page's track list under the name `NAME.mp3.locked` (after the open tracks, never first) and pass `--locked NAME.mp3.locked=PATH`. `tools/lock_voice.mjs` encrypts it to the public key in `assets/voice-key.json`; `assets/voice.js` plays it on devices where the owner entered the singer key, and hides its button everywhere else.
- Before a page goes up, take out anything copyrighted: a record's vocal or stem in the open (also as a track choice in the page's data; locked is fine), the sung melody of a song under copyright (including a compendium's "you sing" notes), and the owner's own recordings of other people's records (those can go up locked too). Earlier-version iframes go too unless each one is checked.
- **One key for both sites.** `assets/voice-key.json`, `assets/voice-check.locked`, `assets/voice.js` and `tools/lock_voice.mjs` are copies of Fret Finder's, so the key he already has opens the tracks here. Keep them in step with Fret Finder and don't change the locked format (`FFV1`, info string "fret-finder voice"), or his key stops working. The private half of the key is never in this repository or in any page.
- The key is kept in the browser under `ff.voicekey`, the same name as Fret Finder. Both sites are served from lordfran28.github.io, the same origin, so entering it on either owner page puts it on both, and removing it on one removes it on both. Anything Key Finder stores for itself takes a `kf.` prefix so the two sites never step on each other.
- The owner page (`#owner`) has only the singer key and *Connect your phone*: a QR code for the link `#connect=` + base64url of `{"v": KEY}`. Opening that link checks the key against `voice-check.locked`, saves it, and replaces the address with `#owner` so the key doesn't stay in the address bar or the history.

## Look and paintings

- **The same design as Fret Finder and Valve Finder, with a slight variance.** The owner wants the three to read as brothers. Same layout, type and pieces: one music-stand column; a framed title (eyebrow "For the piano", the name, a short line) with an old painting of a man playing the instrument cut into a 17th-century silk on the right; a faint silk behind the whole page; songs on parchment cards; the owner page with "← Songs"; credits at the foot over a band of the same silk. When a sister site changes its look, follow it here.
- The variance is the colour and the pictures. Fret Finder is madder red, Valve Finder brass; Key Finder is ivory and ebony with Vermeer's ultramarine. Its silk is a 17th-century Italian velvet (The Met 229429) recoloured blue on ivory and blue on ebony; its title painting is Abraham Ragueneau's *Portrait of a Man at a Harpsichord* (1670, Frans Hals Museum). `tools/piano/design.py` makes the velvet and `tools/piano/heroes.py` cuts the title paintings for Key Finder and Fret Finder.
- **The title paintings show men here and on Fret Finder.** The owner wanted a man playing the instrument: Ragueneau's harpsichordist here, Watteau's *Mezzetin* on Fret Finder. Valve Finder keeps Vermeer's Clio, by his choice.
- EB Garamond and IM Fell French Canon, served from `assets/fonts`. Light and dark follow the device.
- Still to come: the faint paintings that stand behind the songs on the sister sites (Fret Finder's Baroque guitarists, Valve Finder's trumpeters). Here they will be players at keyboards, once their files are in.
- Only real, public-domain paintings, photographs and historical pieces. Never newly drawn or generated imagery: the owner says it looks AI-made.
- Phone first: it must work at 390 px wide with no sideways scroll.

## How work is done here

- **No build step.** The site is one page, `index.html`, plus assets. Keep it that way unless there's a strong reason.
- **Keep instructions off the site.** No setup steps, notes or explanations on the pages; the owner calls that bloat. Page text is short and plain.
- **Look before pushing.** Check the library, the owner page and any changed song page in a headless browser at 390 px and 1280 px, light and dark.
- **Write commit messages for the player.** Say in plain words what changed for him, not which function moved.
- Each site is its own repository. Don't change Fret Finder or Valve Finder from here.

## Where it stands (5 November 2026)

- Built: the library, the owner page, the song-page look, the import tool and the song-list workflow; slower tracks; the music stand, the shape book and the library's progress (5 November).
- 39 songs, built with the tools in `tools/piano/` (see its README).
- The look now matches the sister sites (see Look and paintings).
- Live at https://lordfran28.github.io/Key-Finder/ (repository lordfran28/Key-Finder, Pages from `main`, root).
