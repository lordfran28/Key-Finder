"""Chord charts for the piano pages, read from the guitar arrangement pages (the artifacts' own data):
bars in playing order with their start times, chords and beats, where the voice sings and rests, the
sung pitch classes per bar where the page has them, and the words for songs whose words are free."""
import re, json, os, sys
SP = '/tmp/claude-0/-home-claude/32eff81e-a259-5caa-a171-2530c104e7b0/scratchpad'
FF = '/home/claude/fret-finder/songs'
# slug: (title, page, voice mix, guitar track the mix was built on, words are free, source artifact)
SONGS = {
 'it-had-to-be-you': ('It Had to Be You', 'imp/ihtby', None, FF + '/it-had-to-be-you/ihtby-guitar.mp3', True, 'https://claude.ai/artifact/6BtQavYFM9hSJ2Me5QAkE2'),
 'misty': ('Misty', 'imp/misty', 'imp/misty/misty-voice.mp3', FF + '/misty/misty-guitar.mp3', False, 'https://claude.ai/artifact/N4AM8jZCR5tufb2WFAgDvf'),
 'my-one-and-only-love': ('My One and Only Love', 'imp/moaol', 'imp/moaol/moaol-voice.mp3', FF + '/my-one-and-only-love/moaol-guitar.mp3', False, 'https://claude.ai/artifact/AGyGzPVkPp5yz1it26wRYz'),
 'ive-got-a-crush-on-you': ('I’ve Got a Crush on You', 'imp/crush', 'imp/crush/crush-all.mp3', FF + '/ive-got-a-crush-on-you/crush-tpt.mp3', False, 'https://claude.ai/artifact/Uo7oWw6UJnXGMNGmXApb9b'),
 'where-or-when': ('Where or When', 'cand/wow', 'cand/wow/wow-voice.mp3', 'cand/wow/wow-guitar.mp3', False, 'https://claude.ai/artifact/4xSnXgbBPrH6hvFGfZGUm7'),
 'ill-be-seeing-you': ('I’ll Be Seeing You', 'cand2/ibsy', 'cand2/ibsy/ibsy-voice.mp3', 'cand2/ibsy/ibsy-guitar.mp3', False, 'https://claude.ai/artifact/8FytBUK6Ta89MjaKt6pvNh'),
 'youd-be-so-nice-to-come-home-to': ('You’d Be So Nice to Come Home To', 'cand2/ybsn', 'cand2/ybsn/ybsn-voice.mp3', 'cand2/ybsn/ybsn-guitar.mp3', False, 'https://claude.ai/artifact/Xs4UBHmPTGzgXD8rndhAUj'),
 'i-cover-the-waterfront': ('I Cover the Waterfront', 'cand2/icw', 'cand2/icw/icw-voice.mp3', 'cand2/icw/icw-guitar.mp3', False, 'https://claude.ai/artifact/Vbmmcu3AE5EgetcHuRxr98'),
 'how-deep-is-the-ocean': ('How Deep Is the Ocean', 'cand2/hd', 'cand2/hd/hd-full-guide.mp3', 'cand2/hd/hd-full-guitar.mp3', False, 'https://claude.ai/artifact/XC2r8KEnJCSD4D8HzFP9fN'),
 'everything-happens-to-me': ('Everything Happens to Me', 'cand2/eh', 'cand2/eh/eh-full-guide.mp3', 'cand2/eh/eh-full-guitar.mp3', False, 'https://claude.ai/artifact/8rASRS49dTVzJyEhfQgZAn'),
 'ive-never-been-in-love-before': ('I’ve Never Been in Love Before', 'cand2/nb', 'cand2/nb/nb-full-guide.mp3', 'cand2/nb/nb-full-guitar.mp3', False, 'https://claude.ai/artifact/PA5ZtDeeuHR1JiM8kjeeB9'),
 'i-cant-get-started': ('I Can’t Get Started', 'cand2/icgs', 'cand2/icgs/icgs-voice.mp3', 'cand2/icgs/icgs-guitar.mp3', False, 'https://claude.ai/artifact/4wTiuPBh3qXXjJAeB2uGEo'),
 'but-not-for-me': ('But Not for Me', 'cand2/bnfm', 'cand2/bnfm/bnfm-voice.mp3', 'cand2/bnfm/bnfm-guitar.mp3', False, 'https://claude.ai/artifact/Et3rUJfVQxukan9xbpkZaN'),
 'i-wish-you-love': ('I Wish You Love', 'cand2/iwyl', 'cand2/iwyl/iwyl-voice.mp3', 'cand2/iwyl/iwyl-guitar.mp3', False, 'https://claude.ai/artifact/LwRpi6qtVjrNyw3Q6pKZM3'),
 'thats-all': ('That’s All', 'cand/tha', 'cand/tha/tha-voice.mp3', 'cand/tha/tha-guitar.mp3', False, 'https://claude.ai/artifact/1bwSv2Hjm4goNH2XRjuwZ3'),
 'youll-never-know': ('You’ll Never Know', 'cand/ynk', 'cand/ynk/ynk-voice.mp3', 'cand/ynk/ynk-guitar.mp3', False, 'https://claude.ai/artifact/87sUJ8po8da8QaeSFo6KTe'),
 'isnt-it-romantic': ('Isn’t It Romantic', 'cand/iir', 'cand/iir/iir-voice.mp3', 'cand/iir/iir-guitar.mp3', False, 'https://claude.ai/artifact/Fv5e5rY8ZFiMc2Zbyt4JnD'),
 'the-christmas-song': ('The Christmas Song', 'cand/xmas', 'cand/xmas/xmas-voice.mp3', 'cand/xmas/xmas-guitar.mp3', False, 'https://claude.ai/artifact/MgvWpLNf6gsyST6f5Un7zH'),
 'white-christmas': ('White Christmas', 'cand/wc', 'cand/wc/wc-voice.mp3', 'cand/wc/wc-guitar.mp3', False, 'https://claude.ai/artifact/Co2r35HDPKiTgdmCfS5Fyz'),
 'dont-get-around-much-anymore': ('Don’t Get Around Much Anymore', 'cand/dga', None, 'cand/dga/dga-guitar.mp3', False, 'https://claude.ai/artifact/NcuGWZPc7DFzZhQrGXmEKX'),
 'for-all-we-know': ('For All We Know', 'cand2/fawk', 'cand2/fawk/fawk-with-hartman.mp3', 'cand2/fawk/fawk-guitar.mp3', False, 'https://claude.ai/artifact/ADVd6hX4bytUQvND41D3Ce'),
 'what-a-difference-a-day-made': ('What a Diff’rence a Day Made', 'cand2/wad', 'cand2/wad/wad-long-voice.mp3', 'cand2/wad/wad-long-guitar.mp3', False, 'https://claude.ai/artifact/Prio4YakfMdJKrbtph8KXV'),
 'i-wonder-whos-kissing-her-now': ('I Wonder Who’s Kissing Her Now', 'imp/khn', 'imp/khn/iwonder-full-dean.mp3', FF + '/i-wonder-whos-kissing-her-now/iwonder-full.mp3', True, 'https://claude.ai/artifact/2UiV3kZd44SBgjFsJicj9t'),
 'seria-fantastico': ('Sería fantástico', 'imp/seria', 'imp/seria/serrat-voice.mp3', FF + '/seria-fantastico/serrat-guitar.mp3', False, 'https://claude.ai/artifact/9ngaXqjVvuoUwYW611g9ax'),
 'barquito-de-papel': ('Barquito de papel', 'imp/bq', 'imp/bq/bq-with-serrat.mp3', 'imp/bq/bq-guitar.mp3', False, 'https://claude.ai/artifact/41Ke1uXfPjvGgNGxdb4nAW'),
 'it-keeps-you-runnin': ('It Keeps You Runnin’', 'cand/ikyr', 'cand/ikyr/ikyr-voice.mp3', 'cand/ikyr/ikyr-guitar.mp3', False, 'https://claude.ai/artifact/8C4CDBrJq9CNP47sdmbmZs'),
 'ya-vas-lyubil': ('Я вас любил', 'imp/yvl', 'imp/yvl/yvl-voice.mp3', FF + '/ya-vas-lyubil/yvl-guitar.mp3', True, 'https://claude.ai/artifact/7Z9p2XX6TiXmub6vQkxUDp'),
 'are-you-lonesome-tonight': ('Are You Lonesome Tonight', 'imp/lonesome', 'imp/lonesome/are-you-lonesome-tonight-full.mp3', None, False, 'https://claude.ai/artifact/FZTia6X1K3LYFfWMrf3inx'),
 'love-me-tender': ('Love Me Tender', 'imp/tender', 'imp/tender/love-me-tender-full.mp3', None, False, 'https://claude.ai/artifact/TKwKKst9Md8KPRZwodnxNL'),
 'somos-novios': ('Somos novios', 'cand/sn', 'cand/sn/sn-voice.mp3', 'cand/sn/sn-guitar.mp3', False, 'https://claude.ai/artifact/AEVF3mrrucvpyya1obNeEd'),
 'no-me-platiques-mas': ('No me platiques más', 'cand/nmp', 'cand/nmp/nmp-voice.mp3', 'cand/nmp/nmp-guitar.mp3', False, 'https://claude.ai/artifact/CV3UTWqvY2TFkiqdmifch3'),
 'dormir-contigo': ('Dormir contigo', 'cand/dc', 'cand/dc/dc-voice.mp3', 'cand/dc/dc-guitar.mp3', False, 'https://claude.ai/artifact/PqbnioxyBcECrg7sgGQDQk'),
 'in-over-my-head': ('In Over My Head', 'cand/iomh', 'cand/iomh/iomh-voice.mp3', 'cand/iomh/iomh-guitar.mp3', False, 'https://claude.ai/artifact/QwWvtJjfrzE3RTfnZtRM6N'),
 'so-i-could-find-my-way': ('So I Could Find My Way', 'cand/enya', 'cand/enya/enya-voice.mp3', 'cand/enya/enya-guitar.mp3', False, 'https://claude.ai/artifact/8zyE7XMxeH6dqbRKSadnXu'),
 'cloudy': ('Cloudy', 'cand2/cloudy', 'cand2/cloudy/cloudy-voice.mp3', 'cand2/cloudy/cloudy-guitar.mp3', False, 'https://claude.ai/artifact/L26FbKBMXk5PMciNapffRy'),
 'glinka-ya-pomnyu': ('Glinka – Я помню чудное мгновенье', 'imp/irm', 'imp/irm/irm-voice.mp3', FF + '/glinka-ya-pomnyu/irm-guitar.mp3', True, 'https://claude.ai/artifact/YJ1nqyjFFETmyfsKdKjG16'),
 'you-dont-mess-around-with-jim': ('You Don’t Mess Around with Jim', 'imp/jim', 'imp/jim/jim-voice.mp3', FF + '/you-dont-mess-around-with-jim/jim-guitar.mp3', False, 'https://claude.ai/artifact/64rNZEHDwajoH9L7h8ZSu1'),
 'ochi-chyornye': ('Очи чёрные (Dark Eyes)', FF + '/ochi-chyornye', 'oci-voice.mp3', 'oci-guitar.mp3', True, 'https://claude.ai/artifact/Dtod3AhL34hbdMYfsuDcQG'),
}

def norm(c):
    c = c.replace('♭', 'b').replace('♯', '#').replace('°', 'dim').replace('ø', 'm7b5').replace('Δ', 'maj7')
    return c.strip()

def kit_chart(s):
    D = json.loads(re.search(r'\nconst DATA = (.*?);?\n', s).group(1).rstrip(';'))
    song = D.get('song', {})
    T = max(D['tracks'], key=lambda t: len(t['bars']))      # the full version
    mel = {}
    cm = re.search(r'<script id="cp-data" type="application/json">(.*?)</script>', s, re.S)
    if cm:
        cp = json.loads(cm.group(1))
        for o in cp.get('opts', []):
            if o.get('mel'): mel.setdefault(str(o.get('bar')), o['mel'])
    fw = {}
    for part in D.get('form') or []:
        for fb in (part.get('bars') or []) if isinstance(part, dict) else []:
            if fb.get('w'): fw.setdefault(str(fb.get('n')), fb['w'])
    bars = []; last = None
    for b in T['bars']:
        chords = []; t = 0.0
        for it in b.get('items', []):
            k = it[0]; d = 0.0; name = None
            if k == 'C': name, d = it[1], float(it[3])
            elif k == 'K': name, d = it[1], float(sum(h[0] for h in it[3]))
            elif k == 'Y': name, d = it[1], float(sum(it[3]))
            elif k == 'T': name, d = it[1], float(it[3])
            elif k in ('R', 'P'): d = float(sum(it[2]))
            elif k == 'W': d = float(it[1])
            if d <= 0: continue
            if name:
                if chords and chords[-1]['c'] == norm(name): chords[-1]['beats'] += d
                else: chords.append(dict(c=norm(name), beats=d, at=t))
            else:
                if chords: chords[-1]['beats'] += d
                elif last: chords.append(dict(c=last, beats=d, at=t))
            t += d
        if chords: last = chords[-1]['c']
        bars.append(dict(label=b['label'], sec=b.get('sec', ''), start=b.get('start'), chords=chords, beats=t,
                         voc=b.get('voc', ''), mel=mel.get(str(b['label']), []), words=b.get('w') or fw.get(str(b['label']), '')))
    return dict(key=song.get('key'), tonic=song.get('tonic'), meter=song.get('meter', 4), bpm=song.get('bpm'), bars=bars)

def pt_chart(s):
    m = re.search(r'<script id="pt-data" type="application/json">(.*?)</script>', s, re.S)
    if m:
        P = json.loads(m.group(1)); src = P['bars']; bpm = P.get('bpm')
        get = lambda b: (str(b.get('n')), b.get('part', ''), b.get('start'))
    else:
        P = json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', s, re.S).group(1))
        src = P['bars']; bpm = P.get('bpm')
        get = lambda b: (str(b.get('n')), b.get('sec', ''), b.get('t'))
    bars = []
    for b in src:
        n, sec, st = get(b); t = 0.0; ch = []
        words = ' '.join(w for sg in b['segs'] for w in (sg.get('w') or []))
        for sg in b['segs']:
            ch.append(dict(c=norm(sg['c']), beats=float(sg['beats']), at=t)); t += float(sg['beats'])
        bars.append(dict(label=n, sec=sec, start=st, chords=ch, beats=t, voc='', mel=[], words=words))
    return dict(key=None, tonic=None, meter=None, bpm=bpm, bars=bars)

def chart(slug):
    title, page, vmix, gtr, free, src = SONGS[slug]
    s = open(os.path.join(SP, page, 'index.html'), encoding='utf-8').read()
    C = kit_chart(s) if '\nconst DATA = ' in s else pt_chart(s)
    C.update(slug=slug, title=title, words_free=free, source=src,
             voice=os.path.join(SP, vmix) if vmix else None,
             guitar=(gtr if (gtr and gtr.startswith('/')) else (os.path.join(SP, gtr) if gtr else None)))
    if not C['key']:
        hd = re.search(r'([A-G][♭♯b#]?) (major|minor)', s)
        if hd: C['key'] = hd.group(1).replace('♭', 'b').replace('♯', '#') + ' ' + hd.group(2)
    # bar ends from the next bar's start
    for i, b in enumerate(C['bars']):
        nx = next((x['start'] for x in C['bars'][i + 1:] if x.get('start') is not None), None)
        if b.get('start') is not None and nx is not None and nx > b['start']: b['end'] = nx
    for i, b in enumerate(C['bars']):
        if 'end' not in b and b.get('start') is not None:
            spb = 60.0 / (C['bpm'] or 80)
            b['end'] = b['start'] + max(b['beats'], 1) * spb
    return C

if __name__ == '__main__':
    os.makedirs('charts', exist_ok=True)
    for slug in (sys.argv[1:] or SONGS):
        try:
            C = chart(slug)
        except Exception as e:
            print('FAIL', slug, repr(e)); continue
        json.dump(C, open(f'charts/{slug}.json', 'w'), ensure_ascii=False, indent=0)
        nb = len(C['bars']); nc = sum(len(b['chords']) for b in C['bars'])
        missing = sum(1 for b in C['bars'] if b.get('start') is None)
        names = sorted({c['c'] for b in C['bars'] for c in b['chords']})
        print(f"{slug:34} key={C['key']!s:10} bpm={C['bpm']!s:5} meter={C['meter']} bars={nb} chords={nc} no-start={missing} mel={sum(1 for b in C['bars'] if b['mel'])} words={sum(1 for b in C['bars'] if b['words'])}")
