# Kit Voz Vascaína
- brand/: logo oficial SEM escudo (800 e master), banner 2560x1440
- engine/: motor de quadros (PIL) + legendas karaokê ASS (branco, varre vermelho) + trilha sintetizada + render por blocos em FFmpeg.
  scenes.py é o documentário "A Resposta Histórica" (exemplo de uso). Fontes usadas: Anton, Inter, Crimson Text, Courier 10 Pitch.
- Voz oficial: Dark Planner > Text to Speech > "Paulo - Expressive and Confident" (11Labs, PT-BR). Arquivos: NOME.mp3, NOME_legenda.srt, NOME_srtsyncpalavra.srt, NOME_srtsynctempo.srt
- YouTube Voz Vascaína: canal UCphgfipPcvqjYKZ79q6QYgQ (@vozvascainaoficial), conexão Zapier "YouTube #2". NUNCA usar a conexão padrão (MR. BOOM).

## Exemplo completo com vídeos de apoio (publicado em 19/11/2026: youtu.be/JtS5boO-zFY)
kit/engine/exemplo_filme/: scenes_film.py (cenas ancoradas nas frases da SRT _legenda via at("frase")), build_bg.py (monta bg.mp4 com clipes Pexels/Pixabay por trecho: preto e branco, sépia, cor, chroma key na tela verde), render_film.py (render em 2 blocos paralelos com legenda karaokê), make_subs_film.py.
engine.py tem VReader: Timeline.video_path + video_ranges usam o bg.mp4 como fundo (escurecido 0,62).
Mix que o Elias aprovou: trilha normalizada -16 LUFS, volume 0.42, sidechain ratio 2.5, final loudnorm -14 LUFS.
Vídeos de apoio: Dark Planner > Vídeos e Imagens (bancos Pexels/Pixabay, uso livre). Evitar faixas/bandeiras de outros clubes.
