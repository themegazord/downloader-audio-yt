"""Interface de linha de comando do extrator de áudio, em formato de passo a passo."""

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


def _pedir_formato() -> str:
    formato = input(
        f"Passo 2/4 — Formato [{'/'.join(FORMATOS_SUPORTADOS)}] (padrão: mp3): "
    ).strip() or "mp3"
    if formato not in FORMATOS_SUPORTADOS:
        print("Formato inválido, usando mp3.")
        formato = "mp3"
    return formato


def _pedir_qualidade() -> str:
    return input("Passo 3/4 — Qualidade 0 (melhor) a 9 (pior) (padrão: 0): ").strip() or "0"


def _pedir_saida() -> str:
    return input("Passo 4/4 — Pasta de destino (padrão: ./downloads): ").strip() or "./downloads"


def _executar_wizard(url_inicial: str = "") -> None:
    print("=== Extrator de Áudio (YouTube / Twitter / Instagram / TikTok) ===")

    while True:
        url = url_inicial or input("Passo 1/4 — URL do vídeo: ").strip()
        url_inicial = ""  # só reaproveita a URL passada por argumento na 1ª volta
        if not url:
            print("Nenhuma URL informada. Encerrando.")
            return

        formato = _pedir_formato()
        qualidade = _pedir_qualidade()
        saida = _pedir_saida()

        _processar(url, formato, qualidade, saida)

        de_novo = input("\nBaixar outro vídeo? [s/N]: ").strip().lower()
        print()
        if de_novo not in ("s", "sim", "y", "yes"):
            break


def main() -> None:
    url_inicial = sys.argv[1] if len(sys.argv) > 1 else ""
    _executar_wizard(url_inicial)


if __name__ == "__main__":
    main()
