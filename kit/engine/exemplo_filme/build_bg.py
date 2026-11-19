"""Builds work/bg.mp4: stock-footage background track (1920x1080, 30fps) synced to the narration."""
import sys, subprocess, os, json
sys.argv = ["x", "/home/claude/doc/film/work/legenda.srt"]
sys.path.insert(0, "/home/claude/doc/film"); sys.path.insert(0, "/home/claude/doc")
import scenes_film as S
from PIL import Image
from engine import txt, stack, WHITE, RED, OFF

C = "/home/claude/doc/film/clips/"
W, H = 1920, 1080
END = S.DURATION

# poster shown on the keyed cinema screen
post = Image.new("RGB", (W, H), (8, 8, 9))
blk = stack([txt("CAMISAS NEGRAS", "anton", 230, WHITE, tracking=4), txt("NOS CINEMAS · 19 DE NOVEMBRO", "xb", 60, RED, tracking=10, shadow=False)], gap=-10)
blk = blk.resize((860, int(blk.height * 860 / blk.width)), Image.LANCZOS)
post.paste(blk, (960 - blk.width // 2, 555 - blk.height // 2), blk)
post.save("/home/claude/doc/film/work/poster.png")

# (start, clip, mode)  mode: bw / sepia / color / key / none(red engine bg)
segs = [
    (0.0, "pexels-15436959.mp4", "bw"),
    (4.0, "pixabay-236221.mp4", "bw"),
    (S.at("mais de cem anos"), "pixabay-144961.mp4", "color"),
    (S.t_fala, "pixabay-80685.mp4", "key"),
    (S.t_estreia, "pexels-7988642.mp4", "color"),
    (S.t_docu, "pixabay-55248.mp4", "color"),
    (S.t_reconst, "pexels-15436959.mp4", "bw"),
    (S.t_reacao, "pexels-34187599.mp4", "sepia"),
    (S.t_elenco, "pexels-7233729.mp4", "color"),
    (S.t_paises, "pixabay-205193.mp4", "color"),
    (S.t_diretor, "pexels-40059252.mp4", "bw"),
    (S.t_pre, "pexels-7988642.mp4", "color"),
    (S.t_expo, "pixabay-236221.mp4", "color"),
    (S.t_mais, None, "none"),
    (S.t_perder, "pixabay-43869.mp4", "sepia"),
    (S.t_cta, "pexels-40059252.mp4", "color"),
]
os.makedirs("/home/claude/doc/film/work/bg", exist_ok=True)
lst = []
ranges = []
for i, (t0, clip, mode) in enumerate(segs):
    t1 = segs[i + 1][0] if i + 1 < len(segs) else END
    # snap to frame grid
    f0, f1 = round(t0 * 30), round(t1 * 30)
    dur = (f1 - f0) / 30
    out = f"/home/claude/doc/film/work/bg/s{i:02d}.mp4"
    base = "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,setsar=1"
    look = {"bw": "hue=s=0,eq=brightness=-0.10:contrast=1.15",
            "sepia": "colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131,eq=brightness=-0.12",
            "color": "eq=brightness=-0.10:saturation=0.8",
            "key": "eq=saturation=0.9"}.get(mode, "")
    if mode == "none":
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=1920x1080:r=30:d={dur}",
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out]
    else:
        clipdur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", C + clip], capture_output=True, text=True).stdout)
        speed = max(min(clipdur / dur, 1.0), 0.6)  # slow down short clips (min 0.6x), loop if still short
        vf = f"setpts=PTS/{speed},{base},{look},vignette=PI/4"
        if mode == "key":
            fc = (f"[0:v]setpts=PTS/{speed},{base},colorkey=0x00ff00:0.35:0.12[k];"
                  f"[1:v]scale=1920:1080[p];[p][k]overlay=shortest=1,eq=brightness=-0.04,vignette=PI/4[o]")
            cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", C + clip, "-loop", "1", "-i", "/home/claude/doc/film/work/poster.png",
                   "-filter_complex", fc, "-map", "[o]", "-t", f"{dur}", "-r", "30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out]
        else:
            cmd = ["ffmpeg", "-v", "error", "-y", "-stream_loop", "-1", "-i", C + clip, "-vf", vf, "-t", f"{dur}", "-r", "30", "-an",
                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", out]
    subprocess.run(cmd, check=True)
    lst.append(f"file '{out}'")
    if mode != "none":
        ranges.append([f0, f1, mode])
open("/home/claude/doc/film/work/bg/list.txt", "w").write("\n".join(lst) + "\n")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "/home/claude/doc/film/work/bg/list.txt", "-c", "copy", "/home/claude/doc/film/work/bg.mp4"], check=True)
json.dump(ranges, open("/home/claude/doc/film/work/bg_ranges.json", "w"))
print("ok", len(segs), "segments")
