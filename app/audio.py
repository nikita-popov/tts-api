import base64
import io
import os
import uuid

import sounddevice as sd
import soundfile as sf

from app.config import SAMPLE_RATE as DEFAULT_SAMPLE_RATE


class AudioService:
    def play(self, result: dict, output: str = "playback"):
        """Play audio from a gonnx predict response.

        Args:
            result:  dict with keys 'audio_b64' (base64 WAV) and
                     optionally 'sample_rate'
            output:  'playback' | 'file'
        """
        audio_b64 = result.get("audio_b64")
        if not audio_b64:
            raise ValueError("gonnx response missing 'audio_b64'")

        wav_bytes = base64.b64decode(audio_b64)
        data, sample_rate = sf.read(io.BytesIO(wav_bytes), dtype="float32")

        if output == "file":
            out_dir = "audio_outputs"
            os.makedirs(out_dir, exist_ok=True)
            file_path = os.path.join(out_dir, f"{uuid.uuid4()}.wav")
            sf.write(file_path, data, sample_rate)
        else:
            sd.play(data, samplerate=sample_rate)
            sd.wait()


audio_service = AudioService()
