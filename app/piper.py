import json
import logging
import numpy as np
import onnxruntime as ort

logger = logging.getLogger(__name__)

# Piper phoneme type constants
_PHONEME_TYPE_ESPEAK = 1


def _load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


class PiperEngine:
    """Minimal Piper TTS engine using onnxruntime directly."""

    def __init__(self, model_path, config_path):
        logger.info("Loading Piper model from %s...", model_path)
        self.config = _load_config(config_path)
        self.sample_rate = self.config["audio"]["sample_rate"]
        self.sess = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],
        )
        # espeak-ng is required for phonemization
        import espeak_phonemizer
        self._phonemizer = espeak_phonemizer
        self._voice = self.config.get("espeak", {}).get("voice", "ru")
        logger.info("Piper model loaded. sample_rate=%d", self.sample_rate)

    def _phonemize(self, text):
        """Convert text to espeak phoneme ids via espeak-ng."""
        phonemes = self._phonemizer.phonemize(
            text,
            voice=self._voice,
            with_stress=True,
        )
        phoneme_to_id = self.config["phoneme_id_map"]
        pad = phoneme_to_id.get("_", [0])[0]
        bos = phoneme_to_id.get("^", [1])[0]
        eos = phoneme_to_id.get("$", [2])[0]
        ids = [bos]
        for ph in phonemes:
            ids += phoneme_to_id.get(ph, [])
        ids.append(eos)
        return ids

    def synthesize(self, text, speaker_id=0, length_scale=1.0,
                   noise_scale=0.667, noise_w=0.8):
        """Return float32 numpy array normalised to [-1, 1]."""
        phoneme_ids = self._phonemize(text)
        phoneme_ids_arr = np.array([phoneme_ids], dtype=np.int64)
        phoneme_ids_len = np.array([len(phoneme_ids)], dtype=np.int64)
        scales = np.array([noise_scale, length_scale, noise_w], dtype=np.float32)

        inputs = {
            "input": phoneme_ids_arr,
            "input_lengths": phoneme_ids_len,
            "scales": scales,
        }
        num_speakers = self.config.get("num_speakers", 1)
        if num_speakers > 1:
            inputs["sid"] = np.array([speaker_id], dtype=np.int64)

        audio = self.sess.run(None, inputs)[0].squeeze()  # shape: (samples,)
        # Piper outputs int16 range floats; normalise to [-1, 1]
        audio = audio / 32768.0
        return audio.astype(np.float32)
