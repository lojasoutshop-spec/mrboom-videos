"""SRT -> ASS karaoke (white text, red sweep), chunked for readability."""
import re

SRT = "/home/claude/doc/film/work/legenda.srt"
OUT = "/home/claude/doc/film/work/karaoke.ass"
MAXCH = 44  # max characters per caption line


def ts(s):
    h, m, rest = s.split(":")
    sec, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


def ass_t(t):
    cs = int(round(t * 100))
    h, cs = divmod(cs, 360000)
    m, cs = divmod(cs, 6000)
    s, cs = divmod(cs, 100)
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"


def weight(w):
    core = re.sub(r"[^\wÀ-ÿ]", "", w)
    k = max(len(core), 1) + 1.5
    if w.endswith((".", ":", "?", "!", '."', '?"')):
        k += 4
    elif w.endswith((",", ";", '",')):
        k += 2
    return k


blocks = open(SRT, encoding="utf-8").read().strip().split("\n\n")
segs = []
for b in blocks:
    lines = b.strip().split("\n")
    a, z = lines[1].split(" --> ")
    text = " ".join(lines[2:]).strip()
    text = text.lstrip("—").strip()
    segs.append((ts(a), ts(z), text))

events = []
for a, z, text in segs:
    words = text.split()
    ws = [weight(w) for w in words]
    tot = sum(ws)
    dur = z - a
    times = []
    t = a
    for w, k in zip(words, ws):
        d = dur * k / tot
        times.append((w, t, d))
        t += d
    # chunk into lines <= MAXCH, prefer breaking after punctuation
    chunks, cur, clen = [], [], 0
    for item in times:
        w = item[0]
        if cur and clen + 1 + len(w) > MAXCH:
            chunks.append(cur)
            cur, clen = [], 0
        cur.append(item)
        clen += len(w) + (1 if clen else 0)
        if w.endswith((".", ":", "?", "!")) and clen > 18:
            chunks.append(cur)
            cur, clen = [], 0
    if cur:
        chunks.append(cur)
    # merge tiny orphan chunks into their neighbour
    def clen_of(c):
        return sum(len(x[0]) + 1 for x in c)
    merged = []
    for ch in chunks:
        if merged and clen_of(ch) < 14 and clen_of(merged[-1]) + clen_of(ch) <= MAXCH + 12:
            merged[-1] = merged[-1] + ch
        else:
            merged.append(ch)
    chunks = merged
    for ch in chunks:
        st = ch[0][1]
        en = ch[-1][1] + ch[-1][2]
        parts = []
        for w, t0, d in ch:
            parts.append(f"{{\\kf{max(int(round(d * 100)), 1)}}}{w} ")
        events.append((st, en, "".join(parts).rstrip()))

# small lead-in so the line appears slightly before the first word
out = []
for i, (st, en, txt) in enumerate(events):
    s0 = max(0, st - 0.08)
    e0 = en + 0.25
    if i + 1 < len(events):
        e0 = min(e0, events[i + 1][0] - 0.1)
    lead = int(round((st - s0) * 100))
    out.append(f"Dialogue: 0,{ass_t(s0)},{ass_t(e0)},Kara,,0,0,0,,{{\\k{lead}}}{txt}")

header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kara,Inter ExtraBold,62,&H001A1AE8,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,4.5,2.5,2,120,120,62,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
open(OUT, "w", encoding="utf-8").write(header + "\n".join(out) + "\n")
print(len(segs), "segments ->", len(events), "caption lines; last end", segs[-1][1])
