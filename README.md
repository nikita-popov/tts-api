# TTS API

Text-to-speech service built on [Kokoro-ONNX](https://github.com/thewh1teagle/kokoro-onnx).
Exposes two interfaces: a **REST API** (Flask/Gunicorn) and an **MCP server** (FastMCP over stdio).

## Features

- Real-time streaming TTS — audio playback starts immediately as sentences are generated
- Sequential request processing — thread-safe lock ensures clean audio output
- Multiple voices — gender-diverse voice options per language
- REST API — JSON endpoints with Swagger UI (`/apidocs`)
- MCP server — native stdio transport, works with any MCP-compatible LLM client
- Configuration via ENV variables — no hardcoded paths or defaults

## Requirements

- Python 3.8+
- PortAudio (`libportaudio2`)
- Audio output device (speakers/headphones)

## Installation

### 1. System dependencies

```bash
sudo apt-get install libportaudio2
```

### 2. Download model files

Place the following files into the `models/` directory:

| File | Source |
|---|---|
| `kokoro-v1.0.onnx` | [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx) |
| `voices-v1.0.bin` | [kokoro-onnx releases](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin) |
| `config.json` | [Kokoro-82M-v1.1-zh on HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/raw/main/config.json) |

### 3. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

All settings are controlled via environment variables. Defaults work out of the box if model files are in `models/`.

| Variable | Default | Description |
|---|---|---|
| `TTS_MODEL_PATH` | `models/kokoro-v1.0.onnx` | Path to ONNX model |
| `TTS_VOICES_PATH` | `models/voices-v1.0.bin` | Path to voices binary |
| `TTS_VOCAB_PATH` | `models/config.json` | Path to vocabulary config |
| `TTS_SAMPLE_RATE` | `24000` | Audio sample rate |
| `TTS_LANG` | `en` | Default language code |
| `TTS_VOICE` | `af_heart` | Default voice ID |
| `TTS_OUTPUT` | `playback` | Output mode: `playback` or `file` |

## Running

### REST API

```bash
source venv/bin/activate
gunicorn -w 1 -b 0.0.0.0:5000 run:app
```

Single worker (`-w 1`) is required to avoid audio device conflicts.
Swagger UI is available at `http://localhost:5000/apidocs`.

```bash
# Example request
curl -X POST http://localhost:5000/v1/speak \
  -H 'Content-Type: application/json' \
  -d '{"lang": "ja", "text": "注意！火災警報！", "voice": "jf_alpha"}'
```

### MCP server

```bash
source venv/bin/activate
python mcp.py
```

The server speaks JSON-RPC 2.0 over stdio. Configure your MCP client:

```json
{
  "mcpServers": {
    "tts": {
      "command": "/path/to/tts-api/venv/bin/python",
      "args": ["/path/to/tts-api/mcp.py"],
      "env": {
        "TTS_LANG": "en",
        "TTS_VOICE": "af_heart"
      }
    }
  }
}
```

#### Available MCP tools

| Tool | Arguments | Description |
|---|---|---|
| `speak` | `text`, `lang?`, `voice?`, `output?` | Synthesize and play speech; returns `"speaking"` immediately |
| `list_voices` | `lang?` | List voices for a language |
| `list_languages` | — | List supported language codes |

## Systemd (REST API)

```ini
[Service]
User=your_username
WorkingDirectory=/path/to/tts-api
Environment=TTS_LANG=en
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

## Credits

- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) — TTS model by hexgrad
- [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) — ONNX runtime implementation
