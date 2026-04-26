# TTS API

Text-to-speech service with three engines:
- **[Silero TTS v4](https://github.com/snakers4/silero-models)** — Russian, high quality, 48 kHz
- **[Kokoro-ONNX](https://github.com/thewh1teagle/kokoro-onnx)** — English, Japanese and other languages
- **[Piper](https://github.com/rhasspy/piper)** — Russian fallback (`ru-piper`)

Exposes two interfaces: a **REST API** (Flask/Gunicorn) and an **MCP server** (stdio, JSON-RPC 2.0).

## Features

- Multi-engine routing — language determines the engine automatically
- Sequential request processing — thread-safe lock ensures clean audio output
- Multiple voices — gender-diverse voice options per language
- Speed control — `speed` parameter (0.5 slow … 2.0 fast)
- REST API — JSON endpoints with Swagger UI (`/apidocs`)
- MCP server — native stdio transport, works with any MCP-compatible LLM client
- Configuration via ENV variables — no hardcoded paths or defaults
- Lazy engine loading — engines initialise on first use

## Engine routing

| Language | Code | Engine | Voices | Hz |
|---|---|---|---|---|
| English | `en`, `br` | Kokoro | af_heart, af_bella, … | 24000 |
| Japanese | `ja` | Kokoro | jf_alpha, jm_kumo, … | 24000 |
| Russian | `ru` | **Silero v4** | aidar, baya, kseniya, xenia, random | 48000 |
| Russian (fallback) | `ru-piper` | Piper | irina | 22050 |

## Requirements

- Python 3.8+
- PortAudio (`libportaudio2`)
- espeak-ng (required by Piper phonemiser, used for `ru-piper`)
- Audio output device

> **Note:** Silero model is downloaded automatically via `torch.hub` on first run
> and cached in `~/.cache/torch/hub`. Internet access is required once.

## Installation

### 1. System dependencies

```bash
sudo apt-get install libportaudio2 espeak-ng
```

### 2. Download model files

See [`models/README.md`](models/README.md) for download instructions.

### 3. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

| Variable | Default | Description |
|---|---|---|
| `TTS_MODEL_PATH` | `models/kokoro-v1.0.onnx` | Kokoro ONNX model |
| `TTS_VOICES_PATH` | `models/voices-v1.0.bin` | Kokoro voices binary |
| `TTS_VOCAB_PATH` | `models/config.json` | Kokoro vocabulary config |
| `TTS_SAMPLE_RATE` | `24000` | Kokoro audio sample rate |
| `PIPER_MODEL_PATH` | `models/ru_RU-irina-medium.onnx` | Piper ONNX model |
| `PIPER_CONFIG_PATH` | `models/ru_RU-irina-medium.onnx.json` | Piper model config |
| `TTS_LANG` | `ru` | Default language code |
| `TTS_VOICE` | `xenia` | Default voice ID |
| `TTS_OUTPUT` | `playback` | Output mode: `playback` or `file` |

## Running

### REST API

```bash
source venv/bin/activate
gunicorn -w 1 -b 0.0.0.0:5000 run:app
```

Single worker (`-w 1`) is required to avoid audio device conflicts.  
Swagger UI: `http://localhost:5000/apidocs`

```bash
# Russian — Silero v4 (default)
curl -X POST http://localhost:5000/v1/speak \
  -H 'Content-Type: application/json' \
  -d '{"text": "Привет, мир!"}'

# Russian — slower speech
curl -X POST http://localhost:5000/v1/speak \
  -H 'Content-Type: application/json' \
  -d '{"text": "Привет!", "speed": 0.85}'

# Russian — Piper fallback
curl -X POST http://localhost:5000/v1/speak \
  -H 'Content-Type: application/json' \
  -d '{"lang": "ru-piper", "text": "Привет, мир!"}'

# English — Kokoro
curl -X POST http://localhost:5000/v1/speak \
  -H 'Content-Type: application/json' \
  -d '{"lang": "en", "text": "Hello, world!", "voice": "af_heart"}'
```

#### Request parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `text` | string | **required** | Text to synthesize |
| `lang` | string | `ru` | Language code |
| `voice` | string | `xenia` | Voice ID |
| `output` | string | `playback` | `playback` or `file` |
| `speed` | float | `1.0` | Speed multiplier (0.5 … 2.0) |

### MCP server

```bash
source venv/bin/activate
python server.py
```

Configure your MCP client:

```json
{
  "mcpServers": {
    "tts": {
      "command": "/path/to/tts-api/venv/bin/python",
      "args": ["/path/to/tts-api/server.py"]
    }
  }
}
```

#### Available MCP tools

| Tool | Arguments | Description |
|---|---|---|
| `tts_speak` | `text`, `lang?`, `voice?`, `output?`, `speed?` | Synthesize and play speech |
| `tts_list_voices` | `lang?` | List voices for a language |
| `tts_list_languages` | — | List supported language codes and engines |

## Systemd (REST API)

```ini
[Service]
User=your_username
WorkingDirectory=/path/to/tts-api
ExecStart=/path/to/tts-api/venv/bin/gunicorn -w 1 -b 0.0.0.0:5000 run:app
Restart=on-failure
```

```bash
sudo cp tts.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tts.service
```

## License

Source code: MIT.  
Kokoro-82M model: Apache 2.0 — see [official repository](https://huggingface.co/hexgrad/Kokoro-82M).  
Silero models: MIT — see [snakers4/silero-models](https://github.com/snakers4/silero-models).  
Piper voices: various open licenses — see individual model cards on [Hugging Face](https://huggingface.co/rhasspy/piper-voices).

## Credits

- [Silero TTS](https://github.com/snakers4/silero-models) — high-quality Russian TTS by snakers4
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) — TTS model by hexgrad
- [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) — ONNX runtime implementation
- [Piper](https://github.com/rhasspy/piper) — fast local TTS by rhasspy
- [espeak-ng](https://github.com/espeak-ng/espeak-ng) — phonemisation backend
