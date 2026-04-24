# TTS API

Text-to-speech service with two engines:
- **[Kokoro-ONNX](https://github.com/thewh1teagle/kokoro-onnx)** — English, Japanese and other languages
- **[Piper](https://github.com/rhasspy/piper)** — Russian (and any other language with a Piper model)

Exposes two interfaces: a **REST API** (Flask/Gunicorn) and an **MCP server** (stdio, JSON-RPC 2.0).

## Features

- Multi-engine routing — language determines the engine automatically
- Real-time streaming TTS — audio playback starts immediately as sentences are generated
- Sequential request processing — thread-safe lock ensures clean audio output
- Multiple voices — gender-diverse voice options per language
- REST API — JSON endpoints with Swagger UI (`/apidocs`)
- MCP server — native stdio transport, works with any MCP-compatible LLM client
- Configuration via ENV variables — no hardcoded paths or defaults
- Lazy engine loading — engines initialise on first use

## Requirements

- Python 3.8+
- PortAudio (`libportaudio2`)
- espeak-ng (required by Piper for phonemisation)
- Audio output device (speakers/headphones)

## Installation

### 1. System dependencies

```bash
sudo apt-get install libportaudio2 espeak-ng
```

### 2. Download model files

Place files into the `models/` directory.

#### Kokoro (English, Japanese, …)

| File | Source |
|---|---|
| `kokoro-v1.0.onnx` | [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx) |
| `voices-v1.0.bin` | [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin) |
| `config.json` | [Kokoro-82M-v1.1-zh on HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/raw/main/config.json) |

#### Piper (Russian)

Download `ru_RU-irina-medium.onnx` and its `.json` config from the
[Piper releases page](https://github.com/rhasspy/piper/releases) or from
[Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/main/ru/ru_RU/irina/medium):

```bash
cd models
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/ru/ru_RU/irina/medium/ru_RU-irina-medium.onnx.json
```

Any other Piper voice can be used by pointing the ENV variables to the corresponding files.

### 3. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

All settings are controlled via environment variables.

| Variable | Default | Description |
|---|---|---|
| `TTS_MODEL_PATH` | `models/kokoro-v1.0.onnx` | Kokoro ONNX model |
| `TTS_VOICES_PATH` | `models/voices-v1.0.bin` | Kokoro voices binary |
| `TTS_VOCAB_PATH` | `models/config.json` | Kokoro vocabulary config |
| `TTS_SAMPLE_RATE` | `24000` | Kokoro audio sample rate |
| `PIPER_MODEL_PATH` | `models/ru_RU-irina-medium.onnx` | Piper ONNX model |
| `PIPER_CONFIG_PATH` | `models/ru_RU-irina-medium.onnx.json` | Piper model config |
| `TTS_LANG` | `en` | Default language code |
| `TTS_VOICE` | `af_heart` | Default voice ID |
| `TTS_OUTPUT` | `playback` | Output mode: `playback` or `file` |

## Engine routing

The engine is selected automatically by language code:

| Language | Code | Engine |
|---|---|---|
| English | `en`, `br` | Kokoro |
| Japanese | `ja` | Kokoro |
| Russian | `ru` | Piper |

To add another language backed by Piper, add the model files and extend `_PIPER_LANGS` in `app/tts.py`.

## Running

### REST API

```bash
source venv/bin/activate
gunicorn -w 1 -b 0.0.0.0:5000 run:app
```

Single worker (`-w 1`) is required to avoid audio device conflicts.
Swagger UI is available at `http://localhost:5000/apidocs`.

```bash
# English (Kokoro)
curl -X POST http://localhost:5000/v1/speak \
  -H 'Content-Type: application/json' \
  -d '{"lang": "en", "text": "Hello, world!", "voice": "af_heart"}'

# Russian (Piper)
curl -X POST http://localhost:5000/v1/speak \
  -H 'Content-Type: application/json' \
  -d '{"lang": "ru", "text": "Привет, мир!"}'
```

### MCP server

```bash
source venv/bin/activate
python mcp.py
```

Configure your MCP client:

```json
{
  "mcpServers": {
    "tts": {
      "command": "/path/to/tts-api/venv/bin/python",
      "args": ["/path/to/tts-api/mcp.py"],
      "env": {
        "TTS_LANG": "en",
        "TTS_VOICE": "af_heart",
        "PIPER_MODEL_PATH": "/path/to/tts-api/models/ru_RU-irina-medium.onnx",
        "PIPER_CONFIG_PATH": "/path/to/tts-api/models/ru_RU-irina-medium.onnx.json"
      }
    }
  }
}
```

#### Available MCP tools

| Tool | Arguments | Description |
|---|---|---|
| `speak` | `text`, `lang?`, `voice?`, `output?` | Synthesize and play speech; returns immediately |
| `list_voices` | `lang?` | List voices for a language |
| `list_languages` | — | List supported language codes and engines |

## Systemd (REST API)

```ini
[Service]
User=your_username
WorkingDirectory=/path/to/tts-api
Environment=TTS_LANG=en
Environment=PIPER_MODEL_PATH=/path/to/tts-api/models/ru_RU-irina-medium.onnx
Environment=PIPER_CONFIG_PATH=/path/to/tts-api/models/ru_RU-irina-medium.onnx.json
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
Kokoro-82M model: Apache 2.0 — see the [official repository](https://huggingface.co/hexgrad/Kokoro-82M).
Piper voices: various open licenses — see individual model cards on [Hugging Face](https://huggingface.co/rhasspy/piper-voices).

## Credits

- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) — TTS model by hexgrad
- [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) — ONNX runtime implementation
- [Piper](https://github.com/rhasspy/piper) — fast local TTS by rhasspy
- [espeak-ng](https://github.com/espeak-ng/espeak-ng) — phonemisation for Piper
