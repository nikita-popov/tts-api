import os

# Kokoro
MODEL_PATH   = os.environ.get("TTS_MODEL_PATH",  "models/kokoro-v1.0.onnx")
VOICES_PATH  = os.environ.get("TTS_VOICES_PATH", "models/voices-v1.0.bin")
VOCAB_PATH   = os.environ.get("TTS_VOCAB_PATH",  "models/config.json")
SAMPLE_RATE  = int(os.environ.get("TTS_SAMPLE_RATE", "24000"))

# Piper (Russian)
PIPER_MODEL_PATH  = os.environ.get("PIPER_MODEL_PATH",  "models/ru_RU-irina-medium.onnx")
PIPER_CONFIG_PATH = os.environ.get("PIPER_CONFIG_PATH", "models/ru_RU-irina-medium.onnx.json")

# Silero (Russian)
SILERO_MODEL_PATH = os.environ.get("SILERO_MODEL_PATH", "models/silero_tts.pt")

# Defaults
DEFAULT_LANG   = os.environ.get("TTS_LANG",   "ru")
DEFAULT_VOICE  = os.environ.get("TTS_VOICE",  "xenia")
DEFAULT_OUTPUT = os.environ.get("TTS_OUTPUT", "playback")
