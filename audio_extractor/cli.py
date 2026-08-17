"""Interface de linha de comando do extrator, em formato de passo a passo."""

import sys

import yt_dlp

from .core import (
    baixar_video,
    extrair_audio,
    FORMATOS_AUDIO_SUPORTADOS,
    FORMATOS_VIDEO_SUPORTADOS,
    QUALIDADES_VIDEO_SUPORTADAS,
)


def _processar(func, *args) -> bool:
    try:
        func(*args)
        return True
    except yt_dlp.utils.DownloadError as e:
        print(f"Erro ao processar a URL: {e}", file=sys.stderr)
        return False


def _pedir_tipo() -> str:
    while True:
        escolha = input(
            "Passo 2/5 — O que deseja baixar? [1] Áudio  [2] Vídeo (padrão: 1): "
        ).strip() or "1"
        if escolha in ("1", "audio", "áudio"):
            return "audio"
        if escolha in ("2", "video", "vídeo"):
            return "video"
        print("Opção inválida, digite 1 ou 2.")


def _pedir_formato_audio() -> str:
    formato = input(
        f"Passo 3/5 — Formato [{'/'.join(FORMATOS_AUDIO_SUPORTADOS)}] (padrão: mp3): "
    ).strip() or "mp3"
    if formato not in FORMATOS_AUDIO_SUPORTADOS:
        print("Formato inválido, usando mp3.")
        formato = "mp3"
    return formato


def _pedir_qualidade_audio() -> str:
    return input("Passo 4/5 — Qualidade 0 (melhor) a 9 (pior) (padrão: 0): ").strip() or "0"


def _pedir_qualidade_video() -> str:
    qualidade = input(
        f"Passo 3/5 — Qualidade máxima [{'/'.join(QUALIDADES_VIDEO_SUPORTADAS)}] (padrão: melhor): "
    ).strip().lower() or "melhor"
    if qualidade not in QUALIDADES_VIDEO_SUPORTADAS:
        print("Qualidade inválida, usando melhor.")
        qualidade = "melhor"
    return qualidade


def _pedir_formato_video() -> str:
    formato = input(
        f"Passo 4/5 — Formato [{'/'.join(FORMATOS_VIDEO_SUPORTADOS)}] (padrão: mp4): "
    ).strip() or "mp4"
    if formato not in FORMATOS_VIDEO_SUPORTADOS:
        print("Formato inválido, usando mp4.")
        formato = "mp4"
    return formato


def _pedir_saida() -> str:
    return input("Passo 5/5 — Pasta de destino (padrão: ./downloads): ").strip() or "./downloads"


def _executar_wizard(url_inicial: str = "") -> None:
    print("=== Extrator de Áudio e Vídeo (YouTube / Twitter / Instagram / TikTok) ===")

    while True:
        url = url_inicial or input("Passo 1/5 — URL do vídeo: ").strip()
        url_inicial = ""  # só reaproveita a URL passada por argumento na 1ª volta
        if not url:
            print("Nenhuma URL informada. Encerrando.")
            return

        tipo = _pedir_tipo()

        if tipo == "audio":
            formato = _pedir_formato_audio()
            qualidade = _pedir_qualidade_audio()
            saida = _pedir_saida()
            _processar(extrair_audio, url, formato, qualidade, saida)
        else:
            qualidade = _pedir_qualidade_video()
            formato = _pedir_formato_video()
            saida = _pedir_saida()
            _processar(baixar_video, url, qualidade, formato, saida)

        de_novo = input("\nBaixar outro vídeo? [s/N]: ").strip().lower()
        print()
        if de_novo not in ("s", "sim", "y", "yes"):
            break


def main() -> None:
    url_inicial = sys.argv[1] if len(sys.argv) > 1 else ""
    _executar_wizard(url_inicial)


if __name__ == "__main__":
    main()
