from flask import Flask, request, Response
import requests
import json
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

@app.route('/your-backend-endpoint', methods=['POST'])
def stream_response():
    data = request.json
    prompt = data.get('prompt', '')

    api_url = "https://api.deepseek.com/v1/chat/completions"
    api_key = "sk-0e32ad43352d49698d40ed949e07741e"
    model = "deepseek-chat"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }

    response = requests.post(api_url, headers=headers, json=data, stream=True)

    def generate():
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith("data: "):
                    json_data = decoded_line[6:]
                    try:
                        message = json.loads(json_data)
                        if "choices" in message:
                            content = message["choices"][0]["delta"].get("content", "")
                            yield content
                    except json.JSONDecodeError:
                        yield "Error decoding JSON"

    return Response(generate(), content_type='text/plain')

if __name__ == '__main__':
    app.run(port=5000)