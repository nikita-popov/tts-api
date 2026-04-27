import logging
import httpx
from app.audio import audio_service
from app.config import (
    GONNX_BASE_URL,
    GONNX_KOKORO, GONNX_PIPER, GONNX_SILERO,
    DEFAULT_LANG, DEFAULT_VOICE,
)

logger = logging.getLogger(__name__)

_KOKORO_LANGS = {"en", "br", "ja", "zh", "es", "fr", "hi", "it", "pt"}
_PIPER_LANGS  = {"ru-piper"}
_SILERO_LANGS = {"ru"}

AVAILABLE_LANGUAGES = [
    {"code": "en",       "name": "English",           "engine": "kokoro"},
    {"code": "br",       "name": "English (British)",  "engine": "kokoro"},
    {"code": "ja",       "name": "Japanese",           "engine": "kokoro"},
    {"code": "ru",       "name": "Russian (Silero)",   "engine": "silero"},
    {"code": "ru-piper", "name": "Russian (Piper)",    "engine": "piper"},
]

VOICES_BY_LANGUAGE = {
    "en": [
        {"id": "af_heart",    "name": "Heart (Female)",            "gender": "female"},
        {"id": "af_bella",    "name": "Bella (Female)",            "gender": "female"},
        {"id": "af_nicole",   "name": "Nicole (Female)",           "gender": "female"},
        {"id": "af_sarah",    "name": "Sarah (Female)",            "gender": "female"},
        {"id": "af_sky",      "name": "Sky (Female)",              "gender": "female"},
        {"id": "am_adam",     "name": "Adam (Male)",               "gender": "male"},
        {"id": "am_michael",  "name": "Michael (Male)",            "gender": "male"},
        {"id": "bf_emma",     "name": "Emma (British Female)",     "gender": "female"},
        {"id": "bf_isabella", "name": "Isabella (British Female)", "gender": "female"},
        {"id": "bm_george",   "name": "George (British Male)",     "gender": "male"},
        {"id": "bm_lewis",    "name": "Lewis (British Male)",      "gender": "male"},
    ],
    "br": [
        {"id": "bf_emma",     "name": "Emma (Female)",    "gender": "female"},
        {"id": "bf_isabella", "name": "Isabella (Female)", "gender": "female"},
        {"id": "bm_george",   "name": "George (Male)",    "gender": "male"},
        {"id": "bm_lewis",    "name": "Lewis (Male)",     "gender": "male"},
    ],
    "ja": [
        {"id": "jf_alpha",      "name": "Alpha (Female)",      "gender": "female"},
        {"id": "jf_gongitsune", "name": "Gongitsune (Female)", "gender": "female"},
        {"id": "jm_kumo",       "name": "Kumo (Male)",         "gender": "male"},
    ],
    "ru": [
        {"id": "aidar",   "name": "Aidar (Male)",     "gender": "male"},
        {"id": "baya",    "name": "Baya (Female)",    "gender": "female"},
        {"id": "kseniya", "name": "Kseniya (Female)", "gender": "female"},
        {"id": "xenia",   "name": "Xenia (Female)",   "gender": "female"},
        {"id": "random",  "name": "Random",           "gender": "neutral"},
    ],
    "ru-piper": [
        {"id": "irina", "name": "Irina (Female)", "gender": "female"},
    ],
}


def _predict(model_name: str, payload: dict) -> dict:
    url = f"{GONNX_BASE_URL}/v1/models/{model_name}:predict"
    with httpx.Client(timeout=60.0) as client:
        resp = client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()


class TTSEngine:
    def speak(self, text: str, lang: str = None, voice: str = None,
              output: str = "playback", speed: float = 1.0):
        lang  = lang  or DEFAULT_LANG
        voice = voice or DEFAULT_VOICE

        if lang in _KOKORO_LANGS:
            result = _predict(GONNX_KOKORO, {
                "text": text, "voice": voice, "lang": lang, "speed": speed,
            })
        elif lang in _PIPER_LANGS:
            result = _predict(GONNX_PIPER, {"text": text})
        elif lang in _SILERO_LANGS:
            result = _predict(GONNX_SILERO, {
                "text": text, "voice": voice, "speed": speed,
            })
        else:
            raise ValueError(f"Unsupported language: {lang}")

        audio_service.play(result, output=output)

    def get_available_languages(self):
        return AVAILABLE_LANGUAGES

    def get_voices_for_language(self, lang: str):
        return VOICES_BY_LANGUAGE.get(lang, [])


tts_engine = TTSEngine()
