"""Synthesised music bed + SFX (booms, whooshes, typewriter) -> work/bed.wav"""
import sys, wave
import numpy as np
sys.path.insert(0, "/home/claude/doc")
import scenes

SR = 44100
DUR = scenes.DURATION
N = int(DUR * SR)
rng = np.random.default_rng(7)
t = np.arange(N) / SR


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x)


# ---------------- pad: i–VI–III–VII in D minor, 8 s per chord
def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


chords = [[50, 53, 57, 62], [46, 50, 53, 58], [53, 57, 60, 65], [48, 52, 55, 60]]  # Dm Bb F C
CH = 8.0
pad = np.zeros(N)
for ci in range(int(DUR / CH) + 2):
    ch = chords[ci % 4]
    s0 = ci * CH - 2.0
    s1 = s0 + CH + 4.0
    a, b = max(0, int(s0 * SR)), min(N, int(s1 * SR))
    if a >= b:
        continue
    tt = t[a:b] - s0
    env = np.clip(tt / 2.5, 0, 1) * np.clip((s1 - s0 - tt) / 2.5, 0, 1)
    env = env ** 1.5
    seg = np.zeros(b - a)
    for m in ch:
        f = midi(m)
        for det in (-0.12, 0.0, 0.11):
            ff = f * 2 ** (det / 12)
            ph = rng.uniform(0, 6.28)
            seg += np.sin(2 * np.pi * ff * tt + ph) + 0.35 * np.sin(4 * np.pi * ff * tt + ph) + 0.12 * np.sin(6 * np.pi * ff * tt)
    pad[a:b] += seg * env
pad = onepole_lp(pad, 900)
pad /= np.abs(pad).max()
sub = np.sin(2 * np.pi * midi(26) * t) * 0.35 + np.sin(2 * np.pi * midi(38) * t) * 0.15
music = pad * 0.8 + sub * 0.5
music *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.07 * t)

# section dynamics
dyn = np.ones(N)
def ramp_region(t0, t1, level, fade=2.0):
    a, b = int(t0 * SR), int(t1 * SR)
    seg = np.ones(b - a)
    seg *= level
    fi = int(fade * SR)
    seg[:fi] = np.linspace(1, level, fi) if fi < len(seg) else seg[:fi]
    seg[-fi:] = np.linspace(level, 1, fi)
    dyn[a:b] *= seg
ramp_region(355.5, 419.2, 0.55)  # quieter under the letter
ramp_region(0, 4.2, 0.35, 1.0)
music *= dyn

# tension pulse (heartbeat) under the exclusion + stadium build
def pulse(t0, t1, bpm=62, amp=0.7):
    out = np.zeros(N)
    step = 60 / bpm
    x = t0
    while x < t1:
        for off, g in ((0, 1.0), (0.22, 0.6)):
            a = int((x + off) * SR)
            L = int(0.35 * SR)
            if a + L < N:
                tt = np.arange(L) / SR
                out[a:a + L] += np.sin(2 * np.pi * (48 + 30 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9) * g
        x += step
    return out * amp
music += pulse(300.9, 336.8) + pulse(499.2, 518.3, 76, 0.55)

# fade in/out
music[: int(1.0 * SR)] *= np.linspace(0, 1, int(1.0 * SR))
fo = int(4 * SR)
music[N - fo:] *= np.linspace(1, 0, fo)
music = music / np.abs(music).max() * 0.5

# ---------------- SFX
sfx = np.zeros(N)
for b0 in scenes.BOOMS:
    a = int(b0 * SR)
    L = int(2.2 * SR)
    if a + L >= N:
        L = N - a - 1
    tt = np.arange(L) / SR
    f = 30 + 40 * np.exp(-tt * 4)
    ph = 2 * np.pi * np.cumsum(f) / SR
    boom = np.sin(ph) * np.exp(-tt * 2.2)
    nz = onepole_lp(rng.normal(0, 1, L), 400) * np.exp(-tt * 10) * 3
    sfx[a:a + L] += (boom + nz) * 0.9
for w0 in scenes.WHOOSH:
    L = int(0.9 * SR)
    a = int((w0 - 0.15) * SR)
    if a < 0 or a + L >= N:
        continue
    tt = np.arange(L) / SR
    env = np.sin(np.pi * tt / 0.9) ** 2
    nz = rng.normal(0, 1, L)
    hp = nz - onepole_lp(nz, 600)
    sfx[a:a + L] += onepole_lp(hp, 3500) * env * 0.5
clicks = sorted(scenes.CLICKS)
last = -1
for c0 in clicks:
    if c0 - last < 0.035:
        continue
    last = c0
    a = int(c0 * SR)
    L = int(0.05 * SR)
    if a + L >= N:
        continue
    tt = np.arange(L) / SR
    g = rng.uniform(0.5, 1.0)
    k = rng.normal(0, 1, L) * np.exp(-tt * 260) + 0.6 * np.sin(2 * np.pi * rng.uniform(1700, 2600) * tt) * np.exp(-tt * 180)
    sfx[a:a + L] += k * 0.22 * g
sfx = sfx / max(np.abs(sfx).max(), 1e-6) * 0.7

# stereo
L_ch = music * 0.9 + sfx
R_ch = np.roll(music, int(0.012 * SR)) * 0.9 + sfx
st = np.stack([L_ch, R_ch], 1)
st = st / np.abs(st).max() * 0.9
pcm = (st * 32767).astype(np.int16)
with wave.open("/home/claude/doc/work/bed.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("bed ok", len(clicks), "clicks", len(scenes.BOOMS), "booms")
