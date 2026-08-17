"""Pacote de extração de áudio/vídeo de vídeos (YouTube, Twitter/X, Instagram, TikTok) via yt-dlp."""

from .core import (
    baixar_video,
    extrair_audio,
    FORMATOS_AUDIO_SUPORTADOS,
    FORMATOS_VIDEO_SUPORTADOS,
    QUALIDADES_VIDEO_SUPORTADAS,
)

__all__ = [
    "extrair_audio",
    "baixar_video",
    "FORMATOS_AUDIO_SUPORTADOS",
    "FORMATOS_VIDEO_SUPORTADOS",
    "QUALIDADES_VIDEO_SUPORTADAS",
]
__version__ = "1.1.0"
