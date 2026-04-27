import os

# gonnx daemon
GONNX_BASE_URL = os.environ.get("GONNX_URL", "http://localhost:8080")

# model names registered in gonnx
GONNX_KOKORO  = os.environ.get("GONNX_KOKORO_MODEL",  "kokoro-tts")
GONNX_PIPER   = os.environ.get("GONNX_PIPER_MODEL",   "piper-ru-tts")
GONNX_SILERO  = os.environ.get("GONNX_SILERO_MODEL",  "silero-ru-tts")

SAMPLE_RATE    = int(os.environ.get("TTS_SAMPLE_RATE", "24000"))
DEFAULT_LANG   = os.environ.get("TTS_LANG",   "ru")
DEFAULT_VOICE  = os.environ.get("TTS_VOICE",  "xenia")
DEFAULT_OUTPUT = os.environ.get("TTS_OUTPUT", "playback")
