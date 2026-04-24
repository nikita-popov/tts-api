import logging
import re
import threading
from kokoro_onnx import Kokoro
from misaki import ja
from app.audio import audio_service
from app.config import MODEL_PATH, VOICES_PATH, VOCAB_PATH

LANG_MAP = {
    "en": "a",
    "br": "b",
    "ja": "j",
    "ru": "r",
}

AVAILABLE_LANGUAGES = [
    {"code": "en", "name": "English",          "kokoro_code": "a"},
    {"code": "br", "name": "English (British)", "kokoro_code": "b"},
    {"code": "ja", "name": "Japanese",          "kokoro_code": "j"},
    {"code": "ru", "name": "Russian",           "kokoro_code": "r"},
]

VOICES_BY_LANGUAGE = {
    "en": [
        {"id": "af_heart",    "name": "Heart (Female)",           "gender": "female"},
        {"id": "af_bella",    "name": "Bella (Female)",           "gender": "female"},
        {"id": "af_nicole",   "name": "Nicole (Female)",          "gender": "female"},
        {"id": "af_sarah",    "name": "Sarah (Female)",           "gender": "female"},
        {"id": "af_sky",      "name": "Sky (Female)",             "gender": "female"},
        {"id": "am_adam",     "name": "Adam (Male)",              "gender": "male"},
        {"id": "am_michael",  "name": "Michael (Male)",           "gender": "male"},
        {"id": "bf_emma",     "name": "Emma (British Female)",    "gender": "female"},
        {"id": "bf_isabella", "name": "Isabella (British Female)","gender": "female"},
        {"id": "bm_george",   "name": "George (British Male)",    "gender": "male"},
        {"id": "bm_lewis",    "name": "Lewis (British Male)",     "gender": "male"},
    ],
    "ja": [
        {"id": "af_heart",   "name": "Heart (Female)",  "gender": "female"},
        {"id": "af_bella",   "name": "Bella (Female)",  "gender": "female"},
        {"id": "af_sarah",   "name": "Sarah (Female)",  "gender": "female"},
        {"id": "am_adam",    "name": "Adam (Male)",     "gender": "male"},
        {"id": "am_michael", "name": "Michael (Male)",  "gender": "male"},
    ],
    "ru": [
        {"id": "af_heart", "name": "Heart (Female)", "gender": "female"},
        {"id": "af_bella", "name": "Bella (Female)", "gender": "female"},
        {"id": "am_adam",  "name": "Adam (Male)",    "gender": "male"},
    ],
}

g2p_engines = {
    "ja": ja.G2P(fallback="espeak-ng"),
}

logger = logging.getLogger(__name__)


class TTSEngine:
    def __init__(self, model_path, voices_path, vocab_path):
        logger.info("Loading Kokoro model from %s...", model_path)
        self.model = Kokoro(model_path, voices_path, vocab_config=vocab_path)
        self.lock = threading.Lock()
        logger.info("Model loaded.")

    def get_available_languages(self):
        return AVAILABLE_LANGUAGES

    def get_voices_for_language(self, lang_code):
        return [
            {"id": v["id"], "name": v["name"], "gender": v["gender"], "language": lang_code}
            for v in VOICES_BY_LANGUAGE.get(lang_code, [])
        ]

    def get_all_voices(self):
        return {
            lang: self.get_voices_for_language(lang)
            for lang in VOICES_BY_LANGUAGE
        }

    def validate_voice_for_language(self, voice_id, lang_code):
        return any(v["id"] == voice_id for v in VOICES_BY_LANGUAGE.get(lang_code, []))

    def speak(self, text, lang="en", voice="af_heart", output="playback"):
        """Generate and play speech. Blocks until playback is done."""
        k_lang = LANG_MAP.get(lang, "a")
        g2p = g2p_engines.get(lang)

        if g2p is None:
            raise ValueError(f"Language '{lang}' not supported")

        with self.lock:
            phonemes = g2p(text)
            audio, _ = self.model.create(
                phonemes,
                voice=voice,
                speed=1.0,
                is_phonemes=True,
            )
            audio_service.play(audio, output=output)


tts_engine = TTSEngine(MODEL_PATH, VOICES_PATH, VOCAB_PATH)
