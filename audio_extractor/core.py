"""
Núcleo de extração de áudio.

Usa a biblioteca yt-dlp, que já implementa toda a "engenharia reversa" das
plataformas (extração de metadados, resolução de URLs assinadas, etc).
Aqui apenas orquestramos o fluxo.
"""

from pathlib import Path

import yt_dlp

FORMATOS_SUPORTADOS = ("mp3", "m4a", "wav", "opus")


def extrair_audio(url: str, formato: str = "mp3", qualidade: str = "0",
                   pasta_saida: str = "./downloads") -> Path:
    """
    Extrai apenas o stream de áudio de um vídeo.

    Etapas internas (feitas pelo yt-dlp):
    1. Requisita a página do vídeo e extrai o JSON de metadados embutido
    2. Lista todos os "formats" disponíveis (cada resolução/stream é um format)
    3. Filtra e escolhe o melhor stream de ÁUDIO apenas (não baixa vídeo)
    4. Baixa o stream bruto (geralmente .webm/opus ou .m4a/aac)
    5. Usa ffmpeg para converter pro formato pedido (mp3, wav, etc)

    Retorna o caminho da pasta de saída.
    """
    if formato not in FORMATOS_SUPORTADOS:
        raise ValueError(
            f"Formato '{formato}' não suportado. Use um de: {', '.join(FORMATOS_SUPORTADOS)}"
        )

    saida = Path(pasta_saida)
    saida.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        # 'bestaudio/best' = pega o melhor stream de ÁUDIO puro disponível;
        # se não houver um stream separado, cai pro melhor disponível
        "format": "bestaudio/best",

        # Pós-processamento: converte o áudio baixado pro formato desejado
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": formato,
            "preferredquality": qualidade,
        }],

        "outtmpl": f"{saida}/%(title)s.%(ext)s",
        "noplaylist": True,       # evita baixar playlist inteira por engano
        "quiet": False,
        "no_warnings": False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        print(f"Título: {info.get('title')}")
        print(f"Duração: {info.get('duration')}s")
        print(f"Extrator usado: {info.get('extractor')}")
        print("-" * 40)

        ydl.download([url])

    print("-" * 40)
    print(f"Concluído. Arquivo salvo em: {saida}/")
    return saida
