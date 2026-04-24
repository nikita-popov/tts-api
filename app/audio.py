import sounddevice as sd
from app.config import SAMPLE_RATE


class AudioService:
    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        sd.default.samplerate = self.sample_rate

    def play(self, audio_data, output="playback"):
        """Play audio data. Blocks until playback is complete."""
        if audio_data is None or len(audio_data) == 0:
            return

        if output == "file":
            import os
            import uuid
            import soundfile as sf
            output_dir = "audio_outputs"
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")
            sf.write(file_path, audio_data, self.sample_rate)
        else:
            sd.play(audio_data, self.sample_rate, blocking=True)


audio_service = AudioService()
