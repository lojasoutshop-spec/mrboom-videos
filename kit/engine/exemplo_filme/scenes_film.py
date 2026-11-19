"""Vídeo-teste: filme 'Camisas Negras' (estreia 19/11/2026). Cenas ancoradas na SRT _legenda."""
import sys, re, unicodedata
sys.path.insert(0, "/home/claude/doc")
from engine import *
from art import *

SRT = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1].endswith(".srt") else "/home/claude/doc/film/work/legenda.srt"
DUR_AUDIO = float(open("/home/claude/doc/film/work/dur.txt").read())
DURATION = round(DUR_AUDIO + 3.0, 2)
T = Timeline(DURATION)
A = T.add
CX = W // 2
LOGO = Image.open("/home/claude/doc/brand/LOGO_VOZ_VASCAINA_800.png").convert("RGBA")


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9 ]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def ts(s):
    h, m, r = s.split(":"); sec, ms = r.split(",")
    return int(h) * 3600 + int(m) * 60 + int(sec) + int(ms) / 1000


SEGS = []
for b in open(SRT, encoding="utf-8-sig").read().strip().split("\n\n"):
    L = b.strip().split("\n")
    a, z = L[1].split(" --> ")
    SEGS.append((ts(a), ts(z), norm(" ".join(L[2:]))))
WORDSTREAM = []
for a, z, t in SEGS:
    ws = t.split()
    for i, w in enumerate(ws):
        WORDSTREAM.append((a + (z - a) * i / max(len(ws), 1), w))


def at(phrase, after=0.0):
    """Start time of the first occurrence of phrase (normalised words) after `after`."""
    p = norm(phrase).split()
    for i in range(len(WORDSTREAM) - len(p) + 1):
        if WORDSTREAM[i][0] < after:
            continue
        if all(WORDSTREAM[i + k][1] == p[k] for k in range(len(p))):
            return WORDSTREAM[i][0]
    raise ValueError("frase não encontrada: " + phrase)


def logo(size):
    return LOGO.resize((size, size), Image.LANCZOS)


def sash(t0, dur=0.75):
    def fn(tl, d):
        p = ease_io(tl / dur)
        im = canvas(W, H)
        dr = ImageDraw.Draw(im)
        x = -900 + p * (W + 1800)
        bw = 420
        dr.polygon([(x - bw / 2 + 300, -10), (x + bw / 2 + 300, -10), (x + bw / 2 - 300, H + 10), (x - bw / 2 - 300, H + 10)], fill=RED + (255,))
        x2 = x - bw - 30
        dr.polygon([(x2 - 60 + 300, -10), (x2 + 60 + 300, -10), (x2 + 60 - 300, H + 10), (x2 - 60 - 300, H + 10)], fill=WHITE + (255,))
        return im
    A(t0, t0 + dur, fn, 0, 0, anchor="tl", fin=0, fout=0, z=70)


def film_strip(w=1500, h=260):
    im = rect(w, h, (18, 18, 20), radius=6)
    d = ImageDraw.Draw(im)
    for x in range(20, w - 20, 60):
        d.rounded_rectangle((x, 14, x + 34, 38), radius=5, fill=(70, 70, 76))
        d.rounded_rectangle((x, h - 38, x + 34, h - 14), radius=5, fill=(70, 70, 76))
    for i in range(5):
        fx = 30 + i * ((w - 60) // 5)
        d.rectangle((fx + 8, 56, fx + (w - 60) // 5 - 8, h - 56), fill=(34, 34, 38), outline=(90, 90, 96), width=2)
    return im


def cast_card(actor, role, desc):
    im = rect(520, 340, (24, 24, 28), radius=8)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 10, 340), fill=RED)
    im.alpha_composite(silhouette((70, 70, 76), 90), (400, 40))
    im.alpha_composite(txt("ATOR", "xb", 20, GREY, tracking=6, shadow=False), (20, 16))
    im.alpha_composite(txt(actor, "anton", 56, WHITE, shadow=False), (20, 40))
    im.alpha_composite(txt("PERSONAGEM", "xb", 20, RED, tracking=6, shadow=False), (20, 130))
    im.alpha_composite(txt(role, "anton", 48, WHITE, shadow=False), (20, 154))
    im.alpha_composite(txt(desc, "m", 22, OFF, shadow=False, maxw=470, align="left"), (20, 226))
    return im


# ------------------------------------------------------------------ timeline
t_hook = 0.0
t_fala = at("fala torcida vascaina")
t_estreia = at("o longa estreia")
t_data = at("a data nao foi escolhida")
t_docu = at("camisas negras e um docudrama")
t_direcao = at("a direcao e de jefferson")
t_prod = at("e a producao e distribuicao")
t_reconst = at("o filme reconstroi")
t_reacao = at("e mostra tambem a reacao")
t_elenco = at("no elenco sergio malheiros")
t_juan = at("juan paiva interpreta")
t_mazzeo = at("e bruno mazzeo")
t_outros = at("o elenco tem ainda")
t_paises = at("a parte documental")
t_diretor = at("segundo o diretor")
t_pesquisa = at("foram dois anos")
t_pre = at("o filme ja teve")
t_expo = at("e quem estiver na cidade")
t_mais = at("para o vascaino camisas negras")
t_perder = at("a historia de quem preferiu")
t_cta = at("e voce ja vai ao cinema")
t_eu = at("eu sou elias ferreira")
END = DURATION

# HOOK
T.bg(0, "dark", 41)
A(0.2, t_hook + 4.0, txt("1923", "anton", 300, WHITE, tracking=8), CX, 430, anim="zoom", fin=1.0, kb=0.05)
words = ["OPERÁRIOS", "MOTORISTAS", "JOVENS NEGROS"]
for j, wd in enumerate(words):
    A(0.9 + j * 0.7, 6.4, txt(wd, "xb", 44, RED if j == 2 else OFF, tracking=8), CX - 520 + j * 520, 700, anim="up")
_j = jersey(); _j = _j.resize((int(_j.width * 0.8), int(_j.height * 0.8)), Image.LANCZOS)
T.bg(4.0, "dark", 42)
A(4.0, at("mais de cem anos"), _j, CX, 470, anim="zoom", fin=1.0, kb=0.05)
A(4.4, at("mais de cem anos"), txt("UMA CAMISA PRETA QUE MUDOU O FUTEBOL", "anton", 64, WHITE), CX, 880 - 40, anim="up", z=3)
t_mcem = at("mais de cem anos")
T.bg(t_mcem, "dark", 43)
A(t_mcem, t_fala, film_strip(), CX, 470, anim="right", dist=200, fin=1.0)
A(t_mcem + 0.3, t_fala, txt("MAIS DE 100 ANOS DEPOIS", "xb", 40, OFF, tracking=8), CX, 230, anim="down")
A(at("e chega hoje") - 0.2, t_fala, label("CHEGA AO CINEMA · HOJE", 54), CX, 760, anim="pop")

# TITLE
sash(t_fala - 0.25)
T.bg(t_fala, "dark", 44)
A(t_fala + 0.1, t_estreia, logo(170), CX, 120, anim="pop", fin=0.6)

# ESTREIA
T.bg(t_estreia, "dark", 45)


def cal(day, month, top=RED):
    im = rect(400, 440, (240, 236, 228), radius=16)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, 399, 110), radius=16, fill=top)
    d.rectangle((0, 90, 399, 110), fill=top)
    t = txt(month, "xb", 50, WHITE, tracking=8, shadow=False)
    im.alpha_composite(t, (200 - t.width // 2, 26))
    n = txt(day, "anton", 230, (20, 20, 22), shadow=False)
    im.alpha_composite(n, (200 - n.width // 2, 100))
    return soft_shadow(im)


A(t_estreia + 0.1, t_docu, cal("19", "NOVEMBRO"), CX - 420, 440, anim="up", fin=0.7)
A(t_estreia + 0.4, t_docu, txt("ESTREIA NOS\nCINEMAS DE\nTODO O BRASIL", "anton", 100, WHITE, align="left", gap=104), CX - 150, 400, anim="left", anchor="l")
A(t_data, t_docu, label("VÉSPERA DO DIA DA CONSCIÊNCIA NEGRA · 20/11", 30), CX, 790, anim="up")

# DOCUDRAMA
T.bg(t_docu, "dark", 46)
A(t_docu + 0.1, t_direcao, hstack([label("DRAMA", 60, WHITE, (40, 40, 44), padx=40, pady=20),
                                    txt("+", "anton", 120, RED), label("DOCUMENTÁRIO", 60, WHITE, RED, padx=40, pady=20)], gap=30),
  CX, 450, anim="pop")
A(t_direcao, t_reconst, stack([txt("DIREÇÃO E FOTOGRAFIA", "xb", 34, RED, tracking=10, shadow=False),
                                txt("JEFFERSON MELLO", "anton", 130, WHITE)], gap=0), CX, 380, anim="up")
A(t_prod, t_reconst, stack([txt("PRODUÇÃO E DISTRIBUIÇÃO", "xb", 30, GREY, tracking=10, shadow=False),
                             txt("TREMÈ PRODUÇÕES", "anton", 80, OFF)], gap=0), CX, 640, anim="up")

# HISTÓRIA
T.bg(t_reconst, "dark", 47)
A(t_reconst + 0.1, t_elenco, stack([txt("★", "black", 80, RED), txt("CARIOCA 1923", "anton", 140, WHITE),
                                     txt("1º TÍTULO DO VASCO", "xb", 34, OFF, tracking=8, shadow=False)], gap=-10), CX - 430, 430, anim="up")
A(t_reacao, t_elenco, stack([txt("★", "black", 80, RED), txt("RESPOSTA\nHISTÓRICA 1924", "anton", 100, WHITE, gap=104),
                              txt("A REAÇÃO DA ELITE", "xb", 34, OFF, tracking=8, shadow=False)], gap=-10), CX + 430, 430, anim="up")

# ELENCO
T.bg(t_elenco, "dark", 48)
A(t_elenco, t_paises, txt("ELENCO", "xb", 36, RED, tracking=14, shadow=False), CX, 110, anim="down")
A(t_elenco + 0.1, t_paises, cast_card("SÉRGIO MALHEIROS", "NELSON DA CONCEIÇÃO", "Goleiro, motorista, 1º goleiro negro do Vasco"), CX - 560, 380, anim="pop")
A(t_juan, t_paises, cast_card("JUAN PAIVA", "CECY", "Meia dos Camisas Negras"), CX, 380, anim="pop")
A(t_mazzeo, t_paises, cast_card("BRUNO MAZZEO", "JOSÉ AUGUSTO PRESTES", "Presidente que assinou a Resposta Histórica"), CX + 560, 380, anim="pop")
A(t_outros, t_paises, stack([txt("TAMBÉM NO ELENCO", "xb", 26, GREY, tracking=8, shadow=False),
                              txt("Aline Dias · Rodrigo Candelot · Brenno Leone · Thelmo Fernandes", "sb", 38, WHITE, shadow=False)], gap=0), CX, 720, anim="up")

# SEIS PAÍSES
T.bg(t_paises, "dark", 49)
A(t_paises, t_diretor + 0.3, txt("FILMADO EM 6 PAÍSES", "anton", 110, WHITE), CX, 200, anim="down")
paises = ["BRASIL", "ARGENTINA", "ESPANHA", "ITÁLIA", "ALEMANHA", "POLÔNIA"]
for i, pn in enumerate(paises):
    r, c = divmod(i, 3)
    A(t_paises + 1.2 + i * 0.45, t_diretor, label(pn, 40, WHITE, RED if i == 0 else (40, 40, 44), padx=34, pady=16), CX - 440 + c * 440, 420 + r * 120, anim="pop")
A(t_diretor, t_pre, stack([txt("RACISMO NO FUTEBOL:", "anton", 90, WHITE), txt("UM PROBLEMA GLOBAL", "anton", 90, RED)], gap=-20), CX, 470, anim="up", z=3)
A(t_pesquisa, t_pre, txt("2 ANOS DE PESQUISA · consultoria de Paulo César Vasconcellos", "sb", 34, OFF), CX, 700, anim="up", z=3)
A(t_diretor, t_pesquisa, rect(W, 600, (14, 14, 16, 235)), CX, 470, fin=0.4, z=2)
A(t_pesquisa, t_pre, rect(W, 600, (14, 14, 16, 235)), CX, 470, fin=0.01, z=2)

# PRÉ-ESTREIA E EXPOSIÇÃO
T.bg(t_pre, "dark", 50)
A(t_pre + 0.1, t_expo, cal("07", "NOVEMBRO", (40, 40, 44)), CX - 420, 440, anim="up")
A(t_pre + 0.4, t_expo, txt("PRÉ-ESTREIA\nCINE ODEON\nCENTRO DO RIO", "anton", 100, WHITE, align="left", gap=104), CX - 150, 400, anim="left", anchor="l")
A(t_expo, t_mais, txt("EXPOSIÇÃO GRATUITA", "anton", 110, WHITE), CX, 230, anim="down")
A(t_expo + 0.3, t_mais, label("SHOPPING LEBLON · ATÉ 30/11", 44), CX, 380, anim="pop")
for j, wd in enumerate(["UNIFORMES", "CHUTEIRAS", "BOLAS"]):
    A(t_expo + 1.5 + j * 0.6, t_mais, txt(wd, "anton", 80, OFF), CX - 500 + j * 500, 560, anim="up")
A(t_expo + 3.4, t_mais, txt("réplicas usadas nas filmagens", "serif_i", 52, GREY, shadow=False), CX, 680, anim="up")

# EMOÇÃO
T.bg(t_mais, "red", 51)
A(t_mais + 0.1, t_perder, txt("MAIS DO QUE\nUM FILME", "anton", 170, WHITE, gap=170), CX, 450, anim="zoom", fin=1.0, kb=0.05)
T.bg(t_perder, "dark", 52)
A(t_perder + 0.1, t_cta, stack([txt("PREFERIU PERDER UM CAMPEONATO", "anton", 90, OFF),
                                 rich([("A ", WHITE), ("ABANDONAR OS SEUS.", RED)], "anton", 110)], gap=-10), CX, 450, anim="zoom", fin=1.0)

# CTA
sash(t_cta - 0.25)
T.bg(t_cta, "dark", 53)
A(t_cta + 0.1, END, logo(400), CX - 470, 440, anim="pop", fin=0.6)
A(t_cta + 0.3, t_eu, stack([txt("JÁ VAI AO CINEMA?", "anton", 96, WHITE, shadow=False), txt("CONTA NOS COMENTÁRIOS", "xb", 36, RED, tracking=6, shadow=False)], gap=-6, align="left"),
  CX - 200, 360, anim="left", anchor="l")
A(t_cta + 2.0, END, label("INSCREVA-SE", 46, WHITE, RED, padx=40, pady=18), CX - 200 + 170, 540, anim="pop")
A(t_cta + 2.4, END, label("ATIVE O SININHO", 30, WHITE, (40, 40, 44)), CX + 400, 540, anim="pop")
lt = canvas(760, 130)
ImageDraw.Draw(lt).rectangle((0, 0, 10, 130), fill=RED)
lt.alpha_composite(txt("ELIAS FERREIRA", "anton", 64, WHITE, shadow=False), (20, -6))
lt.alpha_composite(txt("NARRAÇÃO · VOZ VASCAÍNA", "xb", 24, OFF, tracking=6, shadow=False), (24, 76))
A(t_eu, END, lt, CX - 200, 700, anim="right", anchor="l")

# bug
bug = hstack([logo(54), txt("VOZ VASCAÍNA", "xb", 22, WHITE, tracking=6, shadow=False)], gap=10)
A(t_estreia, t_cta - 0.3, bug, 50, 40, anchor="tl", fin=1.0, fout=0.5, z=55)

import json as _json
T.video_path = "/home/claude/doc/film/work/bg.mp4"
T.video_ranges = _json.load(open("/home/claude/doc/film/work/bg_ranges.json"))
T.prepare()
