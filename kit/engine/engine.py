"""Frame engine for the Voz Vascaína documentary: backgrounds, sprites, items, compositing."""
import math, random, functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 1920, 1080, 30
RED = (213, 15, 31)
WHITE = (246, 244, 240)
OFF = (226, 219, 204)
GREY = (150, 148, 144)
DARK = (11, 11, 12)
INK = (38, 28, 20)
SEPIA = (196, 168, 120)

FONTS = {
    "anton": "/usr/share/fonts/truetype/google-fonts/ofl/anton/Anton-Regular.ttf",
    "xb": "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf",
    "black": "/usr/share/fonts/opentype/inter/Inter-Black.otf",
    "b": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "sb": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "m": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "serif": "/usr/share/fonts/truetype/google-fonts/ofl/crimsontext/CrimsonText-SemiBold.ttf",
    "serif_i": "/usr/share/fonts/truetype/google-fonts/ofl/crimsontext/CrimsonText-Italic.ttf",
    "serif_b": "/usr/share/fonts/truetype/google-fonts/ofl/crimsontext/CrimsonText-Bold.ttf",
    "type": "/usr/share/fonts/X11/Type1/c0419bt_.pfb",
    "type_b": "/usr/share/fonts/X11/Type1/c0583bt_.pfb",
}


@functools.lru_cache(None)
def font(name, size):
    return ImageFont.truetype(FONTS[name], size)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def ease_io(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- text sprites
def txt(text, f="anton", size=80, fill=WHITE, tracking=0, align="center", gap=None,
        shadow=True, maxw=None):
    """Render (multi-line) text to a tight RGBA sprite. Words wrapped at maxw."""
    fo = font(f, size)
    lines = []
    for para in text.split("\n"):
        if maxw is None:
            lines.append(para)
            continue
        cur = ""
        for w in para.split(" "):
            test = (cur + " " + w).strip()
            if _lw(test, fo, tracking) > maxw and cur:
                lines.append(cur)
                cur = w
            else:
                cur = test
        lines.append(cur)
    asc, desc = fo.getmetrics()
    lh = gap if gap else int((asc + desc) * 1.08)
    widths = [_lw(l, fo, tracking) for l in lines]
    pad = 24
    sw, sh = int(max(widths + [1])) + pad * 2, lh * len(lines) + pad * 2 - (lh - asc - desc)
    im = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        x = pad if align == "left" else (sw - widths[i]) / 2 if align == "center" else sw - pad - widths[i]
        y = pad + i * lh
        _draw_line(d, x, y, l, fo, fill, tracking)
    if shadow:
        a = im.getchannel("A").filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55))
        sh_im = Image.new("RGBA", im.size, (0, 0, 0, 0))
        sh_im.putalpha(a)
        out = Image.new("RGBA", im.size, (0, 0, 0, 0))
        out.alpha_composite(sh_im, (0, 4) if False else (0, 0))
        out.alpha_composite(im)
        im = out
    return im


def rich(parts, f="anton", size=80, tracking=0, shadow=True):
    """Single line with differently coloured parts: [(text, color), ...]."""
    fo = font(f, size)
    tw = sum(_lw(t, fo, tracking) for t, _ in parts)
    asc, desc = fo.getmetrics()
    pad = 24
    im = Image.new("RGBA", (int(tw) + pad * 2, asc + desc + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = pad
    for t, c in parts:
        _draw_line(d, x, pad, t, fo, c, tracking)
        x += _lw(t, fo, tracking)
    if shadow:
        a = im.getchannel("A").filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.55))
        s = Image.new("RGBA", im.size, (0, 0, 0, 0))
        s.putalpha(a)
        s.alpha_composite(im)
        im = s
    return im


def _lw(s, fo, tr):
    if not s:
        return 0
    if tr == 0:
        return fo.getlength(s)
    return sum(fo.getlength(c) for c in s) + tr * (len(s) - 1)


def _draw_line(d, x, y, s, fo, fill, tr):
    if tr == 0:
        d.text((x, y), s, font=fo, fill=fill)
        return
    for c in s:
        d.text((x, y), c, font=fo, fill=fill)
        x += fo.getlength(c) + tr


def stack(sprites, gap=0, align="center"):
    w = max(s.width for s in sprites)
    h = sum(s.height for s in sprites) + gap * (len(sprites) - 1)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    y = 0
    for s in sprites:
        x = (w - s.width) // 2 if align == "center" else 0
        im.alpha_composite(s, (x, y))
        y += s.height + gap
    return im


def hstack(sprites, gap=0):
    w = sum(s.width for s in sprites) + gap * (len(sprites) - 1)
    h = max(s.height for s in sprites)
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for s in sprites:
        im.alpha_composite(s, (x, (h - s.height) // 2))
        x += s.width + gap
    return im


def canvas(w, h):
    return Image.new("RGBA", (w, h), (0, 0, 0, 0))


def rect(w, h, fill, radius=0, outline=None, width=0):
    im = canvas(w, h)
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), radius=radius, fill=fill,
                                         outline=outline, width=width)
    return im


def label(text, size=30, fg=WHITE, bg=RED, f="xb", padx=26, pady=12, tracking=3):
    t = txt(text, f, size, fg, tracking=tracking, shadow=False)
    t = t.crop(t.getbbox())
    im = rect(t.width + padx * 2, t.height + pady * 2, bg)
    im.alpha_composite(t, (padx, pady))
    return im


def underline(sp, color=RED, h=8, gap=6):
    bb = sp.getbbox()
    im = canvas(sp.width, sp.height + gap + h)
    im.alpha_composite(sp)
    ImageDraw.Draw(im).rectangle((bb[0] + 4, bb[3] + gap, bb[2] - 4, bb[3] + gap + h), fill=color)
    return im


# ---------------------------------------------------------------- backgrounds
PADX, PADY = 110, 62


def _noise(h, w, scale, seed):
    rng = np.random.default_rng(seed)
    small = rng.random((max(2, h // scale), max(2, w // scale))).astype(np.float32)
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255.0


def _vignette(h, w, strength=0.75, power=2.2):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx, ny = (x - w / 2) / (w / 2), (y - h / 2) / (h / 2)
    r = np.sqrt(nx ** 2 * 0.9 + ny ** 2)
    return 1 - strength * np.clip(r / 1.25, 0, 1) ** power


def make_bg(kind, seed=1):
    h, w = H + PADY, W + PADX
    vig = _vignette(h, w)[..., None]
    fine = np.random.default_rng(seed).normal(0, 1, (h, w, 1)).astype(np.float32)
    if kind == "dark":
        base = np.array([14, 14, 16], np.float32)
        mott = _noise(h, w, 90, seed)[..., None]
        img = base * (0.75 + 0.5 * mott) * vig + fine * 2.0
        # faint diagonal sash
        y, x = np.mgrid[0:h, 0:w].astype(np.float32)
        dist = np.abs((x - w * 0.70) * 0.766 - (y - h * 0.5) * 0.643)
        band = np.clip(1 - np.abs(dist - 0) / 170, 0, 1)
        band = (dist < 160).astype(np.float32) * 9.0
        img = img + band[..., None] * vig
    elif kind == "sepia":
        base = np.array([40, 30, 20], np.float32)
        mott = _noise(h, w, 70, seed)[..., None]
        img = base * (0.7 + 0.6 * mott) * _vignette(h, w, 0.85)[..., None] + fine * 3.0
        # vertical film scratches
        rng = np.random.default_rng(seed + 7)
        for _ in range(14):
            xx = rng.integers(0, w)
            img[:, xx:xx + 1, :] += rng.uniform(4, 10)
    elif kind == "paper":
        base = np.array([226, 213, 187], np.float32)
        mott = _noise(h, w, 60, seed)[..., None]
        blot = _noise(h, w, 260, seed + 3)[..., None]
        img = base * (0.9 + 0.12 * mott) * (0.92 + 0.08 * blot) * _vignette(h, w, 0.42, 2.6)[..., None] + fine * 4.0
    elif kind == "grey":
        base = np.array([188, 188, 184], np.float32)
        mott = _noise(h, w, 60, seed)[..., None]
        img = base * (0.9 + 0.12 * mott) * _vignette(h, w, 0.5, 2.4)[..., None] + fine * 4.0
    elif kind == "red":
        base = np.array([120, 8, 16], np.float32)
        mott = _noise(h, w, 90, seed)[..., None]
        img = base * (0.75 + 0.45 * mott) * _vignette(h, w, 0.8)[..., None] + fine * 2.5
    elif kind == "black":
        img = np.zeros((h, w, 3), np.float32)
    else:
        raise ValueError(kind)
    return np.clip(img, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------- grain
def make_grain(n=8):
    out = []
    rng = np.random.default_rng(42)
    for _ in range(n):
        g = rng.integers(0, 256, (H, W), dtype=np.uint8)
        a = np.full((H, W), 6, np.uint8)
        out.append(Image.fromarray(np.dstack([g, g, g, a]), "RGBA"))
    return out


# ---------------------------------------------------------------- items
class Item:
    def __init__(self, t0, t1, spr, x=W // 2, y=H // 2, anim="fade", fin=0.6, fout=0.5,
                 dist=50, z=0, kb=0.0, anchor="c"):
        self.t0, self.t1, self.spr = t0, t1, spr
        self.x, self.y, self.anim, self.fin, self.fout = x, y, anim, fin, fout
        self.dist, self.z, self.kb, self.anchor = dist, z, kb, anchor
        self._cache = {}

    def sprite(self, tl):
        if callable(self.spr):
            return self.spr(tl, self.t1 - self.t0)
        return self.spr

    def draw(self, frame, t):
        if t < self.t0 or t >= self.t1:
            return
        tl = t - self.t0
        dur = self.t1 - self.t0
        pin = ease(tl / self.fin) if self.fin > 0 else 1.0
        pout = ease((dur - tl) / self.fout) if self.fout > 0 else 1.0
        a = min(pin, pout)
        if a <= 0.004:
            return
        spr = self.sprite(tl)
        if spr is None:
            return
        dx = dy = 0
        sc = 1.0
        if self.anim == "up":
            dy = (1 - pin) * self.dist
        elif self.anim == "down":
            dy = -(1 - pin) * self.dist
        elif self.anim == "left":
            dx = (1 - pin) * self.dist
        elif self.anim == "right":
            dx = -(1 - pin) * self.dist
        elif self.anim == "zoom":
            sc = 1.0 + 0.08 * (1 - pin)
        elif self.anim == "pop":
            sc = 0.82 + 0.18 * pin
        if self.kb:
            sc *= 1.0 + self.kb * (tl / max(dur, 0.01))
        if abs(sc - 1.0) > 0.002:
            nw, nh = max(1, int(spr.width * sc)), max(1, int(spr.height * sc))
            spr = spr.resize((nw, nh), Image.BILINEAR)
        if a < 0.996:
            al = spr.getchannel("A").point(lambda v, a=a: int(v * a))
            spr = spr.copy()
            spr.putalpha(al)
        if self.anchor == "c":
            px, py = int(self.x - spr.width / 2 + dx), int(self.y - spr.height / 2 + dy)
        elif self.anchor == "l":
            px, py = int(self.x + dx), int(self.y - spr.height / 2 + dy)
        else:  # top-left
            px, py = int(self.x + dx), int(self.y + dy)
        paste(frame, spr, px, py)


def paste(frame, spr, px, py):
    x0, y0 = max(px, 0), max(py, 0)
    x1, y1 = min(px + spr.width, W), min(py + spr.height, H)
    if x1 <= x0 or y1 <= y0:
        return
    if (x0, y0, x1, y1) != (px, py, px + spr.width, py + spr.height):
        spr = spr.crop((x0 - px, y0 - py, x1 - px, y1 - py))
    frame.alpha_composite(spr, (x0, y0))


def cached(fn):
    """Decorator for dynamic sprite fns keyed on a quantised state."""
    store = {}

    def wrap(key, *a):
        if key not in store:
            store[key] = fn(key, *a)
        return store[key]
    return wrap


# ---------------------------------------------------------------- renderer
class VReader:
    def __init__(self, path):
        self.path = path; self.p = None; self.next = -1; self.last = None
    def get(self, fi):
        import subprocess
        if self.p is None or fi != self.next:
            if self.p: self.p.kill()
            self.p = subprocess.Popen(["ffmpeg", "-v", "quiet", "-ss", f"{fi/FPS:.4f}", "-i", self.path, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE, bufsize=W*H*3*2)
            self.next = fi
        buf = self.p.stdout.read(W * H * 3)
        if len(buf) == W * H * 3:
            self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        self.next = fi + 1
        return self.last


class Timeline:
    def __init__(self, duration):
        self.duration = duration
        self.bgs = []      # (t0, kind, seed)
        self.items = []
        self.overlays = [] # full-frame callables(frame, t)

    def bg(self, t0, kind, seed=1):
        self.bgs.append((t0, kind, seed))

    def add(self, *a, **k):
        it = Item(*a, **k)
        self.items.append(it)
        return it

    def prepare(self):
        self.bgs.sort()
        self._bgcache = {}
        self.grain = make_grain()
        g = np.zeros((H, W, 4), np.uint8)
        ramp = np.clip((np.arange(H) - (H - 300)) / 300.0, 0, 1) ** 1.4 * 170
        g[..., 3] = ramp.astype(np.uint8)[:, None]
        self.shade = Image.fromarray(g, "RGBA")
        self.items.sort(key=lambda i: i.z)

    def _bgarr(self, kind, seed):
        k = (kind, seed)
        if k not in self._bgcache:
            self._bgcache[k] = make_bg(kind, seed)
        return self._bgcache[k]

    def _bg_at(self, idx, t):
        t0, kind, seed = self.bgs[idx]
        t1 = self.bgs[idx + 1][0] if idx + 1 < len(self.bgs) else self.duration
        arr = self._bgarr(kind, seed)
        p = min(max((t - t0) / max(t1 - t0, 0.1), 0.0), 1.0)
        dirx = 1 if idx % 2 == 0 else -1
        ox = int(PADX / 2 + dirx * (p - 0.5) * PADX * 0.9)
        oy = int(PADY / 2 + (p - 0.5) * PADY * 0.6 * (1 if idx % 3 else -1))
        ox = min(max(ox, 0), PADX); oy = min(max(oy, 0), PADY)
        return arr[oy:oy + H, ox:ox + W]

    def frame(self, fi):
        t = fi / FPS
        vr = getattr(self, "video_ranges", None)
        if vr:
            for f0, f1, mode in vr:
                if f0 <= fi < f1:
                    if not hasattr(self, "_vreader"):
                        self._vreader = VReader(self.video_path)
                    arr = self._vreader.get(fi)
                    if arr is not None:
                        k = 0.85 if mode == "key" else 0.62
                        base = (arr.astype(np.float32) * k).astype(np.uint8)
                        return self._compose(base, fi, t)
        idx = 0
        for i, (t0, _, _) in enumerate(self.bgs):
            if t0 <= t:
                idx = i
        base = self._bg_at(idx, t)
        XF = 0.5
        if idx + 1 < len(self.bgs) and self.bgs[idx + 1][0] - t < XF / 2:
            pass
        if idx > 0 and t - self.bgs[idx][0] < XF:
            prev = self._bg_at(idx - 1, t)
            a = ease_io((t - self.bgs[idx][0]) / XF)
            base = (prev.astype(np.float32) * (1 - a) + base.astype(np.float32) * a).astype(np.uint8)
        return self._compose(base, fi, t)

    def _compose(self, base, fi, t):
        frame = Image.fromarray(np.ascontiguousarray(base), "RGB").convert("RGBA")
        for it in self.items:
            it.draw(frame, t)
        frame.alpha_composite(self.shade)
        for ov in self.overlays:
            ov(frame, t)
        frame.alpha_composite(self.grain[(fi // 2) % len(self.grain)])
        return frame.convert("RGB")
