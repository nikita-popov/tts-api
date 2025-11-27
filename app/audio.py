import sounddevice as sd
import numpy as np

class AudioService:
    def __init__(self, sample_rate=24000):
        self.sample_rate = sample_rate
        # Audio initialization (you can select a device via sd.default.device)
        sd.default.samplerate = self.sample_rate

    def play(self, audio_data, output):
        """
        Plays audio data. Blocks execution until the end of the playback of the piece.
        """
        if audio_data is None or len(audio_data) == 0:
            return
        # Kokoro returns float32, sounddevice understands them
        if output_format == 'file':
            output_dir = 'audio_outputs'
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, f'{uuid.uuid4()}.wav')
            sf.write(file_path, audio_data, 24000)
            return jsonify({"status": "ok", "file_path": file_path})
        else:
            sd.play(audio_data, self.sample_rate, blocking=True)
            return jsonify({"status": "ok", "file_path": None})

# Global
audio_service = AudioService()
