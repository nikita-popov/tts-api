import os
import uuid
import numpy as np
import sounddevice as sd
from app.config import SAMPLE_RATE


class AudioService:
    def play(self, audio_data, output="playback"):
        """Play audio data via sounddevice or write to file."""
        if audio_data is None or len(audio_data) == 0:
            return

        if output == "file":
            import soundfile as sf
            out_dir = "audio_outputs"
            os.makedirs(out_dir, exist_ok=True)
            file_path = os.path.join(out_dir, f"{uuid.uuid4()}.wav")
            sf.write(file_path, audio_data, SAMPLE_RATE)
        else:
            sd.play(audio_data.astype(np.float32), samplerate=SAMPLE_RATE)
            sd.wait()


audio_service = AudioService()
