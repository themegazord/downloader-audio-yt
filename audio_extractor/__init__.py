"""Pacote de extração de áudio de vídeos (YouTube, Twitter/X, Instagram) via yt-dlp."""

from .core import extrair_audio, FORMATOS_SUPORTADOS

__all__ = ["extrair_audio", "FORMATOS_SUPORTADOS"]
__version__ = "1.0.0"
