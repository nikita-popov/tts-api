import logging
import torch
import numpy as np

logger = logging.getLogger(__name__)

# Available speakers in v4_ru / v5_ru
SILERO_RU_SPEAKERS = ["aidar", "baya", "kseniya", "xenia", "random"]
SILERO_SAMPLE_RATE = 48000
SILERO_MODEL_ID = "v4_ru"  # v4_ru is stable; switch to v5_ru when available


class SileroEngine:
    """Silero TTS engine for Russian via torch.hub."""

    def __init__(self, model_id=SILERO_MODEL_ID, device="cpu"):
        logger.info("Loading Silero model %s on %s...", model_id, device)
        self.device = torch.device(device)
        self.model, _ = torch.hub.load(
            repo_or_dir="snakers4/silero-models",
            model="silero_tts",
            language="ru",
            speaker=model_id,
            trust_repo=True,
        )
        self.model.to(self.device)
        self.sample_rate = SILERO_SAMPLE_RATE
        logger.info("Silero model loaded. sample_rate=%d", self.sample_rate)

    def synthesize(self, text, speaker="xenia", speed=1.0):
        """Return float32 numpy array in [-1, 1].

        Args:
            text:    Input text (Russian)
            speaker: One of aidar / baya / kseniya / xenia / random
            speed:   Speech rate multiplier (0.5 slow … 2.0 fast)
        """
        if speaker not in SILERO_RU_SPEAKERS:
            logger.warning("Unknown speaker '%s', falling back to 'xenia'", speaker)
            speaker = "xenia"

        with torch.no_grad():
            audio = self.model.apply_tts(
                text=text,
                speaker=speaker,
                sample_rate=self.sample_rate,
                put_accent=True,
                put_yo=True,
            )

        audio_np = audio.cpu().numpy().astype(np.float32)

        # Speed adjustment via resampling (simple but clean)
        if abs(speed - 1.0) > 0.01:
            import scipy.signal as sps
            target_len = int(len(audio_np) / speed)
            audio_np = sps.resample(audio_np, target_len).astype(np.float32)

        return np.clip(audio_np, -1.0, 1.0)
