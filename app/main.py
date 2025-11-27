from flask import Flask, request, jsonify
from flasgger import Swagger
from app.tts import tts_engine

app = Flask(__name__)

# Setup Swagger
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
              example: "Hello world. This is a real-time test."
            lang:
              type: string
              enum: [en, ja, ru]
              default: en
            voice:
              type: string
              default: af_heart
              description: Voice ID
            output:
              type: string
              default: playback
              description: Type of generated data.
    responses:
      200:
        description: Speech was played back successfully
      500:
        description: Generation error
    """
    data = request.json
    text = data.get('text')
    lang = data.get('lang', 'en')
    voice = data.get('voice', 'af_heart')
    output = data.get('output', 'playback')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        tts_engine.speak(text, lang=lang, voice=voice, output=output)
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
        schema:
          type: object
          properties:
            languages:
              type: array
              items:
                type: object
                properties:
                  code:
                    type: string
                    example: en
                  name:
                    type: string
                    example: English
    """
    try:
        languages = tts_engine.get_available_languages()
        return jsonify({"languages": languages}), 200
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
        description: Код языка (en, ja, ru)
        enum: [en, ja, ru]
    responses:
      200:
        description: List of voices for the specified language
        schema:
          type: object
          properties:
            language:
              type: string
              example: en
            voices:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                    example: af_heart
                  name:
                    type: string
                    example: Heart
                  language:
                    type: string
                    example: en
      400:
        description: The lang parameter is not specified
    """
    lang = request.args.get('lang')

    if not lang:
        return jsonify({"error": "Language parameter 'lang' is required"}), 400

    try:
        voices = tts_engine.get_voices_for_language(lang)
        return jsonify({
            "language": lang,
            "voices": voices
        }), 200
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
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
            model:
              type: string
              example: kokoro-v1.0
    """
    return jsonify({
        "status": "ok",
        "model": "kokoro-v1.0"
    }), 200


if __name__ == '__main__':
    app.run(debug=True)
