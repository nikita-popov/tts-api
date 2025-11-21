import sounddevice as sd
import numpy as np

class AudioService:
    def __init__(self, sample_rate=24000):
        self.sample_rate = sample_rate
        # Инициализация аудио (можно выбрать устройство через sd.default.device)
        sd.default.samplerate = self.sample_rate

    def play(self, audio_data):
        """
        Воспроизводит аудиоданные. Блокирует выполнение до конца проигрывания куска.
        """
        if audio_data is None or len(audio_data) == 0:
            return
        # Kokoro возвращает float32, sounddevice их понимает
        sd.play(audio_data, self.sample_rate, blocking=True)

# Глобальный инстанс
audio_service = AudioService()
