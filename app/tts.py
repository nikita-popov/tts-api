import logging
import threading
from app.audio import audio_service
from app.config import (
    MODEL_PATH, VOICES_PATH, VOCAB_PATH,
    PIPER_MODEL_PATH, PIPER_CONFIG_PATH,
)

logger = logging.getLogger(__name__)

_KOKORO_LANGS = {"en", "br", "ja", "zh", "es", "fr", "hi", "it", "pt"}
_PIPER_LANGS  = {"ru-piper"}
_SILERO_LANGS = {"ru"}
_G2P_LANGS    = {"ja"}

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
        {"id": "aidar",   "name": "Aidar (Male)",    "gender": "male"},
        {"id": "baya",    "name": "Baya (Female)",   "gender": "female"},
        {"id": "kseniya", "name": "Kseniya (Female)","gender": "female"},
        {"id": "xenia",   "name": "Xenia (Female)",  "gender": "female"},
        {"id": "random",  "name": "Random",          "gender": "neutral"},
    ],
    "ru-piper": [
        {"id": "irina", "name": "Irina (Female)", "gender": "female"},
    ],
}

_g2p_cache     = {}
_g2p_lock      = threading.Lock()
_kokoro_engine = None
_piper_engine  = None
_silero_engine = None
_engine_lock   = threading.Lock()


def _get_kokoro():
    global _kokoro_engine
    if _kokoro_engine is not None:
        return _kokoro_engine
    with _engine_lock:
        if _kokoro_engine is None:
            from kokoro_onnx import Kokoro
            _kokoro_engine = Kokoro(MODEL_PATH, VOICES_PATH, vocab_config=VOCAB_PATH)
            logger.info("Kokoro engine loaded.")
    return _kokoro_engine


def _get_piper():
    global _piper_engine
    if _piper_engine is not None:
        return _piper_engine
    with _engine_lock:
        if _piper_engine is None:
            from app.piper import PiperEngine
            _piper_engine = PiperEngine(PIPER_MODEL_PATH, PIPER_CONFIG_PATH)
            logger.info("Piper engine loaded.")
    return _piper_engine


def _get_silero():
    global _silero_engine
    if _silero_engine is not None:
        return _silero_engine
    with _engine_lock:
        if _silero_engine is None:
            from app.silero import SileroEngine
            _silero_engine = SileroEngine()
            logger.info("Silero engine loaded.")
    return _silero_engine


def _get_g2p(lang):
    if lang in _g2p_cache:
        return _g2p_cache[lang]
    with _g2p_lock:
        if lang in _g2p_cache:
            return _g2p_cache[lang]
        if lang == "ja":
            from misaki.ja import JAG2P
            engine = JAG2P()
        else:
            raise ValueError(f"No G2P engine for language '{lang}'")
        _g2p_cache[lang] = engine
    return _g2p_cache[lang]


_speak_lock = threading.Lock()


class TTSEngine:
    def get_available_languages(self):
        return AVAILABLE_LANGUAGES

    def get_voices_for_language(self, lang_code):
        return [
            {"id": v["id"], "name": v["name"], "gender": v["gender"], "language": lang_code}
            for v in VOICES_BY_LANGUAGE.get(lang_code, [])
        ]

    def get_all_voices(self):
        return {lang: self.get_voices_for_language(lang) for lang in VOICES_BY_LANGUAGE}

    def validate_voice_for_language(self, voice_id, lang_code):
        return any(v["id"] == voice_id for v in VOICES_BY_LANGUAGE.get(lang_code, []))

    def speak(self, text, lang="en", voice="af_heart", output="playback", speed=1.0):
        all_langs = _KOKORO_LANGS | _PIPER_LANGS | _SILERO_LANGS
        if lang not in all_langs:
            raise ValueError(f"Language '{lang}' not supported")

        with _speak_lock:
            if lang in _SILERO_LANGS:
                silero = _get_silero()
                audio = silero.synthesize(text, speaker=voice, speed=speed)
                audio_service.play(audio, output=output,
                                   sample_rate=silero.sample_rate)

            elif lang in _PIPER_LANGS:
                piper = _get_piper()
                length_scale = 1.0 / max(speed, 0.1)
                audio = piper.synthesize(text, length_scale=length_scale)
                audio_service.play(audio, output=output,
                                   sample_rate=piper.sample_rate)

            else:
                kokoro = _get_kokoro()
                if lang in _G2P_LANGS:
                    g2p = _get_g2p(lang)
                    input_text = g2p(text)
                    is_phonemes = True
                else:
                    input_text = text
                    is_phonemes = False
                audio, _ = kokoro.create(
                    input_text,
                    voice=voice,
                    speed=speed,
                    is_phonemes=is_phonemes,
                )
                audio_service.play(audio, output=output)


tts_engine = TTSEngine()
