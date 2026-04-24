import json
import logging
import numpy as np
import onnxruntime as ort
from phonemizer.backend import EspeakBackend

logger = logging.getLogger(__name__)


def _load_config(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


class PiperEngine:
    """Minimal Piper TTS engine using onnxruntime + phonemizer (espeak-ng)."""

    def __init__(self, model_path, config_path):
        logger.info("Loading Piper model from %s...", model_path)
        self.config = _load_config(config_path)
        self.sample_rate = self.config["audio"]["sample_rate"]
        self.sess = ort.InferenceSession(
            model_path,
            providers=["CPUExecutionProvider"],
        )
        self._espeak_voice = self.config.get("espeak", {}).get("voice", "ru")
        self._phoneme_to_id = self.config["phoneme_id_map"]
        self._num_speakers = self.config.get("num_speakers", 1)
        self._backend = EspeakBackend(
            self._espeak_voice,
            with_stress=True,
            language_switch="remove-flags",
        )
        logger.info("Piper model loaded. sample_rate=%d espeak_voice=%s",
                    self.sample_rate, self._espeak_voice)

    def _text_to_ids(self, text):
        """Phonemize text and convert to Piper phoneme id sequence."""
        phonemes = self._backend.phonemize([text], njobs=1)[0]
        p2i = self._phoneme_to_id
        bos = p2i.get("^", [1])[0]
        eos = p2i.get("$", [2])[0]
        ids = [bos]
        for ph in phonemes:
            ids += p2i.get(ph, [])
        ids.append(eos)
        return ids

    def synthesize(self, text, speaker_id=0, length_scale=1.0,
                   noise_scale=0.667, noise_w=0.8):
        """Return float32 numpy array in [-1, 1] ready for sounddevice/soundfile.

        Piper ONNX models output raw float32 audio directly — no int16 conversion
        needed. The /32768 normalisation applied to raw int16 must NOT be used here.
        """
        phoneme_ids = self._text_to_ids(text)
        inputs = {
            "input":         np.array([phoneme_ids], dtype=np.int64),
            "input_lengths": np.array([len(phoneme_ids)], dtype=np.int64),
            "scales":        np.array([noise_scale, length_scale, noise_w],
                                      dtype=np.float32),
        }
        if self._num_speakers > 1:
            inputs["sid"] = np.array([speaker_id], dtype=np.int64)

        audio = self.sess.run(None, inputs)[0].squeeze().astype(np.float32)
        # Clip to [-1, 1] to guard against rare OOB values from the model
        return np.clip(audio, -1.0, 1.0)
