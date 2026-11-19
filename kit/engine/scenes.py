"""All scenes of 'A Resposta Histórica', timed to the narration SRT (seconds)."""
import textwrap
from engine import *
from art import *

DURATION = 624.0
T = Timeline(DURATION)
A = T.add
CLICKS = []     # typewriter key times (s)
BOOMS = []      # chapter impacts (s)
WHOOSH = []     # soft transitions (s)
CX = W // 2


# ---------------------------------------------------------------- helpers
def full_dark():
    return Image.fromarray(make_bg("dark", 77)[:H, :W]).convert("RGBA")


_DARK = None


def chapter(t0, num, title, dur=3.3):
    global _DARK
    if _DARK is None:
        _DARK = full_dark()
    card = _DARK.copy()
    k = txt(f"CAPÍTULO {num}", "xb", 34, RED, tracking=12, shadow=False)
    ti = txt(title, "anton", 150, WHITE, tracking=2)
    bar = rect(140, 8, RED)
    blk = stack([k, bar, ti], gap=18)
    A(t0, t0 + dur, card, CX, H // 2, anim="fade", fin=0.22, fout=0.55, z=60)
    A(t0 + 0.05, t0 + dur, blk, CX, 540 - 20, anim="zoom", fin=1.2, fout=0.55, z=61, kb=0.04)
    sash(t0 - 0.2)
    BOOMS.append(t0)


def sash(t0, dur=0.75, color=RED):
    def fn(tl, d):
        p = ease_io(tl / dur)
        im = canvas(W, H)
        dr = ImageDraw.Draw(im)
        cx = -900 + p * (W + 1800)
        bw = 420
        for off, col in ((0, color + (255,)), (bw + 30, WHITE + (255,))):
            x = cx - off
            dr.polygon([(x - bw / 2 + 300, -10), (x + bw / 2 + 300, -10), (x + bw / 2 - 300, H + 10),
                        (x - bw / 2 - 300, H + 10)], fill=col if off == 0 else (246, 244, 240, 255))
            if off:
                break
        return im
    A(t0, t0 + dur, fn, 0, 0, anchor="tl", fin=0, fout=0, z=70)
    WHOOSH.append(t0)


def head(text, t0, t1, y=470, size=120, color=WHITE, anim="up", f="anton", z=10, maxw=1600, tracking=1, **k):
    s = txt(text, f, size, color, tracking=tracking, maxw=maxw)
    return A(t0, t1, s, CX, y, anim=anim, z=z, **k)


def sub(text, t0, t1, y=600, size=40, color=OFF, f="sb", anim="up", z=10, maxw=1500, **k):
    s = txt(text, f, size, color, maxw=maxw)
    return A(t0, t1, s, CX, y, anim=anim, z=z, **k)


def counter(t0, t1, x, y, v1, ramp=1.4, prefix="", suffix="", size=200, color=WHITE, fmt="{:d}"):
    cache = {}

    def fn(tl, d):
        v = int(round(v1 * ease(tl / ramp)))
        if v not in cache:
            s = fmt.format(v).replace(",", ".")
            cache[v] = txt(prefix + s + suffix, "anton", size, color)
        return cache[v]
    return A(t0, t1, fn, x, y, anim="pop", fin=0.4)


class Typer:
    """Typewriter page: blocks typed char by char between given times."""

    def __init__(self, blocks, ink=INK, page=(W, H)):
        self.blocks = []
        self.ink = ink
        self.page = page
        for b in blocks:
            text, ta, tb, x, y = b["text"], b["t0"], b["t1"], b["x"], b["y"]
            fo = font(b.get("f", "type"), b.get("size", 34))
            cols = b.get("cols", 62)
            lines = []
            for para in text.split("\n"):
                lines += textwrap.wrap(para, cols) or [""]
            total = sum(len(l) for l in lines)
            self.blocks.append(dict(lines=lines, t0=ta, t1=tb, x=x, y=y, fo=fo, lh=b.get("lh", 50),
                                    total=total, fill=b.get("fill", ink), hl=b.get("hl")))
            for i in range(total):
                CLICKS.append(ta + (tb - ta) * (i + 1) / max(total, 1))

    def sprite_at(self, t):
        im = canvas(*self.page)
        d = ImageDraw.Draw(im)
        caret = None
        for b in self.blocks:
            if t < b["t0"]:
                continue
            n = int(b["total"] * min(1.0, (t - b["t0"]) / max(b["t1"] - b["t0"], 0.01)))
            y = b["y"]
            left = n
            for li, line in enumerate(b["lines"]):
                if left <= 0:
                    break
                part = line[:left]
                d.text((b["x"], y), part, font=b["fo"], fill=b["fill"])
                if b["hl"] and t > b["t1"]:
                    pass
                left -= len(line)
                if left <= 0 or li == len(b["lines"]) - 1:
                    caret = (b["x"] + b["fo"].getlength(part) + 4, y, b["fo"].size)
                y += b["lh"]
            if n < b["total"]:
                break
        if caret and int(t * 2.4) % 2 == 0:
            x, y, s = caret
            d.rectangle((x, y + 4, x + s * 0.55, y + s + 4), fill=self.ink + (170,))
        return im

    def item(self, t0, t1, z=5):
        return A(t0, t1, lambda tl, d, t0=t0: self.sprite_at(t0 + tl), 0, 0, anchor="tl", fin=0.4, fout=0.5, z=z)


# ================================================================ 1. COLD OPEN 0 – 38.4
T.bg(0, "black")
op = Typer([dict(text="Rio de Janeiro, 7 de abril de 1924.", t0=0.35, t1=3.0, x=0, y=0, size=54,
                 fill=OFF, cols=80)], ink=OFF, page=(1150, 120))
A(0.0, 4.1, lambda tl, d: op.sprite_at(tl), CX, 520, fin=0.2, fout=0.5)

T.bg(4.15, "sepia", 3)
# a letter on a desk, being written
desk_paper = paper_sheet(860, 1060, seed=4)
dp = ImageDraw.Draw(desk_paper)
hdr = txt("Ofício Nº 261", "type_b", 44, INK, shadow=False)
desk_paper.alpha_composite(hdr, (70, 60))
paper_rot = None


def letter_writing(tl, d):
    im = desk_paper.copy()
    dr = ImageDraw.Draw(im)
    rng = random.Random(11)
    p = ease_io(tl / 11.5)
    rows = []
    y = 210
    for para in range(3):
        for r in range(5 if para < 2 else 3):
            ww = rng.randint(520, 760) if r < 4 else rng.randint(260, 420)
            rows.append((y, ww))
            y += 46
        y += 40
    shown = p * len(rows)
    for i, (yy, ww) in enumerate(rows):
        if i < int(shown):
            dr.rounded_rectangle((90, yy, 90 + ww, yy + 12), radius=6, fill=(80, 64, 46, 210))
        elif i == int(shown):
            frac = shown - int(shown)
            dr.rounded_rectangle((90, yy, 90 + ww * frac, yy + 12), radius=6, fill=(80, 64, 46, 210))
    if tl > 10.5:
        a = min(1, (tl - 10.5) / 1.5)
        sig = txt("José Augusto Prestes", "serif_i", 64, (40, 26, 14), shadow=False)
        sig.putalpha(sig.getchannel("A").point(lambda v: int(v * a)))
        im.alpha_composite(sig, (380, 900))
    return im.rotate(4, resample=Image.BILINEAR, expand=True)


A(4.2, 16.7, letter_writing, CX + 80, 600, anim="up", dist=80, fin=1.0, fout=0.6, kb=0.06)
sub("POUCOS PARÁGRAFOS.", 11.2, 16.6, y=160, size=34, f="xb", color=SEPIA)
A(13.0, 16.6, txt("SEM GOLS · SEM TÍTULOS · SEM DINHEIRO", "xb", 30, OFF, tracking=6, shadow=False), CX, 215, anim="up")

T.bg(16.7, "dark", 2)
xs = [CX - 6 * 128 + 64 + i * 128 for i in range(12)]
for i, x in enumerate(xs):
    A(16.8 + i * 0.22, 25.9, silhouette(WHITE, 104), x, 470, anim="up", dist=40, fin=0.45)
A(17.2, 25.9, txt("12", "anton", 120, RED), CX, 230, anim="pop")
for j, wd in enumerate(["NEGROS", "POBRES", "OPERÁRIOS"]):
    A(19.6 + j * 0.9, 25.9, txt(wd, "xb", 44, OFF, tracking=6), CX - 420 + j * 420, 680, anim="up")
A(22.8, 25.9, txt("E A RECUSA DE UM CLUBE EM ABANDONÁ-LOS", "xb", 34, RED, tracking=4), CX, 770, anim="up")

T.bg(26.0, "dark", 3)
pod = txt("UM LUGAR ENTRE OS PODEROSOS", "anton", 110, (140, 140, 146))


def strike(tl, d):
    im = pod.copy()
    p = ease(max(0, tl - 1.8) / 0.6)
    if p > 0:
        bb = im.getbbox()
        ImageDraw.Draw(im).rectangle((bb[0], im.height // 2 - 6, bb[0] + (bb[2] - bb[0]) * p, im.height // 2 + 8), fill=RED)
    return im


A(26.0, 30.7, strike, CX, 470, anim="up")
A(30.7, 33.5, txt("UMA ALMA.", "anton", 210, WHITE), CX, 470, anim="zoom", fin=1.0, kb=0.05)

# title
T.bg(33.4, "dark", 5)
sash(33.25)
BOOMS.append(33.45)
t1 = txt("A RESPOSTA", "anton", 190, WHITE, tracking=4)
t2 = txt("HISTÓRICA", "anton", 190, RED, tracking=4)
tt = stack([t1, t2], gap=-70)
A(33.45, 38.45, tt, CX, 470, anim="zoom", fin=1.4, fout=0.6, kb=0.05, z=20)
A(34.3, 38.45, txt("RIO DE JANEIRO · 1923 — 1927", "xb", 32, OFF, tracking=10, shadow=False), CX, 745, anim="up")
A(35.2, 38.45, txt("UM DOCUMENTÁRIO VOZ VASCAÍNA", "sb", 26, GREY, tracking=8, shadow=False), CX, 800, anim="up")

# ================================================================ 2. UM FUTEBOL PARA POUCOS 38.5 – 102.4
chapter(38.5, 1, "UM FUTEBOL PARA POUCOS")
T.bg(40.0, "sepia", 6)
A(41.4, 68.5, skyline(), CX, H - 260, anim="up", dist=60, fin=1.5, kb=0.05, z=1)
A(42.6, 52.6, label("RIO DE JANEIRO · INÍCIO DO SÉCULO XX", 28), CX, 150, anim="down")
head("NÃO ERA O ESPORTE DO POVO", 43.5, 47.8, y=330, size=104)
A(47.85, 58.5, rich([("UM PASSATEMPO DA ", WHITE), ("ELITE", RED)], "anton", 120), CX, 320, anim="up")
for j, wd in enumerate(["FILHOS DE FAMÍLIAS RICAS", "BAIRROS NOBRES", "REGRAS PARA POUCOS"]):
    A(50.2 + j * 2.6, 58.5, label(wd, 30, WHITE, (20, 16, 12)), CX - 560 + j * 560, 470, anim="pop")
# abolition
A(58.65, 68.5, rect(W, 760, (14, 11, 8, 225)), CX, 380, fin=0.5, z=8)
A(59.0, 63.8, txt("1888", "anton", 230, WHITE), CX, 330, anim="pop", z=9)
sub("ABOLIÇÃO DA ESCRAVIDÃO — POUCO MAIS DE 30 ANOS ANTES", 59.6, 63.8, y=520, size=36, f="xb", z=9)
head("O PRECONCEITO ESTAVA ESCRITO", 63.9, 68.5, y=300, size=100, z=9)
reg = paper_sheet(620, 300, seed=8)
rd = ImageDraw.Draw(reg)
rd.text((40, 30), "REGULAMENTO", font=font("type_b", 44), fill=INK)
for i in range(5):
    rd.rectangle((40, 110 + i * 34, 40 + [520, 480, 540, 400, 300][i], 122 + i * 34), fill=(90, 74, 56))
A(65.0, 68.5, soft_shadow(reg.rotate(-3, expand=True, resample=Image.BICUBIC)), CX, 560, anim="up", z=9)

# timeline 1907 / 1917
T.bg(68.6, "dark", 7)


def tline(tl, d):
    im = canvas(1500, 20)
    p = ease(tl / 1.2)
    ImageDraw.Draw(im).rectangle((0, 6, 1500 * p, 12), fill=(90, 90, 96))
    return im


A(68.6, 92.4, tline, CX, 560, fin=0.2, fout=0.6)
for x, yr, ta in ((CX - 400, "1907", 68.8), (CX + 400, "1917", 79.35)):
    dot = canvas(60, 60)
    ImageDraw.Draw(dot).ellipse((6, 6, 54, 54), fill=RED, outline=WHITE, width=5)
    A(ta, 92.4, dot, x, 560, anim="pop", fin=0.4, fout=0.6, z=3)
    A(ta + 0.1, 92.4, txt(yr, "anton", 120, WHITE), x, 660, anim="up", fout=0.6, z=3)
c1 = stack([txt("A liga proíbe o registro de", "sb", 36, OFF, shadow=False),
            txt("“PESSOAS DE COR”", "anton", 70, RED, shadow=False),
            txt("como atletas amadores", "sb", 36, OFF, shadow=False)], gap=-14)
A(70.5, 92.4, c1, CX - 400, 360, anim="up", fout=0.6)
c2 = stack([txt("Estatuto da LMDT exclui", "sb", 36, OFF, shadow=False),
            txt("ANALFABETOS", "anton", 70, RED, shadow=False),
            txt("e certas profissões", "sb", 36, OFF, shadow=False)], gap=-14)
A(85.4, 92.4, c2, CX + 400, 360, anim="up", fout=0.6)
A(81.0, 92.4, txt("LIGA METROPOLITANA DE DESPORTOS TERRESTRES", "xb", 24, GREY, tracking=4, shadow=False), CX + 400, 740, anim="up")
# the door
T.bg(92.45, "dark", 8)


def door(tl, d):
    im = canvas(900, 640)
    dr = ImageDraw.Draw(im)
    p = ease_io(min(1, max(0, (tl - 4.0) / 1.6)))
    gap = 300 * (1 - p)
    dr.rectangle((0, 0, 899, 639), outline=(110, 110, 116), width=10)
    lw = 450 - gap / 2
    dr.rectangle((10, 10, 10 + lw - 10, 629), fill=(40, 40, 44))
    dr.rectangle((890 - lw + 10, 10, 889, 629), fill=(40, 40, 44))
    if gap > 24:
        dr.rectangle((10 + lw, 10, 890 - lw, 629), fill=(236, 226, 200))
    dr.ellipse((10 + lw - 60, 300, 10 + lw - 36, 324), fill=RED)
    dr.ellipse((890 - lw + 36, 300, 890 - lw + 60, 324), fill=RED)
    return im


A(92.45, 102.4, door, CX, 430, anim="up", fin=0.7, fout=0.4)
A(92.6, 98.5, txt("SEM ESCOLA, SEM ACESSO", "xb", 36, OFF, tracking=8), CX, 820, anim="up")
A(98.6, 102.4, txt("A PORTA CONTINUAVA FECHADA.", "anton", 80, WHITE), CX, 820, anim="up")

# ================================================================ 3. O CLUBE DOS IMIGRANTES 102.4 – 158.2
chapter(102.4, 2, "O CLUBE DOS IMIGRANTES", dur=2.6)
T.bg(104.0, "dark", 9)
A(104.9, 108.6, txt("21 · 08 · 1898", "anton", 210, WHITE, tracking=6), CX, 420, anim="zoom", fin=1.0)
A(105.6, 108.6, label("FUNDAÇÃO DO CLUB DE REGATAS VASCO DA GAMA", 30), CX, 620, anim="up")


def route(tl, d):
    im = canvas(1400, 600)
    dr = ImageDraw.Draw(im)
    a = (220, 470)
    b = (1180, 150)
    p = ease(tl / 2.5)
    n = 60
    for i in range(int(n * p)):
        s = i / n
        x = a[0] + (b[0] - a[0]) * s
        y = a[1] + (b[1] - a[1]) * s - math.sin(s * math.pi) * 210
        if i % 2 == 0:
            dr.ellipse((x - 5, y - 5, x + 5, y + 5), fill=OFF)
    for (x, y), nm in ((b, "PORTUGAL"), (a, "RIO DE JANEIRO")):
        dr.ellipse((x - 16, y - 16, x + 16, y + 16), fill=RED, outline=WHITE, width=4)
        t = txt(nm, "xb", 34, WHITE, tracking=4, shadow=False)
        im.alpha_composite(t, (int(x - t.width / 2), int(y + 22)))
    return im


A(108.7, 119.0, route, CX, 380, anim="up")
A(110.4, 119.0, txt("IMIGRANTES PORTUGUESES · GENTE DO COMÉRCIO", "xb", 34, OFF, tracking=4), CX, 760, anim="up")


def rowing():
    im = canvas(1300, 300)
    dr = ImageDraw.Draw(im)
    dr.ellipse((0, 150, 1300, 210), fill=WHITE)
    dr.rectangle((0, 150, 1300, 180), fill=(14, 14, 16, 0))
    for i in range(4):
        x = 330 + i * 200
        dr.ellipse((x - 26, 40, x + 26, 92), fill=WHITE)
        dr.rounded_rectangle((x - 30, 96, x + 30, 175), radius=22, fill=WHITE)
        dr.line((x, 140, x - 190, 285), fill=RED, width=10)
        dr.line((x, 140, x + 170, 285), fill=RED, width=10)
    for k in range(8):
        y = 260 + (k % 3) * 12
        x = 60 + k * 150
        dr.line((x, y, x + 90, y), fill=(90, 90, 96), width=4)
    return im


A(119.0, 121.6, rowing(), CX, 430, anim="right", dist=120, fin=0.8)
A(119.3, 121.6, txt("NO COMEÇO, UM CLUBE DE REMO", "xb", 38, WHITE, tracking=4), CX, 720, anim="up")
A(121.65, 124.9, txt("1915", "anton", 230, WHITE), CX, 380, anim="pop")
A(122.0, 124.9, label("O FUTEBOL CHEGA AO VASCO", 32), CX, 590, anim="up")
for k, (ta, tb) in enumerate(((124.9, 137.6), (137.6, 144.3), (144.3, 151.7), (151.7, 158.2))):
    act = [0, 1, 2, 3][k]
    A(ta, tb, stairs(act), CX, 560, fin=0.5 if k == 0 else 0.25, fout=0.25, anim="up" if k == 0 else "fade")
A(130.8, 137.6, rich([("NÃO O SOBRENOME. ", (120, 120, 126)), ("O FUTEBOL.", WHITE)], "anton", 96), CX, 160, anim="up")
A(137.65, 144.2, txt("BRANCO OU NEGRO. DOUTOR OU OPERÁRIO.", "anton", 80, WHITE), CX, 160, anim="up")
A(144.4, 151.6, txt("CAMPEÃO DA SÉRIE B", "anton", 90, WHITE), CX, 160, anim="up")
A(151.8, 158.2, txt("A ELITE IA CONHECER UM TIME DIFERENTE", "anton", 80, WHITE), CX, 160, anim="up")

# ================================================================ 4. OS CAMISAS NEGRAS 158.2 – 270.6
chapter(158.2, 3, "OS CAMISAS NEGRAS", dur=2.9)
T.bg(160.0, "dark", 10)
_j = jersey(); _j = _j.resize((int(_j.width*0.86), int(_j.height*0.86)), Image.LANCZOS)
A(160.9, 173.8, _j, CX, 470, anim="zoom", fin=1.6, kb=0.06)
A(162.0, 173.8, label("1923", 34, WHITE, RED), CX, 110, anim="down", z=3)
A(165.6, 173.8, txt("OS CAMISAS NEGRAS", "anton", 100, WHITE, tracking=3), CX, 805, anim="up", z=3)
A(170.3, 173.8, txt("MUITO MAIS QUE A COR DO UNIFORME", "xb", 30, RED, tracking=6), CX, 870, anim="up", z=3)

players = [
    ("NELSON", "GOLEIRO", "Motorista de táxi", 173.95),
    ("LEITÃO", "ZAGUEIRO", "Fábrica de tintas", 181.9),
    ("MINGOTE", "ZAGUEIRO", "Pintor de paredes", 185.6),
    ("NICOLINO", "MEIO-CAMPO", "Operário do petróleo", 188.3),
    ("ARTHUR", "MEIO-CAMPO", "Mecânico", 192.7),
    ("TORTEROLLI", "MEIO-CAMPO", "Operário da Singer", 194.7),
    ("BOLÃO", "MEIO-CAMPO", "Estivador do porto", 198.1),
    ("NEGRITO", "ATAQUE", "Trabalhador da indústria", 203.6),
    ("PASCHOAL", "ATAQUE", "Comerciário", 204.6),
    ("CECI", "ATAQUE", "Comerciário", 205.5),
    ("ARLINDO", "ATAQUE", "Funcionário de seguradora", 206.6),
]
T.bg(173.9, "dark", 11)
A(173.9, 214.3, txt("OS CAMPEÕES DE 1923", "xb", 32, RED, tracking=10, shadow=False), CX, 92, anim="down")


def pcard(nm, pos, job):
    im = rect(400, 196, (24, 24, 28), radius=6)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 8, 196), fill=RED)
    im.alpha_composite(silhouette((70, 70, 76), 74), (300, 46))
    im.alpha_composite(txt(pos, "xb", 20, RED, tracking=4, shadow=False), (12, 8))
    im.alpha_composite(txt(nm, "anton", 60, WHITE, shadow=False), (12, 30))
    im.alpha_composite(txt(job, "m", 24, OFF, shadow=False, maxw=280, align="left"), (12, 112))
    return im


for i, (nm, pos, job, ta) in enumerate(players):
    r, c = divmod(i, 4)
    ncol = 4 if r < 2 else 3
    x = CX - (ncol - 1) * 215 + c * 430
    y = 245 + r * 222
    A(ta, 214.3, pcard(nm, pos, job), x, y, anim="pop", fin=0.45, fout=0.5)
A(178.7, 185.5, label("1º GOLEIRO NEGRO DO VASCO", 24, WHITE, RED), CX - 645, 360, anim="up", z=4)
A(208.3, 214.3, rect(W, H, (10, 10, 12, 215)), CX, H // 2, fin=0.5, z=6)
A(208.5, 214.3, txt("TRABALHAVAM ANTES DE TREINAR", "anton", 110, WHITE), CX, 470, anim="up", z=7)

# literacy
T.bg(214.35, "paper", 12)
abc = Typer([dict(text="A  B  C  D  E  F  G", t0=215.0, t1=218.0, x=420, y=260, size=96, f="type_b", cols=40),
             dict(text="Custódio Moura — bibliotecário do clube", t0=220.5, t1=223.6, x=420, y=520, size=44, cols=60)])
abc.item(214.4, 224.6)
A(214.45, 224.6, txt("MUITOS NÃO SABIAM LER", "anton", 74, INK, shadow=False), CX, 130, anim="down")
sumula = canvas(1080, 120)
sd = ImageDraw.Draw(sumula)
sd.text((0, 30), "Assinatura:", font=font("type", 40), fill=INK)
sd.line((300, 80, 1060, 80), fill=INK, width=3)
A(217.2, 224.6, sumula, CX, 420, anim="up")
A(218.4, 224.6, txt("Nelson da Conceição", "serif_i", 64, (30, 30, 90), shadow=False), CX + 160, 410, anim="fade", fin=1.2)

# Platero
T.bg(224.7, "dark", 13)
A(224.75, 239.3, label("TÉCNICO URUGUAIO", 28), CX, 170, anim="down")
A(224.9, 235.2, txt("RAMÓN PLATERO", "anton", 150, WHITE, tracking=2), CX, 330, anim="up")
A(228.5, 235.2, txt("PREPARAÇÃO FÍSICA DE VERDADE", "xb", 40, RED, tracking=6), CX, 470, anim="up")


def run_route(tl, d):
    im = canvas(1300, 220)
    dr = ImageDraw.Draw(im)
    p = ease(tl / 1.2)
    a, b = 140, 1160
    for x in range(a, int(a + (b - a) * p), 34):
        dr.rectangle((x, 100, x + 18, 108), fill=OFF)
    for x, nm in ((a, "TIJUCA"), (b, "VILA ISABEL")):
        dr.ellipse((x - 16, 88, x + 16, 120), fill=RED, outline=WHITE, width=4)
        t = txt(nm, "xb", 34, WHITE, tracking=4, shadow=False)
        im.alpha_composite(t, (int(x - t.width / 2), 128))
    if tl > 1.2:
        s = (math.sin((tl - 1.2) * 1.6 - math.pi / 2) + 1) / 2
        x = a + (b - a) * s
        dr.ellipse((x - 12, 92, x + 12, 116), fill=WHITE)
    return im


A(235.3, 239.4, run_route, CX, 560, anim="up")
A(235.6, 239.4, txt("CORRIDAS DIÁRIAS", "xb", 30, OFF, tracking=8, shadow=False), CX, 410, anim="up")

T.bg(239.45, "dark", 14)
A(239.5, 246.7, txt("1º TURNO", "xb", 34, RED, tracking=12, shadow=False), CX, 230, anim="down")
A(240.0, 246.7, txt("VITÓRIAS SOBRE OS 3\nMAIORES RIVAIS DA CIDADE", "anton", 104, WHITE, gap=120), CX, 430, anim="up")
for j, (v, nm) in enumerate(((11, "VITÓRIAS"), (2, "EMPATES"), (1, "DERROTA"))):
    x = CX - 500 + j * 500
    counter(246.8 + j * 0.7, 251.6, x, 380, v, size=260, color=WHITE if j == 0 else (200, 200, 204))
    A(247.0 + j * 0.7, 251.6, txt(nm, "xb", 40, RED if j == 0 else OFF, tracking=8), x, 560, anim="up")

T.bg(251.6, "dark", 15)
A(251.7, 261.3, txt("12 · 08 · 1923", "anton", 120, WHITE, tracking=4), CX, 200, anim="down")
board = rect(1400, 300, (22, 22, 26), radius=10, outline=(70, 70, 76), width=4)
for nm, x in (("VASCO", 250), ("SÃO CRISTÓVÃO", 1150)):
    t = txt(nm, "anton", 64, WHITE, shadow=False)
    board.alpha_composite(t, (x - t.width // 2, 150 - t.height // 2))
A(252.5, 261.3, board, CX, 500, anim="up")
A(257.2, 261.3, txt("3 × 2", "anton", 160, RED), CX, 500, anim="pop", z=4)
A(258.5, 261.3, txt("TÍTULO COM UMA RODADA DE ANTECEDÊNCIA", "xb", 30, OFF, tracking=6), CX, 720, anim="up")

T.bg(261.3, "red", 16)


def rays(tl, d):
    im = canvas(1400, 1400)
    dr = ImageDraw.Draw(im)
    c = 700
    rot = tl * 4
    for i in range(24):
        a0 = math.radians(i * 15 + rot)
        a1 = a0 + math.radians(6)
        dr.polygon([(c, c), (c + 1000 * math.cos(a0), c + 1000 * math.sin(a0)),
                    (c + 1000 * math.cos(a1), c + 1000 * math.sin(a1))], fill=(255, 255, 255, 18))
    return im


A(261.3, 270.7, rays, CX, 470, fin=1.0)
A(261.4, 270.7, txt("★", "black", 120, WHITE), CX, 200, anim="pop")
A(261.6, 270.7, stack([txt("CAMPEÃO", "anton", 190, WHITE), txt("CARIOCA DE 1923", "anton", 110, WHITE)], gap=-40),
  CX, 470, anim="zoom", fin=1.0, kb=0.05)
A(268.25, 270.7, txt("NO PRIMEIRO ANO NA ELITE", "xb", 36, WHITE, tracking=8), CX, 730, anim="up")

# ================================================================ 5. A REAÇÃO DA ELITE 270.6 – 337
chapter(270.65, 4, "A REAÇÃO DA ELITE", dur=3.2)
T.bg(272.5, "dark", 17)
A(275.0, 279.0, txt("UMA AFRONTA.", "anton", 200, WHITE), CX, 430, anim="zoom", fin=0.8)
A(279.05, 284.8, stack([rich([("TRABALHADORES", WHITE)], "anton", 120),
                         txt("venceram os filhos da elite", "serif_i", 64, OFF, shadow=False)], gap=-10), CX, 420, anim="up")
T.bg(284.85, "sepia", 18)
A(284.9, 300.8, label("MARÇO DE 1924", 32), CX, 160, anim="down")
A(289.3, 300.8, news_strip("Clubes ricos rompem com a Liga Metropolitana e fundam nova entidade", "O RIO DE JANEIRO · 1924"),
  CX, 400, anim="up", dist=80, fin=0.8, kb=0.03)
A(295.7, 300.8, stack([txt("A.M.E.A.", "anton", 120, WHITE, tracking=8),
                        txt("Associação Metropolitana de Esportes Athleticos", "sb", 36, OFF)], gap=-10),
  CX, 720, anim="up", z=3)

T.bg(300.85, "dark", 19)
A(300.9, 305.4, txt("O VASCO FOI CONVIDADO.", "anton", 110, WHITE), CX, 360, anim="up")
A(302.9, 305.4, label("COM UMA CONDIÇÃO", 40), CX, 520, anim="pop")
xs2 = [CX - 6 * 128 + 64 + i * 128 + (40 if i >= 7 else 0) - 20 for i in range(12)]
for i, x in enumerate(xs2):
    A(305.5 + i * 0.1, 312.4, silhouette(WHITE, 104), x, 430, anim="up", dist=30, fin=0.4, fout=0.3)
    A(312.3, 315.2, silhouette((60, 60, 64), 104), x, 430, fin=0.3, fout=0.4)
    A(312.5 + i * 0.06, 315.2, x_mark(80), x, 430, anim="pop", fin=0.25, fout=0.4, z=3)
A(305.6, 315.2, txt("EXCLUIR 12 JOGADORES", "anton", 96, RED), CX, 200, anim="down")


def bracket(w, t):
    im = canvas(w, 110)
    d = ImageDraw.Draw(im)
    d.line((6, 0, 6, 26, w - 6, 26, w - 6, 0), fill=OFF, width=5)
    s = txt(t, "xb", 30, OFF, tracking=3, shadow=False)
    im.alpha_composite(s, (w // 2 - s.width // 2, 34))
    return im


A(308.7, 315.2, bracket(7 * 128 - 20, "7 DO TIME PRINCIPAL"), (xs2[0] + xs2[6]) / 2, 600, anim="up")
A(309.8, 315.2, bracket(5 * 128 - 20, "5 DO SEGUNDO QUADRO"), (xs2[7] + xs2[11]) / 2, 600, anim="up")
A(311.0, 315.2, txt("QUASE TODOS NEGROS E DE ORIGEM HUMILDE", "xb", 32, WHITE, tracking=4), CX, 760, anim="up")

T.bg(315.25, "paper", 20)
form = Typer([
    dict(text="SINDICÂNCIA — COMISSÃO ORGANIZADORA", t0=315.4, t1=316.8, x=330, y=150, size=40, f="type_b", cols=60),
    dict(text="Jogador: ..................................", t0=316.9, t1=317.6, x=330, y=270, size=38, cols=60),
    dict(text="Local de trabalho atual: ..................", t0=317.7, t1=319.0, x=330, y=350, size=38, cols=60),
    dict(text="Local de trabalho anterior: ...............", t0=319.1, t1=320.6, x=330, y=430, size=38, cols=60),
    dict(text="Posição social: ...........................", t0=320.7, t1=321.9, x=330, y=510, size=38, cols=60),
    dict(text="Defesa do atleta: ", t0=322.0, t1=322.9, x=330, y=590, size=38, cols=60),
])
form.item(315.3, 326.85)
A(323.4, 326.85, stamp("SEM DIREITO A DEFESA", RED, 60), CX + 320, 640, anim="pop", fin=0.2, z=7)
T.bg(326.9, "dark", 21)
A(326.95, 332.4, txt("O RECADO ERA CLARO.", "anton", 130, WHITE), CX, 440, anim="up")
A(332.5, 337.0, stack([txt("ENTRAR, SIM.", "anton", 110, WHITE),
                        rich([("SEM OS HOMENS QUE O FIZERAM ", OFF), ("CAMPEÃO", RED)], "anton", 82)], gap=-10),
  CX, 440, anim="up")

# ================================================================ 6. A CARTA 337 – 423
chapter(337.0, 5, "A CARTA", dur=2.8)
T.bg(338.6, "sepia", 22)
A(339.6, 355.4, portrait(), CX - 420, 430, anim="up", fin=1.0, kb=0.04)
A(339.9, 355.4, txt("JOSÉ AUGUSTO\nPRESTES", "anton", 110, WHITE, align="left", gap=118), CX - 150, 290, anim="left", anchor="l")
A(340.6, 355.4, txt("PRESIDENTE DO VASCO", "xb", 30, RED, tracking=8, shadow=False), CX - 126, 450, anim="left", anchor="l")
for j, wd in enumerate(["NASCIDO EM PORTUGAL", "EMPRESÁRIO", "REPUBLICANO"]):
    A(342.0 + j * 1.2, 355.4, txt("— " + wd, "sb", 34, OFF, shadow=False), CX - 126, 520 + j * 56, anim="left", anchor="l")
A(346.5, 351.8, txt("“O homem certo, no ano certo.”", "serif_i", 54, SEPIA), CX, 830, anim="up")
A(351.9, 355.4, label("DECISÃO UNÂNIME DA DIRETORIA", 34), CX, 830, anim="pop")

T.bg(355.5, "paper", 23)
L = 300
page1 = Typer([
    dict(text="Rio de Janeiro, 7 de Abril de 1924.", t0=355.8, t1=358.6, x=L, y=130, size=40, cols=70),
    dict(text="Ofício Nº 261", t0=359.0, t1=360.5, x=L, y=190, size=40, f="type_b", cols=70),
    dict(text="Exmo. Sr. Dr. Arnaldo Guinle,", t0=362.7, t1=365.0, x=L, y=300, size=40, cols=70),
    dict(text="M. D. Presidente da Comissão Organizadora da AMEA", t0=365.0, t1=368.0, x=L, y=355, size=34, cols=70),
    dict(text="Quanto à condição de eliminarmos doze dos nossos jogadores das nossas equipes, resolve por unanimidade a Diretoria do Club de Regatas Vasco da Gama não a dever aceitar.",
         t0=368.4, t1=380.4, x=L, y=470, size=48, cols=48, lh=70),
])
page1.item(355.5, 380.65)
page2 = Typer([
    dict(text="Estamos certos que V. Exa. será o primeiro a reconhecer que seria um ato pouco digno da nossa parte sacrificar, ao desejo de filiar-se à AMEA, alguns dos que lutaram para que tivéssemos a vitória do Campeonato de 1923.",
         t0=380.7, t1=397.8, x=L, y=120, size=44, cols=54, lh=64),
    dict(text="São esses doze jogadores jovens, quase todos brasileiros, no começo de sua carreira, e o ato público que os pode macular nunca será praticado com a solidariedade dos que dirigem a casa que os acolheu.",
         t0=398.1, t1=411.3, x=L, y=500, size=44, cols=54, lh=64),
])
page2.item(380.65, 411.55)
page3 = Typer([
    dict(text="Nestes termos, sentimos ter de comunicar a V. Exa. que desistimos de fazer parte da AMEA.",
         t0=411.65, t1=418.6, x=L, y=260, size=56, cols=42, lh=84),
    dict(text="José Augusto Prestes — Presidente", t0=418.7, t1=419.1, x=L, y=600, size=38, cols=60),
])
page3.item(411.55, 419.15)
A(417.0, 419.15, txt("José Augusto Prestes", "serif_i", 96, (40, 30, 80), shadow=False), CX + 300, 560, fin=1.2)
T.bg(419.1, "dark", 24)
A(419.15, 423.0, stack([txt("O VASCO PREFERIU FICAR DE FORA", "anton", 104, WHITE),
                         rich([("A ", WHITE), ("ABANDONAR OS SEUS.", RED)], "anton", 104)], gap=-20), CX, 440, anim="zoom", fin=1.0)

# ================================================================ 7. A RESPOSTA À RESPOSTA 423 – 452.4
chapter(423.0, 6, "A RESPOSTA À RESPOSTA", dur=3.0)
T.bg(424.8, "grey", 25)
rep = Typer([
    dict(text="Rio de Janeiro, 17 de abril de 1924.", t0=426.2, t1=428.0, x=L, y=130, size=38, cols=70, fill=(30, 30, 34)),
    dict(text="Exmo. Sr. José Augusto Prestes,", t0=428.1, t1=429.6, x=L, y=190, size=38, cols=70, fill=(30, 30, 34)),
    dict(text="...esperava que o Vasco formasse equipes genuinamente portuguesas...", t0=431.3, t1=436.0,
         x=L, y=470, size=46, cols=46, lh=70, fill=(30, 30, 34)),
], ink=(30, 30, 34))


def reply_page(tl, d):
    t = 426.2 + tl
    im = rep.sprite_at(t)
    dr = ImageDraw.Draw(im)
    rng = random.Random(4)
    nrow = int(min(5, max(0, (t - 429.7) / 0.25)))
    for i in range(nrow):
        dr.rounded_rectangle((L, 290 + i * 38, L + rng.randint(800, 1250), 302 + i * 38), radius=6, fill=(120, 120, 124))
    if t > 436.1:
        p = ease((t - 436.1) / 0.6)
        fo = font("type", 46)
        x0 = L
        dr.rectangle((x0 - 6, 470 + 70 + 54, x0 - 6 + (fo.getlength("genuinamente portuguesas") + 12) * p, 470 + 70 + 62), fill=RED)
    return im


A(426.2, 444.35, reply_page, 0, 0, anchor="tl", fin=0.4)
A(426.4, 431.1, label("A AMEA RESPONDE PONTO POR PONTO", 28, WHITE, (40, 40, 44)), CX, 380, anim="pop")
A(438.2, 444.35, rect(1500, 200, (16, 16, 18, 235), radius=8), CX, 770, fin=0.4, z=8)
A(438.3, 444.35, stack([txt("OU SEJA:", "xb", 30, RED, tracking=10, shadow=False),
                         txt("trocar os jogadores negros por brancos da colônia portuguesa", "sb", 42, WHITE, maxw=1350, shadow=False)], gap=-6),
  CX, 770, anim="up", z=9)
T.bg(444.4, "dark", 26)
A(444.45, 452.4, stack([txt("O PRECONCEITO", "anton", 150, WHITE), underline(txt("SEM DISFARCE", "anton", 150, RED), RED, 10)], gap=-30),
  CX, 450, anim="zoom", fin=1.0, kb=0.04)

# ================================================================ 8. A CASA DO POVO 452.4 – 552
chapter(452.4, 7, "A CASA DO POVO", dur=2.9)
T.bg(454.3, "dark", 27)
A(455.3, 463.6, txt("FORA DA AMEA, NA LIGA METROPOLITANA", "xb", 34, OFF, tracking=6), CX, 200, anim="down")
A(457.0, 463.6, hstack([stack([txt("★", "black", 90, RED), txt("1923", "anton", 150, WHITE)], gap=-20),
                         stack([txt("★", "black", 90, RED), txt("1924", "anton", 150, WHITE)], gap=-20)], gap=160),
  CX, 450, anim="pop")
A(458.5, 463.6, label("CAMPEÕES OUTRA VEZ", 36), CX, 680, anim="up")


def crowd(tl, d):
    return stands(min(1.0, tl / 5.0))


A(463.7, 474.85, crowd, CX, 520, anim="up", fin=0.6)
A(463.8, 470.8, txt("O VASCO LOTAVA OS ESTÁDIOS", "anton", 96, WHITE), CX, 170, anim="down")
A(470.9, 474.85, txt("SEM O VASCO, MENOS DINHEIRO NA NOVA LIGA", "anton", 70, RED), CX, 170, anim="down")
T.bg(474.9, "dark", 28)
A(474.95, 486.5, txt("1925", "anton", 220, WHITE), CX, 250, anim="pop")
A(475.6, 486.5, txt("A AMEA VOLTA ATRÁS", "anton", 90, RED), CX, 420, anim="up")
for j, wd in enumerate(["VASCO CONVIDADO DE NOVO", "JOGADORES CAMPEÕES GARANTIDOS"]):
    A(479.0 + j * 2.6, 486.5, hstack([txt("✓", "black", 46, RED, shadow=False), txt(wd, "xb", 40, WHITE, tracking=3, shadow=False)], gap=16),
      CX, 560 + j * 80, anim="left")
A(486.6, 492.5, txt("A RECUSA TINHA VENCIDO.", "anton", 130, WHITE), CX, 440, anim="zoom", fin=0.8)
A(492.6, 499.1, txt("UMA CASA PRÓPRIA", "anton", 150, WHITE), CX, 380, anim="up")
A(494.1, 499.1, txt("onde ninguém dissesse ao Vasco quem podia jogar", "serif_i", 58, OFF, shadow=False), CX, 540, anim="up")
T.bg(499.15, "dark", 29)
A(499.2, 510.1, txt("OS VASCAÍNOS SE MOBILIZARAM", "anton", 100, WHITE), CX, 200, anim="down")
for j, wd in enumerate(["TÍTULOS DE SÓCIO", "CAMPANHAS", "COMERCIANTES", "TRABALHADORES"]):
    A(503.3 + j * 1.3, 510.1, label(wd, 34, WHITE, (36, 36, 40) if j % 2 else RED), CX - 660 + j * 440, 470, anim="pop")
T.bg(510.2, "dark", 30)
counter(510.3, 518.4, CX - 430, 400, 685, ramp=1.6, size=200)
A(510.6, 518.4, txt("CONTOS DE RÉIS", "xb", 34, OFF, tracking=6), CX - 430, 560, anim="up")
A(511.0, 518.4, label("O TERRENO", 30), CX - 430, 640, anim="up")
counter(515.5, 518.4, CX + 430, 400, 2000, ramp=1.4, size=200, fmt="{:,d}")
A(515.8, 518.4, txt("CONTOS DE RÉIS", "xb", 34, OFF, tracking=6), CX + 430, 560, anim="up")
A(516.2, 518.4, label("A CONSTRUÇÃO", 30), CX + 430, 640, anim="up")

T.bg(518.4, "dark", 31)
fac = facade()


def facade_draw(tl, d):
    p = ease_io(tl / 2.2)
    if p >= 1:
        return fac
    im = fac.copy()
    m = Image.new("L", fac.size, 0)
    ImageDraw.Draw(m).rectangle((0, int(fac.height * (1 - p)), fac.width, fac.height), fill=255)
    im.putalpha(ImageChops.multiply(im.getchannel("A"), m))
    return im


A(518.4, 537.7, facade_draw, CX, 470, fin=0.3, kb=0.05)
A(518.6, 521.8, txt("21 · 04 · 1927", "anton", 110, WHITE, tracking=4), CX, 110, anim="down", z=3)
A(521.85, 526.3, txt("SÃO JANUÁRIO", "anton", 120, WHITE, tracking=4), CX, 110, anim="down", z=3)
A(526.35, 532.0, txt("O MAIOR ESTÁDIO DA AMÉRICA DO SUL", "anton", 80, WHITE), CX, 110, anim="down", z=3)
A(532.1, 537.7, txt("ATÉ 1930 · CENTENÁRIO, MONTEVIDÉU", "anton", 80, OFF), CX, 110, anim="down", z=3)
A(527.0, 537.7, label("SÓ SUPERADO PARA A PRIMEIRA COPA DO MUNDO", 26, WHITE, (40, 40, 44)), CX, 800, anim="up", z=3)
T.bg(537.75, "dark", 32)
A(537.8, 545.4, txt("ERGUIDO PELO POVO.", "anton", 170, WHITE), CX, 430, anim="zoom", fin=1.0, kb=0.04)
A(539.5, 545.4, txt("NENHUM MECENAS · NENHUM PRESENTE", "xb", 34, OFF, tracking=8), CX, 600, anim="up")
T.bg(545.5, "red", 33)
A(545.55, 552.0, stack([txt("A SEGUNDA", "anton", 120, WHITE), txt("RESPOSTA HISTÓRICA", "anton", 160, WHITE)], gap=-40),
  CX, 450, anim="zoom", fin=1.0, kb=0.05)

# ================================================================ 9. O LEGADO 552 – 604.9
chapter(552.0, 8, "O LEGADO", dur=2.8)
T.bg(553.8, "dark", 34)
A(554.9, 566.3, txt("NÃO FOI O PRIMEIRO A ESCALAR JOGADORES NEGROS", "anton", 70, (130, 130, 136)), CX, 330, anim="up")
A(558.65, 566.3, underline(txt("FOI O PRIMEIRO A LUTAR POR ELES", "anton", 110, WHITE), RED, 10), CX, 480, anim="up")
A(566.35, 575.1, rich([("DE POUCOS", (130, 130, 136)), ("  →  ", RED), ("DE TODOS", WHITE)], "anton", 150), CX, 430, anim="zoom", fin=1.0)
A(566.6, 575.1, txt("A ESCOLHA QUE MUDOU O FUTEBOL BRASILEIRO", "xb", 34, OFF, tracking=6), CX, 600, anim="up")
T.bg(575.15, "dark", 35)
A(575.3, 585.4, calendar_page(), CX - 420, 440, anim="up", fin=0.8)
A(575.8, 585.4, txt("DIA DA\nRESPOSTA HISTÓRICA", "anton", 96, WHITE, align="left", gap=104), CX - 150, 360, anim="left", anchor="l")
A(577.0, 585.4, txt("CALENDÁRIO OFICIAL DO RIO DE JANEIRO", "xb", 28, RED, tracking=4, shadow=False), CX - 126, 520, anim="left", anchor="l")
A(585.5, 590.1, book(), CX - 420, 440, anim="up", fin=0.7, z=4)
A(585.8, 590.1, txt("OS CAMISAS\nNEGRAS", "anton", 110, WHITE, align="left", gap=118), CX - 150, 360, anim="left", anchor="l")
A(586.3, 590.1, txt("inscritos no Livro dos Heróis e Heroínas da Pátria", "serif_i", 48, OFF, shadow=False, maxw=760, align="left"), CX - 126, 560, anim="left", anchor="l")
A(586.0, 590.1, rect(W, 160, (10, 10, 12, 0)), CX, 900)
T.bg(590.2, "dark", 36)
A(590.3, 604.9, trophy((90, 90, 96)), CX - 480, 420, anim="pop")
A(590.6, 604.9, txt("UMA TAÇA", "xb", 34, (110, 110, 116), tracking=6), CX - 480, 600, anim="up")
A(593.4, 604.9, x_mark(180, RED, 16), CX - 480, 420, anim="pop", z=3)
A(596.9, 604.9, letter_icon(WHITE), CX, 420, anim="pop")
A(597.1, 604.9, txt("UMA CARTA", "xb", 34, WHITE, tracking=6), CX, 600, anim="up")
A(598.4, 604.9, stadium_icon(RED), CX + 480, 420, anim="pop")
A(598.6, 604.9, txt("UM ESTÁDIO", "xb", 34, WHITE, tracking=6), CX + 480, 600, anim="up")
A(600.6, 604.9, txt("VITÓRIAS QUE NÃO CABEM NUM PLACAR", "anton", 76, WHITE), CX, 180, anim="down")

# ================================================================ 10. ENCERRAMENTO 604.9 – 624
sash(604.7)
T.bg(604.9, "dark", 37)
A(605.0, 619.4, medallion(380), CX - 470, 440, anim="pop", fin=0.6)
A(605.4, 612.5, stack([txt("ESSA HISTÓRIA", "anton", 96, WHITE, shadow=False), txt("TAMBÉM É SUA?", "anton", 96, RED, shadow=False)], gap=-26, align="left"),
  CX + 230, 340, anim="left")
btn = label("INSCREVA-SE", 46, WHITE, RED, padx=40, pady=18)
A(607.0, 619.4, btn, CX + 120, 560, anim="pop")
A(608.2, 619.4, label("DEIXE O LIKE", 30, WHITE, (40, 40, 44)), CX + 470, 560, anim="pop")
A(612.6, 619.4, stack([txt("CONTE NOS COMENTÁRIOS:", "xb", 30, RED, tracking=6, shadow=False),
                        txt("quando você descobriu a Resposta Histórica?", "serif_i", 52, WHITE, shadow=False, maxw=820)], gap=-4),
  CX + 230, 340, anim="up")
lt = canvas(760, 130)
ImageDraw.Draw(lt).rectangle((0, 0, 10, 130), fill=RED)
lt.alpha_composite(txt("ELIAS FERREIRA", "anton", 64, WHITE, shadow=False), (20, -6))
lt.alpha_composite(txt("NARRAÇÃO · VOZ VASCAÍNA", "xb", 24, OFF, tracking=6, shadow=False), (24, 76))
A(615.6, 619.4, lt, CX + 120, 720, anim="right", anchor="l")
T.bg(619.4, "black")
endt = Typer([dict(text="Vasco da Gama.", t0=619.7, t1=620.6, x=0, y=0, size=56, f="type_b", fill=OFF, cols=60),
              dict(text="Desde 1924, do lado certo da história.", t0=620.7, t1=622.4, x=0, y=80, size=44, fill=OFF, cols=60)],
             ink=OFF, page=(1020, 160))
A(619.5, 624.0, lambda tl, d: endt.sprite_at(619.5 + tl), CX, 520, fin=0.3, fout=0.8)

# ---------------------------------------------------------------- channel bug
bug = hstack([rect(6, 34, RED), txt("VOZ VASCAÍNA", "xb", 22, WHITE, tracking=6, shadow=False)], gap=10)
A(41.8, 604.5, bug, 70, 60, anchor="tl", fin=1.0, fout=0.5, z=55)

T.prepare()
