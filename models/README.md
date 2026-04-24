# Model Files

Place all model files in this directory (`models/`).

---

## Silero TTS v4 (Russian — `ru`)

Downloaded **automatically** via `torch.hub` on first use (~50 MB).  
No manual action required.

---

## Kokoro ONNX (English, Japanese, … — `en`, `br`, `ja`, …)

Three files required:

```bash
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
wget https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
wget https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/raw/main/config.json
```

| File | Description |
|---|---|
| `kokoro-v1.0.onnx` | Main TTS model |
| `voices-v1.0.bin` | Voice embeddings |
| `config.json` | Vocabulary / phoneme config |

---

## Piper ONNX (Russian fallback — `ru-piper`)

```bash
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json
```

| File | Description |
|---|---|
| `ru_RU-irina-medium.onnx` | Piper ONNX model |
| `ru_RU-irina-medium.onnx.json` | Phoneme ID map and audio config |

Other Piper voices can be used by pointing `PIPER_MODEL_PATH` / `PIPER_CONFIG_PATH`  
to the corresponding files. All voices are available at  
[huggingface.co/rhasspy/piper-voices](https://huggingface.co/rhasspy/piper-voices).

---

## Expected directory layout

```
models/
├── config.json
├── kokoro-v1.0.onnx
├── voices-v1.0.bin
├── ru_RU-irina-medium.onnx
└── ru_RU-irina-medium.onnx.json
```

Silero files are stored in the `torch.hub` cache (`~/.cache/torch/hub/`) and do not appear here.
