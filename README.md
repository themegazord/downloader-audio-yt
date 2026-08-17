# downloader-audio-yt

Extrator de áudio de vídeos (YouTube, Twitter/X, Instagram) usando [yt-dlp](https://github.com/yt-dlp/yt-dlp).

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

## Instalação

```bash
pip install -r requirements.txt
```

## Uso

### Modo direto (linha de comando)

```bash
python main.py "https://www.youtube.com/watch?v=XXXXXXXX" --formato mp3 --qualidade 0 --saida ./downloads
```

Também aceita múltiplas URLs de uma vez:

```bash
python main.py "URL_1" "URL_2" "URL_3" --formato m4a
```

### Modo interativo

Rode sem argumentos para responder as perguntas no terminal:

```bash
python main.py
```

### Opções

| Opção         | Padrão        | Descrição                                    |
|---------------|---------------|-----------------------------------------------|
| `--formato`   | `mp3`         | `mp3`, `m4a`, `wav` ou `opus`                  |
| `--qualidade` | `0`           | `0` (melhor) a `9` (pior), VBR                 |
| `--saida`     | `./downloads` | Pasta onde os arquivos serão salvos            |

## Instalação como comando (opcional)

```bash
pip install -e .
audio-extractor "https://www.youtube.com/watch?v=XXXXXXXX"
```

## Aviso

Use apenas para baixar conteúdo que você tem direito de baixar (vídeos
próprios, de domínio público ou com licença que permita). Respeite os termos
de uso das plataformas.
