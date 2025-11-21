# TTS API

A simple REST API service for real-time text-to-speech synthesis using Kokoro-ONNX, built with Flask and Gunicorn. The service plays generated speech directly to audio output.

## Features

- Real-time streaming TTS - Audio playback starts immediately as sentences are generated;
- Sequential request processing - Thread-safe queue ensures clean audio output;
- Multiple voices - Gender-diverse voice options per language;
- REST API - Simple JSON endpoints with Swagger documentation;
- Systemd integration - Ready service deployment.

## Requirements

- Python 3.8+
- PortAudio library (libportaudio2)
- Audio output device (speakers/headphones)

## Installation

1. System Dependencies

```bash
sudo apt-get update
sudo apt-get install libportaudio2
```

2. Download Model Files

Download the following files from HuggingFace and place them in the `models/` directory:

- [kokoro-v1.0.onnx](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx)
- [voices-v1.0.bin](https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin)
- [config.json](https://huggingface.co/hexgrad/Kokoro-82M-v1.1-zh/raw/main/config.json) (vocabulary)

3. Setup Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

4. Running

- Directly:

```bash
source venv/bin/activate
gunicorn -w 1 -b 0.0.0.0:5000 run:app
```

Single worker (`-w 1`) prevents audio device conflicts.

- Systemd:

```ini
User=your_username
Group=your_username
WorkingDirectory=/path/to/tts_api
ExecStart=/path/to/tts_api/venv/bin/gunicorn ...
```

```bash
sudo cp tts.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tts.service
sudo systemctl start tts.service
```

### Usage example

```bash
curl -X POST "http://localhost:5000/v1/speak" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{  \"lang\": \"ja\",  \"text\": \"注意！火災警報！全員すぐに避難してください！\",  \"voice\": \"jf_alpha\"}"
```

## License

The project source code is licensed under the MIT license.

This project uses the Kokoro-82M model which is licensed under Apache 2.0.
Check the official repository for model-specific licensing.

## Credits

- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) - TTS model by hexgrad
- [kokoro-onnx](https://github.com/thewh1teagle/kokoro-onnx) - ONNX runtime implementation
