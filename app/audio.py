import os
import uuid
import numpy as np
import sounddevice as sd
from app.config import SAMPLE_RATE as DEFAULT_SAMPLE_RATE


class AudioService:
    def play(self, audio_data, output="playback", sample_rate=None):
        """Play audio data via sounddevice or write to file.

        Args:
            audio_data:  float32 numpy array normalised to [-1, 1]
            output:      'playback' | 'file'
            sample_rate: override default SAMPLE_RATE (e.g. Piper uses 22050)
        """
        if audio_data is None or len(audio_data) == 0:
            return

        rate = sample_rate if sample_rate is not None else DEFAULT_SAMPLE_RATE

        if output == "file":
            import soundfile as sf
            out_dir = "audio_outputs"
            os.makedirs(out_dir, exist_ok=True)
            file_path = os.path.join(out_dir, f"{uuid.uuid4()}.wav")
            sf.write(file_path, audio_data, rate)
        else:
            sd.play(audio_data.astype(np.float32), samplerate=rate)
            sd.wait()


audio_service = AudioService()
