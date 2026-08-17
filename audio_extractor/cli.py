"""Interface de linha de comando do extrator de áudio."""

import argparse
import sys

import yt_dlp

from .core import extrair_audio, FORMATOS_SUPORTADOS


def _processar(url: str, formato: str, qualidade: str, saida: str) -> bool:
    try:
        extrair_audio(url, formato, qualidade, saida)
        return True
    except yt_dlp.utils.DownloadError as e:
        print(f"Erro ao processar a URL '{url}': {e}", file=sys.stderr)
        return False


def _modo_interativo() -> None:
    print("=== Extrator de Áudio (YouTube / Twitter / Instagram) ===")
    url = input("URL do vídeo: ").strip()
    if not url:
        print("Nenhuma URL informada. Encerrando.")
        return

    formato = input(
        f"Formato [{'/'.join(FORMATOS_SUPORTADOS)}] (padrão: mp3): "
    ).strip() or "mp3"
    if formato not in FORMATOS_SUPORTADOS:
        print(f"Formato inválido, usando mp3.")
        formato = "mp3"

    qualidade = input("Qualidade 0 (melhor) a 9 (pior) (padrão: 0): ").strip() or "0"
    saida = input("Pasta de destino (padrão: ./downloads): ").strip() or "./downloads"

    _processar(url, formato, qualidade, saida)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Extrai áudio de vídeos (YouTube, Twitter/X, Instagram) usando yt-dlp"
    )
    parser.add_argument("urls", nargs="*", help="URL(s) do(s) vídeo(s)")
    parser.add_argument("--formato", default="mp3", choices=FORMATOS_SUPORTADOS)
    parser.add_argument("--qualidade", default="0", help="0 (melhor) a 9 (pior), padrão VBR")
    parser.add_argument("--saida", default="./downloads", help="Pasta de destino")
    args = parser.parse_args()

    if not args.urls:
        _modo_interativo()
        return

    sucesso_geral = True
    for url in args.urls:
        if not _processar(url, args.formato, args.qualidade, args.saida):
            sucesso_geral = False

    sys.exit(0 if sucesso_geral else 1)


if __name__ == "__main__":
    main()
