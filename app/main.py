from flask import Flask, request, jsonify
from flasgger import Swagger
from app.tts import tts_engine

app = Flask(__name__)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger = Swagger(app)


@app.route('/v1/speak', methods=['POST'])
def speak():
    """
    Speech generation and reproduction
    ---
    tags:
      - TTS
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              example: "Привет, мир!"
            lang:
              type: string
              enum: [en, br, ja, ru, ru-piper]
              default: en
              description: |
                Language code. ru = Silero (recommended), ru-piper = Piper fallback
            voice:
              type: string
              default: af_heart
              description: |
                Voice ID. For ru: aidar, baya, kseniya, xenia, random
            output:
              type: string
              enum: [playback, file]
              default: playback
            speed:
              type: number
              default: 1.0
              description: Speech speed multiplier (0.5 slow … 2.0 fast)
    responses:
      200:
        description: Speech was played back successfully
      500:
        description: Generation error
    """
    data = request.json
    text   = data.get('text')
    lang   = data.get('lang', 'en')
    voice  = data.get('voice', 'xenia' if data.get('lang') == 'ru' else 'af_heart')
    output = data.get('output', 'playback')
    speed  = float(data.get('speed', 1.0))

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        tts_engine.speak(text, lang=lang, voice=voice, output=output, speed=speed)
        return jsonify({"status": "success", "message": "Playback finished"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/languages', methods=['GET'])
def get_languages():
    """
    Get a list of available languages
    ---
    tags:
      - Languages
    responses:
      200:
        description: List of supported languages
    """
    try:
        return jsonify({"languages": tts_engine.get_available_languages()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/voices', methods=['GET'])
def get_voices():
    """
    Get a list of available voices for a language
    ---
    tags:
      - Voices
    parameters:
      - in: query
        name: lang
        type: string
        required: true
        enum: [en, br, ja, ru, ru-piper]
    responses:
      200:
        description: List of voices
      400:
        description: The lang parameter is not specified
    """
    lang = request.args.get('lang')
    if not lang:
        return jsonify({"error": "Language parameter 'lang' is required"}), 400
    try:
        voices = tts_engine.get_voices_for_language(lang)
        return jsonify({"language": lang, "voices": voices}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/health', methods=['GET'])
def health():
    """
    Service health check
    ---
    tags:
      - Health
    responses:
      200:
        description: Service OK
    """
    return jsonify({"status": "ok", "backend": "gonnx"}), 200


if __name__ == '__main__':
    app.run(debug=True)
