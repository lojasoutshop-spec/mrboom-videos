# Apresentador (avatar) do Voz Vascaína

Personagem fictício gerado por IA (Veo 3.1 no app Dark Planner, referência `[apresentador]`). Voz própria do Veo, aprovada pelo Elias em 19/11/2026.

## Clipes prontos
- `ABERTURA_GIRO.mp4`: 1280x720, 24 fps, 7,93 s. Fala: "Fala, vascaíno! Começa agora o Giro Vascaíno. Bora pras notícias do Gigante da Colina!" Fala de 1,03 s a 7,70 s.
- `ABERTURA_GIRO_legenda.ass`: legenda karaokê já cronometrada (estilo padrão branco/vermelho).

## Como usar no Giro diário
1. Abrir o Giro com `ABERTURA_GIRO.mp4`: fps=30, scale=1920:1080:flags=lanczos, unsharp=5:5:0.6, queimar `ABERTURA_GIRO_legenda.ass`.
2. Áudio do clipe: loudnorm I=-16, entra no mesmo esquema de ducking da trilha que a narração.
3. Crossfade de 0,5 s do clipe para a vinheta/primeira notícia; a narração do Paulo começa depois do clipe.
4. Mudar a data na vinheta de abertura todos os dias.

## Regras
- O apresentador é conteúdo sintético realista: no YouTube marcar "Conteúdo alterado ou sintético = Sim" (não afeta monetização). Na descrição: "Apresentador gerado por IA."
- Novos clipes só são gerados pelo Elias no app Dark Planner (desktop). Prompts sempre com `[apresentador]` entre colchetes, sem nomes de pessoas reais, sem adversários/polêmicas, sem crianças ou multidões (política de pessoas do Veo).
