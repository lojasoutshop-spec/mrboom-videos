import sys, os, subprocess, time
sys.path.insert(0, "/home/claude/doc/film"); sys.path.insert(0, "/home/claude/doc")
import scenes_film as S
from engine import FPS, W, H
ASS = "/home/claude/doc/film/work/karaoke.ass"
FD = "/usr/share/fonts/opentype/inter"
def preview(times):
    os.makedirs("/home/claude/doc/film/work/prev", exist_ok=True)
    for t in times:
        p=f"/home/claude/doc/film/work/prev/f_{t:07.2f}.png"
        S.T.frame(int(round(t*FPS))).save(p)
        subprocess.run(["ffmpeg","-v","error","-y","-i",p,"-vf",f"setpts=PTS+{t}/TB,ass={ASS}:fontsdir={FD}","-frames:v","1",p.replace('.png','_s.png')])
def chunk(f0,f1,path):
    tmp=path+".part.mp4"; t0=f0/FPS
    cmd=["ffmpeg","-v","error","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
         "-vf",f"setpts=PTS+{t0}/TB,ass={ASS}:fontsdir={FD},setpts=PTS-STARTPTS",
         "-c:v","libx264","-preset","veryfast","-crf","20","-maxrate","3500k","-bufsize","7000k","-pix_fmt","yuv420p","-r",str(FPS),tmp]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE); st=time.time()
    for fi in range(f0,f1): p.stdin.write(S.T.frame(fi).tobytes())
    p.stdin.close()
    if p.wait()==0: os.replace(tmp,path)
    print(path,f1-f0,"frames",round(time.time()-st),"s",flush=True)
if __name__=="__main__":
    if sys.argv[2]=="preview": preview([float(x) for x in sys.argv[3:]])
    else: chunk(int(sys.argv[3]),int(sys.argv[4]),sys.argv[5])
