from flask import Flask, request, jsonify
from flasgger import Swagger
from app.tts import tts_engine

app = Flask(__name__)

# Настройка Swagger
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
    Генерация и воспроизведение речи
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
              description: Идентификатор голоса из voices.json
    responses:
      200:
        description: Речь воспроизведена успешно
      500:
        description: Ошибка генерации
    """
    data = request.json
    text = data.get('text')
    lang = data.get('lang', 'en')
    voice = data.get('voice', 'af_heart')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        tts_engine.speak(text, lang=lang, voice=voice)
        return jsonify({"status": "success", "message": "Playback finished"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/v1/languages', methods=['GET'])
def get_languages():
    """
    Получить список доступных языков
    ---
    tags:
      - Languages
    responses:
      200:
        description: Список поддерживаемых языков
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
    Получить список доступных голосов для языка
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
        description: Список голосов для указанного языка
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
        description: Не указан параметр lang
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
    Проверка работоспособности сервиса
    ---
    tags:
      - Health
    responses:
      200:
        description: Сервис работает
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
