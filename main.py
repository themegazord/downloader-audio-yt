#!/usr/bin/env python3
"""Ponto de entrada: python main.py <URL> [--formato mp3|m4a|wav|opus] [--qualidade 0-9]"""

from audio_extractor.cli import main

if __name__ == "__main__":
    main()
