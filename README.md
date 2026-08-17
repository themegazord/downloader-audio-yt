# downloader-audio-yt

Extrator de áudio de vídeos (YouTube, Twitter/X, Instagram, TikTok) usando [yt-dlp](https://github.com/yt-dlp/yt-dlp).

A biblioteca `yt-dlp` já resolve toda a parte de extração de metadados e URLs
das plataformas. Este projeto organiza esse fluxo em um pequeno sistema em
Python com CLI e modo interativo.

## Como funciona

1. Requisita a página do vídeo e extrai o JSON de metadados embutido
2. Lista todos os "formats" disponíveis (cada resolução/stream é um format)
3. Filtra e escolhe o melhor stream de **áudio** apenas (não baixa vídeo)
4. Baixa o stream bruto (geralmente `.webm/opus` ou `.m4a/aac`)
5. Usa o `ffmpeg` para converter para o formato pedido (mp3, wav, etc.)

## Requisitos

- Python 3.9+
- [ffmpeg](https://ffmpeg.org/download.html) instalado e disponível no `PATH`
  (Windows: `winget install --id Gyan.FFmpeg -e`, depois abra um novo terminal)
- [Node.js](https://nodejs.org/) 20+ (usado para resolver desafios de assinatura
  do YouTube e gerar o PO Token — veja abaixo)

## Instalação

```bash
pip install -r requirements.txt
```

### PO Token do YouTube (necessário para downloads confiáveis)

O YouTube passou a exigir um "PO Token" para liberar a maioria dos streams de
áudio; sem ele os downloads podem falhar com `HTTP Error 403: Forbidden`. Este
projeto já usa o plugin [`bgutil-ytdlp-pot-provider`](https://github.com/Brainicism/bgutil-ytdlp-pot-provider)
(instalado via `requirements.txt`) para gerar esse token automaticamente
através de um servidor HTTP local.

Configure o servidor uma única vez:

```bash
git clone --single-branch --branch 1.3.1 https://github.com/Brainicism/bgutil-ytdlp-pot-provider.git ~/bgutil-ytdlp-pot-provider
cd ~/bgutil-ytdlp-pot-provider/server
npm ci
npx tsc
```

A partir daí, o próprio `audio_extractor` sobe o servidor (`node build/main.js`)
automaticamente em background na primeira vez que for necessário — não é
preciso rodá-lo manualmente. Se o Node.js ou o repositório clonado não forem
encontrados, o download segue sem o PO Token (pode falhar em alguns vídeos).

## Uso

O sistema conduz o download em 4 passos, perguntados um de cada vez no
terminal — não é preciso decorar nem passar flags:

```bash
python main.py
```

```
=== Extrator de Áudio (YouTube / Twitter / Instagram / TikTok) ===
Passo 1/4 — URL do vídeo: https://www.youtube.com/watch?v=XXXXXXXX
Passo 2/4 — Formato [mp3/m4a/wav/opus] (padrão: mp3):
Passo 3/4 — Qualidade 0 (melhor) a 9 (pior) (padrão: 0):
Passo 4/4 — Pasta de destino (padrão: ./downloads):
```

Ao final, ele pergunta se você quer baixar outro vídeo (`s`/`N`), então dá
pra encadear vários downloads na mesma execução.

Se preferir, pode passar a URL do Passo 1 direto como argumento — os demais
passos continuam sendo perguntados normalmente:

```bash
python main.py "https://www.youtube.com/watch?v=XXXXXXXX"
```

## Instalação como comando (opcional)

```bash
pip install -e .
audio-extractor "https://www.youtube.com/watch?v=XXXXXXXX"
```

## Aviso

Use apenas para baixar conteúdo que você tem direito de baixar (vídeos
próprios, de domínio público ou com licença que permita). Respeite os termos
de uso das plataformas.
