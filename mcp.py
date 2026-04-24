#!/usr/bin/env python3
import sys
import logging
import threading
from mcp.server.fastmcp import FastMCP
from app.tts import tts_engine
from app.config import DEFAULT_VOICE, DEFAULT_LANG, DEFAULT_OUTPUT

logging.basicConfig(stream=sys.stderr, level=logging.INFO)

mcp = FastMCP("tts-api")


@mcp.tool
def speak(
    text: str,
    lang: str = DEFAULT_LANG,
    voice: str = DEFAULT_VOICE,
    output: str = DEFAULT_OUTPUT,
) -> str:
    """
    Synthesize speech and play it on the audio output.
    Returns immediately; playback happens in the background.
    """
    if not text.strip():
        raise ValueError("text is required")

    threading.Thread(
        target=tts_engine.speak,
        kwargs={"text": text, "lang": lang, "voice": voice, "output": output},
        daemon=True,
    ).start()

    return "speaking"


@mcp.tool
def list_voices(lang: str = DEFAULT_LANG) -> list:
    """List available voices for the given language code."""
    return tts_engine.get_voices_for_language(lang)


@mcp.tool
def list_languages() -> list:
    """List supported language codes."""
    return tts_engine.get_available_languages()


if __name__ == "__main__":
    logging.info("TTS MCP server ready.")
    mcp.run(transport="stdio")
