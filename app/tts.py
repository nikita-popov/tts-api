import os
import re
import threading
from kokoro_onnx import Kokoro
#from misaki import ja, en, espeak
from misaki import ja
from app.audio import audio_service

# Маппинг языков на коды Kokoro
LANG_MAP = {
    'en': 'a',   # American English
    'br': 'b',   # British English
    'ja': 'j',   # Japanese
    'ru': 'r'    # Russian (если модель поддерживает)
}

# Определение доступных языков
AVAILABLE_LANGUAGES = [
    {"code": "en", "name": "English", "kokoro_code": "a"},
    {"code": "br", "name": "English", "kokoro_code": "b"},
    {"code": "ja", "name": "Japanese", "kokoro_code": "j"},
    {"code": "ru", "name": "Russian", "kokoro_code": "r"}
]


# Определение доступных голосов по языкам
# Формат: язык -> список голосов
VOICES_BY_LANGUAGE = {
    'en': [
        {"id": "af_heart", "name": "Heart (Female)", "gender": "female"},
        {"id": "af_bella", "name": "Bella (Female)", "gender": "female"},
        {"id": "af_nicole", "name": "Nicole (Female)", "gender": "female"},
        {"id": "af_sarah", "name": "Sarah (Female)", "gender": "female"},
        {"id": "af_sky", "name": "Sky (Female)", "gender": "female"},
        {"id": "am_adam", "name": "Adam (Male)", "gender": "male"},
        {"id": "am_michael", "name": "Michael (Male)", "gender": "male"},
        {"id": "bf_emma", "name": "Emma (British Female)", "gender": "female"},
        {"id": "bf_isabella", "name": "Isabella (British Female)", "gender": "female"},
        {"id": "bm_george", "name": "George (British Male)", "gender": "male"},
        {"id": "bm_lewis", "name": "Lewis (British Male)", "gender": "male"}
    ],
    'ja': [
        {"id": "af_heart", "name": "Heart (Female)", "gender": "female"},
        {"id": "af_bella", "name": "Bella (Female)", "gender": "female"},
        {"id": "af_sarah", "name": "Sarah (Female)", "gender": "female"},
        {"id": "am_adam", "name": "Adam (Male)", "gender": "male"},
        {"id": "am_michael", "name": "Michael (Male)", "gender": "male"}
    ],
    'ru': [
        {"id": "af_heart", "name": "Heart (Female)", "gender": "female"},
        {"id": "af_bella", "name": "Bella (Female)", "gender": "female"},
        {"id": "am_adam", "name": "Adam (Male)", "gender": "male"}
    ]
}


class TTSEngine:
    def __init__(self, model_path, voices_path, vocab_path):
        print(f"Loading Kokoro model from {model_path}...")
        self.model = Kokoro(model_path, voices_path, vocab_config=vocab_path)
        # Глобальный лок для последовательной обработки запросов от разных юзеров
        self.lock = threading.Lock()
        print("Model loaded.")

    def _split_text(self, text):
        """Разбивает текст на предложения для потокового воспроизведения"""
        # Простая разбивка по знакам препинания
        return re.split(r'(?<=[.!?])\s+', text)

    def get_available_languages(self):
        """Возвращает список поддерживаемых языков"""
        return AVAILABLE_LANGUAGES

    def get_voices_for_language(self, lang_code):
        """Возвращает список голосов для указанного языка"""
        if lang_code not in VOICES_BY_LANGUAGE:
            return []

        voices = []
        for voice in VOICES_BY_LANGUAGE[lang_code]:
            voices.append({
                "id": voice["id"],
                "name": voice["name"],
                "gender": voice["gender"],
                "language": lang_code
            })

        return voices

    def get_all_voices(self):
        """Возвращает все доступные голоса со всеми языками"""
        all_voices = {}
        for lang_code, voices in VOICES_BY_LANGUAGE.items():
            all_voices[lang_code] = [
                {
                    "id": voice["id"],
                    "name": voice["name"],
                    "gender": voice["gender"],
                    "language": lang_code
                }
                for voice in voices
            ]
        return all_voices

    def validate_voice_for_language(self, voice_id, lang_code):
        """Проверяет, доступен ли голос для указанного языка"""
        if lang_code not in VOICES_BY_LANGUAGE:
            return False
        return any(v["id"] == voice_id for v in VOICES_BY_LANGUAGE[lang_code])

    def speak(self, text, lang='en', voice='af_heart'):
        """
        Генерирует и воспроизводит речь.
        Блокирует поток до завершения всей речи.
        """
        k_lang = LANG_MAP.get(lang, 'a')

        # Misaki G2P with espeak-ng fallback
        gpg = {}
        if lang == 'ja':
            g2p = ja.JAG2P()
        elif lang == 'ja':
            fallback = espeak.EspeakFallback(british=False)
            g2p = en.G2P(trf=False, british=False, fallback=fallback)

        # Блокируем движок, чтобы другие запросы ждали своей очереди
        with self.lock:
            phonemes = g2p(text)
            audio, _ = self.model.create(
                phonemes,
                voice=voice,
                speed=1.0,
                is_phonemes=True
            )
            audio_service.play(audio)


MODEL_PATH = os.path.join("models", "kokoro-v1.0.onnx")
VOICES_PATH = os.path.join("models", "voices-v1.0.bin")
VOCAB_PATH = os.path.join("models", "config.json")


# Global instance
tts_engine = TTSEngine(MODEL_PATH, VOICES_PATH, VOCAB_PATH)
