import io
import os
import subprocess
import uuid
import wave
import numpy as np
from app.config import SAMPLE_RATE


class AudioService:
    def play(self, audio_data, output="playback"):
        """Play audio data via aplay (ALSA) or write to file."""
        if audio_data is None or len(audio_data) == 0:
            return

        pcm = (audio_data * 32767).astype(np.int16)

        if output == "file":
            import soundfile as sf
            out_dir = "audio_outputs"
            os.makedirs(out_dir, exist_ok=True)
            file_path = os.path.join(out_dir, f"{uuid.uuid4()}.wav")
            sf.write(file_path, audio_data, SAMPLE_RATE)
        else:
            buf = io.BytesIO()
            with wave.open(buf, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # int16 = 2 bytes
                wf.setframerate(SAMPLE_RATE)
                wf.writeframes(pcm.tobytes())
            subprocess.run(
                ["aplay", "-q"],
                input=buf.getvalue(),
                check=True,
            )


audio_service = AudioService()
