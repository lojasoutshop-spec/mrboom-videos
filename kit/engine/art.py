"""Hand-drawn illustration sprites (no external images)."""
import math, random, textwrap
from PIL import Image, ImageDraw, ImageFilter
from engine import *


def soft_shadow(im, blur=18, alpha=0.6, off=(0, 10)):
    a = im.getchannel("A").filter(ImageFilter.GaussianBlur(blur)).point(lambda v: int(v * alpha))
    out = canvas(im.width + 80, im.height + 80)
    s = canvas(im.width, im.height)
    s.putalpha(a)
    out.alpha_composite(s, (40 + off[0], 40 + off[1]))
    out.alpha_composite(im, (40, 40))
    return out


def cross_pattee(size, color=RED):
    im = canvas(size, size)
    d = ImageDraw.Draw(im)
    c = size / 2
    inner, outer, L = size * 0.09, size * 0.34, size * 0.48
    for ang in range(4):
        pts = [(inner, -inner * 0.2), (L, -outer), (L, outer), (inner, inner * 0.2)]
        rot = []
        for x, y in pts:
            a = math.radians(ang * 90)
            rot.append((c + x * math.cos(a) - y * math.sin(a), c + x * math.sin(a) + y * math.cos(a)))
        d.polygon(rot, fill=color)
    d.ellipse((c - inner * 1.4, c - inner * 1.4, c + inner * 1.4, c + inner * 1.4), fill=color)
    return im


def jersey():
    S = 2
    im = canvas(700 * S, 660 * S)
    d = ImageDraw.Draw(im)
    pts = [(255, 40), (145, 78), (25, 225), (112, 300), (172, 255), (172, 630), (528, 630),
           (528, 255), (588, 300), (675, 225), (555, 78), (445, 40), (405, 82), (350, 95), (295, 82)]
    pts = [(x * S, y * S) for x, y in pts]
    d.polygon(pts, fill=(20, 20, 22))
    d.line(pts + [pts[0]], fill=(92, 92, 98), width=5 * S, joint="curve")
    # polo collar
    col = [(255, 40), (295, 82), (350, 95), (405, 82), (445, 40), (420, 30), (350, 70), (280, 30)]
    d.polygon([(x * S, y * S) for x, y in col], fill=WHITE)
    d.line([(350 * S, 95 * S), (350 * S, 150 * S)], fill=(92, 92, 98), width=4 * S)
    for yb in (112, 136):
        d.ellipse(((344) * S, yb * S, 356 * S, (yb + 12) * S), fill=(200, 200, 200))
    cr = cross_pattee(150 * S)
    im.alpha_composite(cr, (int(275 * S), int(265 * S)))
    im = im.resize((700, 660), Image.LANCZOS)
    return soft_shadow(im, 30, 0.8)


def silhouette(color=WHITE, w=104):
    S = 2
    im = canvas(w * S, int(w * 1.62) * S)
    d = ImageDraw.Draw(im)
    hw = w * S
    d.ellipse((hw * 0.29, 0, hw * 0.71, hw * 0.42), fill=color)
    d.rounded_rectangle((hw * 0.06, hw * 0.48, hw * 0.94, im.height + hw * 0.4), radius=int(hw * 0.36), fill=color)
    return im.resize((w, int(w * 1.62)), Image.LANCZOS)


def x_mark(size=90, color=RED, width=12):
    im = canvas(size, size)
    d = ImageDraw.Draw(im)
    d.line((8, 8, size - 8, size - 8), fill=color, width=width)
    d.line((size - 8, 8, 8, size - 8), fill=color, width=width)
    return im


def skyline():
    """Rio silhouette: Corcovado, Urca and Sugarloaf over the bay."""
    w, h = 1920, 520
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    far = (58, 44, 31, 255)
    near = (30, 23, 16, 255)
    # back range with Corcovado peak
    pts = [(0, 330), (120, 300), (260, 250), (360, 180), (420, 70), (440, 60), (470, 95), (560, 210),
           (700, 260), (860, 300), (1000, 320), (1920, 345), (1920, h), (0, h)]
    d.polygon(pts, fill=far)
    d.rectangle((435, 40, 445, 62), fill=far)
    d.rectangle((424, 47, 456, 52), fill=far)
    # Urca + Sugarloaf
    def dome(cx, base, rx, top):
        pts = []
        for i in range(41):
            a = math.pi * i / 40
            x = cx - rx * math.cos(a)
            y = base - (base - top) * (math.sin(a) ** 0.55)
            pts.append((x, y))
        return pts
    d.polygon(dome(1260, 360, 150, 250) + [(1410, h), (1110, h)], fill=near)
    d.polygon(dome(1500, 360, 130, 95) + [(1630, h), (1370, h)], fill=near)
    d.line((1290, 262, 1478, 112), fill=(90, 70, 50, 255), width=2)
    # water
    d.rectangle((0, 360, w, h), fill=(22, 17, 12, 255))
    rng = random.Random(3)
    for i in range(60):
        y = rng.randint(372, h - 10)
        x = rng.randint(0, w)
        d.line((x, y, x + rng.randint(40, 160), y), fill=(70, 55, 38, 255), width=2)
    return im


def stairs(active):
    w, h = 1640, 560
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    labels = ["TERCEIRA DIVISÃO", "SEGUNDA DIVISÃO", "SÉRIE B · 1922", "ELITE · 1923"]
    for i in range(4):
        x0 = 20 + i * 400
        top = 470 - i * 120
        fill = RED if i == active else (34, 34, 38)
        if i < active:
            fill = (70, 70, 76)
        d.rectangle((x0, top, x0 + 390, h), fill=fill)
        d.rectangle((x0, top, x0 + 390, top + 6), fill=WHITE if i <= active else (90, 90, 96))
        t = txt(labels[i], "xb", 30, WHITE if i <= active else (130, 130, 136), tracking=2, shadow=False)
        im.alpha_composite(t, (int(x0 + 195 - t.width / 2), top - 70))
    return im


def stands(n_frac, seed=5):
    w, h = 1500, 420
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    rows = 6
    rng = random.Random(seed)
    dots = []
    for r in range(rows):
        y0 = 40 + r * 60
        inset = (rows - r) * 30
        d.polygon([(inset, y0 + 52), (w - inset, y0 + 52), (w - inset + 30, y0 + 60), (inset - 30, y0 + 60)],
                  fill=(46, 46, 52))
        x = inset + 8
        while x < w - inset - 8:
            dots.append((x + rng.uniform(-3, 3), y0 + 30 + rng.uniform(-3, 3), rng.random()))
            x += 19
    for x, y, k in dots:
        if k < n_frac:
            col = WHITE if rng.random() > 0.18 else RED
            d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=col)
            d.rectangle((x - 8, y + 6, x + 8, y + 22), fill=(col[0] // 2, col[1] // 2, col[2] // 2))
    return im


def facade():
    S = 2
    w, h = 1360, 560
    im = canvas(w * S, h * S)
    d = ImageDraw.Draw(im)
    L = OFF
    lw = 5 * S

    def R(x0, y0, x1, y1, fill=None, outline=L):
        d.rectangle((x0 * S, y0 * S, x1 * S, y1 * S), fill=fill, outline=outline, width=lw)

    def arch(x0, y0, x1, y1):
        r = (x1 - x0) / 2
        d.rectangle((x0 * S, (y0 + r) * S, x1 * S, y1 * S), fill=(20, 20, 22), outline=L, width=lw)
        d.pieslice((x0 * S, y0 * S, x1 * S, (y0 + 2 * r) * S), 180, 360, fill=(20, 20, 22), outline=L, width=lw)
        d.rectangle(((x0) * S + lw, (y0 + r) * S - lw, (x1) * S - lw, (y0 + r) * S + lw), fill=(20, 20, 22))
    # wings
    R(40, 230, 1320, 540, fill=(26, 26, 30))
    R(40, 200, 1320, 238, fill=(36, 36, 40))
    # central tower
    R(500, 70, 860, 540, fill=(30, 30, 34))
    d.polygon([(480 * S, 80 * S), (680 * S, 10 * S), (880 * S, 80 * S)], fill=(36, 36, 40), outline=L, width=lw)
    arch(600, 300, 760, 540)
    for x in (530, 790):
        arch(x, 150, x + 40, 260)
    d.ellipse((650 * S, 110 * S, 710 * S, 170 * S), outline=RED, width=lw)
    # wing windows
    for i in range(5):
        for side in (0, 1):
            x = 80 + i * 82 if side == 0 else 900 + i * 82
            arch(x, 300, x + 50, 420)
            R(x, 450, x + 50, 500)
    im = im.resize((w, h), Image.LANCZOS)
    return im


def trophy(color):
    im = canvas(260, 260)
    d = ImageDraw.Draw(im)
    d.pieslice((60, 10, 200, 170), 0, 180, fill=color)
    d.rectangle((60, 10, 200, 90), fill=color)
    d.arc((20, 30, 90, 110), 90, 270, fill=color, width=12)
    d.arc((170, 30, 240, 110), 270, 90, fill=color, width=12)
    d.rectangle((118, 165, 142, 205), fill=color)
    d.rectangle((80, 205, 180, 240), fill=color)
    return im


def letter_icon(color):
    im = canvas(260, 260)
    d = ImageDraw.Draw(im)
    d.rectangle((40, 20, 220, 245), outline=color, width=10)
    for i, ww in enumerate((120, 140, 140, 110, 140, 80)):
        d.rectangle((70, 60 + i * 28, 70 + ww, 70 + i * 28), fill=color)
    return im


def stadium_icon(color):
    im = canvas(320, 260)
    d = ImageDraw.Draw(im)
    d.rectangle((20, 110, 300, 240), outline=color, width=10)
    d.polygon([(110, 110), (160, 40), (210, 110)], outline=color, width=10)
    for x in (55, 135, 215):
        d.pieslice((x, 150, x + 50, 200), 180, 360, fill=color)
        d.rectangle((x, 175, x + 50, 240), fill=color)
    return im


def calendar_page():
    im = rect(420, 470, (240, 236, 228), radius=16)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 419, 120), radius=16, fill=RED)
    d.rectangle((0, 100, 419, 120), fill=RED)
    t = txt("ABRIL", "xb", 52, WHITE, tracking=8, shadow=False)
    im.alpha_composite(t, (210 - t.width // 2, 30))
    n = txt("7", "anton", 250, (20, 20, 22), shadow=False)
    im.alpha_composite(n, (210 - n.width // 2, 100))
    for x in (90, 330):
        d.ellipse((x - 14, -14, x + 14, 14), fill=(40, 40, 44))
    return soft_shadow(im)


def book():
    im = rect(400, 520, (96, 12, 20), radius=10)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 34, 520), fill=(70, 8, 14))
    d.rectangle((60, 40, 370, 480), outline=(214, 190, 140), width=3)
    t = txt("LIVRO DOS\nHERÓIS E\nHEROÍNAS\nDA PÁTRIA", "serif_b", 52, (226, 204, 150), shadow=False)
    im.alpha_composite(t, (215 - t.width // 2, 110))
    return soft_shadow(im)


def portrait():
    w, h = 440, 540
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, w - 1, h - 1), fill=(150, 128, 92))
    d.ellipse((14, 14, w - 15, h - 15), fill=(58, 46, 32))
    sil = silhouette((92, 76, 54), 300)
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse((14, 14, w - 15, h - 15), fill=255)
    lay = canvas(w, h)
    lay.alpha_composite(sil, (w // 2 - 150, 120))
    lay.putalpha(ImageChops.multiply(lay.getchannel("A"), m))
    im.alpha_composite(lay)
    q = txt("?", "serif_b", 120, (150, 128, 92), shadow=False)
    return soft_shadow(im)


def paper_sheet(w, h, color=(232, 222, 198), seed=2):
    arr = make_bg("paper", seed)[:h, :w]
    im = Image.fromarray(arr).convert("RGBA")
    if color != (232, 222, 198):
        im = Image.new("RGBA", (w, h), color + (255,))
    return im


def news_strip(head, kicker):
    k = txt(kicker, "xb", 26, RED, tracking=4, shadow=False)
    hd = txt(head, "serif_b", 64, (24, 20, 16), shadow=False, maxw=1180, gap=70)
    w = max(k.width, hd.width) + 80
    hh = k.height + hd.height + 60
    arr = make_bg("paper", 9)[:hh, :w]
    im = Image.fromarray(arr).convert("RGBA")
    d = ImageDraw.Draw(im)
    d.rectangle((30, 22, w - 30, 25), fill=(40, 34, 28))
    im.alpha_composite(k, (30, 30))
    im.alpha_composite(hd, (30, 30 + k.height - 10))
    im = im.rotate(-1.2, resample=Image.BICUBIC, expand=True)
    return soft_shadow(im)


def stamp(text, color=RED, size=54, angle=-8):
    t = txt(text, "black", size, color, tracking=4, shadow=False)
    t = t.crop(t.getbbox())
    im = canvas(t.width + 60, t.height + 50)
    d = ImageDraw.Draw(im)
    d.rectangle((4, 4, im.width - 5, im.height - 5), outline=color, width=7)
    im.alpha_composite(t, (30, 25))
    # distress
    a = np.asarray(im.getchannel("A")).astype(np.float32)
    rng = np.random.default_rng(1)
    a *= (rng.random(a.shape) > 0.12)
    im.putalpha(Image.fromarray(a.astype(np.uint8)))
    return im.rotate(angle, resample=Image.BICUBIC, expand=True)


def medallion(size=420):
    S = 2
    s = size * S
    im = canvas(s, s)
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s - 1, s - 1), fill=(10, 10, 10))
    band = canvas(s, s)
    bd = ImageDraw.Draw(band)
    c = s / 2
    hw = s * 0.13
    L = s
    ang = math.radians(45)
    dx, dy = math.cos(ang), math.sin(ang)
    nx, ny = -dy, dx
    pts = [(c - dx * L + nx * hw, c - dy * L + ny * hw), (c + dx * L + nx * hw, c + dy * L + ny * hw),
           (c + dx * L - nx * hw, c + dy * L - ny * hw), (c - dx * L - nx * hw, c - dy * L - ny * hw)]
    bd.polygon(pts, fill=WHITE)
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).ellipse((0, 0, s - 1, s - 1), fill=255)
    band.putalpha(ImageChops.multiply(band.getchannel("A"), m))
    im.alpha_composite(band)
    d.ellipse((s * 0.03, s * 0.03, s * 0.97, s * 0.97), outline=RED, width=int(s * 0.012))
    r = s * 0.31
    d.ellipse((c - r - s * 0.03, c - r - s * 0.03, c + r + s * 0.03, c + r + s * 0.03), fill=(10, 10, 10))
    d.ellipse((c - r, c - r, c + r, c + r), fill=(10, 10, 10), outline=WHITE, width=int(s * 0.016))
    vv = txt("VV", "anton", int(s * 0.27), WHITE, shadow=False)
    im.alpha_composite(vv, (int(c - vv.width / 2), int(c - vv.height / 2 - s * 0.03)))
    for i in range(9):
        hgt = [8, 20, 32, 16, 40, 16, 32, 20, 8][i] * S * size / 420
        x = c - 4 * 22 * S * size / 420 + i * 22 * S * size / 420
        d.rounded_rectangle((x - 5 * S, c + s * 0.17 - hgt / 2, x + 5 * S, c + s * 0.17 + hgt / 2), radius=3 * S, fill=RED)
    return im.resize((size, size), Image.LANCZOS)
