"""
Núcleo de extração de áudio e vídeo.

Usa a biblioteca yt-dlp, que já implementa toda a "engenharia reversa" das
plataformas (extração de metadados, resolução de URLs assinadas, etc).
Aqui apenas orquestramos o fluxo.
"""

import shutil
import subprocess
import time
import urllib.request
from pathlib import Path

import yt_dlp

FORMATOS_AUDIO_SUPORTADOS = ("mp3", "m4a", "wav", "opus")
FORMATOS_VIDEO_SUPORTADOS = ("mp4", "mkv", "webm")
QUALIDADES_VIDEO_SUPORTADAS = ("melhor", "1080p", "720p", "480p", "360p")

# O YouTube exige um "PO Token" para liberar os streams de áudio/vídeo para a
# maioria dos clients. O plugin bgutil-ytdlp-pot-provider (instalado junto
# com este projeto) gera esse token através de um servidor HTTP local. Sem
# ele, o download pode falhar com "HTTP Error 403: Forbidden".
_POT_SERVER_URL = "http://127.0.0.1:4416"
_POT_SERVER_DIR = Path.home() / "bgutil-ytdlp-pot-provider" / "server"


def _pot_server_ativo(timeout: float = 0.5) -> bool:
    try:
        with urllib.request.urlopen(f"{_POT_SERVER_URL}/ping", timeout=timeout):
            return True
    except OSError:
        return False


def _iniciar_pot_server_se_preciso() -> None:
    """Sobe o servidor local de PO Token em background, se ainda não estiver rodando."""
    if _pot_server_ativo():
        return

    main_js = _POT_SERVER_DIR / "build" / "main.js"
    node = shutil.which("node")
    if not node or not main_js.exists():
        return  # segue sem o servidor; alguns extractors/clients ainda funcionam sem PO Token

    subprocess.Popen(
        [node, str(main_js)],
        cwd=str(_POT_SERVER_DIR),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0),
    )

    for _ in range(20):
        if _pot_server_ativo():
            break
        time.sleep(0.5)


# Alguns sites (TikTok, Instagram) bloqueiam requisições automatizadas e só
# funcionam com uma sessão de login real. Se existir um cookies.txt na pasta
# atual (exportado do navegador — veja o README), ele é usado automaticamente.
_COOKIES_FILE = Path.cwd() / "cookies.txt"


def _ydl_opts_base(saida: Path) -> dict:
    opts = {
        "outtmpl": f"{saida}/%(title)s.%(ext)s",
        "noplaylist": True,       # evita baixar playlist inteira por engano
        "quiet": False,
        "no_warnings": False,

        # Necessário para o YouTube resolver desafios de assinatura/PO Token
        "js_runtimes": {"deno": {}, "node": {}},
        "remote_components": ["ejs:github"],
    }
    if _COOKIES_FILE.exists():
        opts["cookiefile"] = str(_COOKIES_FILE)
    return opts


def _baixar(url: str, ydl_opts: dict, saida: Path) -> Path:
    _iniciar_pot_server_se_preciso()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Uma única extração (metadados + download) — extrair duas vezes gera
        # duas sessões distintas e a segunda pode perder o PO Token obtido
        # na primeira, causando HTTP 403 no download.
        info = ydl.extract_info(url, download=True)
        print(f"Título: {info.get('title')}")
        print(f"Duração: {info.get('duration')}s")
        print(f"Extrator usado: {info.get('extractor')}")
        print("-" * 40)

    print("-" * 40)
    print(f"Concluído. Arquivo salvo em: {saida}/")
    return saida


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
    if formato not in FORMATOS_AUDIO_SUPORTADOS:
        raise ValueError(
            f"Formato '{formato}' não suportado. Use um de: {', '.join(FORMATOS_AUDIO_SUPORTADOS)}"
        )

    saida = Path(pasta_saida)
    saida.mkdir(parents=True, exist_ok=True)

    ydl_opts = {
        **_ydl_opts_base(saida),
        # 'bestaudio/best' = pega o melhor stream de ÁUDIO puro disponível;
        # se não houver um stream separado, cai pro melhor disponível
        "format": "bestaudio/best",

        # Pós-processamento: converte o áudio baixado pro formato desejado
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": formato,
            "preferredquality": qualidade,
        }],
    }

    return _baixar(url, ydl_opts, saida)


def baixar_video(url: str, qualidade: str = "melhor", formato: str = "mp4",
                  pasta_saida: str = "./downloads") -> Path:
    """
    Baixa o vídeo completo (vídeo + áudio) de uma URL.

    'qualidade' limita a resolução máxima ("melhor", "1080p", "720p", ...);
    o yt-dlp junta o melhor stream de vídeo e de áudio disponíveis dentro
    desse limite e usa ffmpeg para juntá-los no contêiner pedido em 'formato'.

    Retorna o caminho da pasta de saída.
    """
    if qualidade not in QUALIDADES_VIDEO_SUPORTADAS:
        raise ValueError(
            f"Qualidade '{qualidade}' não suportada. Use uma de: {', '.join(QUALIDADES_VIDEO_SUPORTADAS)}"
        )
    if formato not in FORMATOS_VIDEO_SUPORTADOS:
        raise ValueError(
            f"Formato '{formato}' não suportado. Use um de: {', '.join(FORMATOS_VIDEO_SUPORTADOS)}"
        )

    saida = Path(pasta_saida)
    saida.mkdir(parents=True, exist_ok=True)

    # Restringe a video em H.264 (avc1) + áudio em AAC (m4a) sempre que
    # possível: são os únicos codecs que Windows, WhatsApp e a maioria dos
    # players tocam sem precisar instalar codec extra (ex.: HEVC/AV1/VP9,
    # que costumam ser os "melhores" streams do YouTube, mas exigem um
    # codec pago no Windows e falham ao enviar pelo WhatsApp).
    limite_altura = f"[height<={qualidade.rstrip('p')}]" if qualidade != "melhor" else ""
    format_selector = (
        f"bestvideo[vcodec^=avc1]{limite_altura}+bestaudio[acodec^=mp4a]"
        f"/best[vcodec^=avc1]{limite_altura}"
        f"/bestvideo{limite_altura}+bestaudio"
        f"/best{limite_altura}"
    )

    ydl_opts = {
        **_ydl_opts_base(saida),
        "format": format_selector,
        "merge_output_format": formato,
        # Reforça a preferência por H.264/AAC dentro de cada candidato do seletor acima
        "format_sort": ["vcodec:h264", "acodec:aac"],
    }

    return _baixar(url, ydl_opts, saida)
