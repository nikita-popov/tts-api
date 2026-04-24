import os

MODEL_PATH = os.environ.get("TTS_MODEL_PATH", "models/kokoro-v1.0.onnx")
VOICES_PATH = os.environ.get("TTS_VOICES_PATH", "models/voices-v1.0.bin")
VOCAB_PATH = os.environ.get("TTS_VOCAB_PATH", "models/config.json")
SAMPLE_RATE = int(os.environ.get("TTS_SAMPLE_RATE", "24000"))
DEFAULT_LANG = os.environ.get("TTS_LANG", "en")
DEFAULT_VOICE = os.environ.get("TTS_VOICE", "af_heart")
DEFAULT_OUTPUT = os.environ.get("TTS_OUTPUT", "playback")
