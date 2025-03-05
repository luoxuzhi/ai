import logging
from flask import Flask, request, Response
import requests
import json
from flask_cors import CORS

# 配置日志
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

# 用于存储每个用户每个会话的对话历史记录
# 结构：{user_id: {session_id: [messages]}}
conversation_history = {}

@app.route('/api/your-backend-endpoint', methods=['POST'])
def stream_response():
    data = request.json
    prompt = data.get('prompt', '')
    user_id = data.get('user_id')
    session_id = data.get('session_id')

    if not user_id or not session_id:
        return Response("Missing user_id or session_id", status=400)

    # 获取该用户该会话的对话历史记录，如果不存在则初始化
    user_sessions = conversation_history.get(user_id, {})
    history = user_sessions.get(session_id, [])

    # 将新的用户消息添加到历史记录中
    history.append({"role": "user", "content": prompt})

    api_url = "https://api.deepseek.com/v1/chat/completions"
    api_key = "sk-0e32ad43352d49698d40ed949e07741e"
    model = "deepseek-chat"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    data = {
        "model": model,
        "messages": history,
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
                            if content:
                                # 如果有回复内容，将其添加到对话历史记录中
                                history.append({"role": "assistant", "content": content})
                            yield content
                    except json.JSONDecodeError:
                        yield "Error decoding JSON"

    # 更新该用户该会话的对话历史记录
    user_sessions[session_id] = history
    conversation_history[user_id] = user_sessions

    return Response(generate(), content_type='text/plain')

@app.route('/api/get-user-sessions', methods=['POST'])
def get_user_sessions():
    data = request.json
    user_id = data.get('user_id')
    if not user_id:
        logging.error("Missing user_id in request")
        return Response("Missing user_id", status=400)
    try:
        user_sessions = conversation_history.get(user_id, {})
        logging.info(f"Fetched user sessions for user {user_id}: {user_sessions}")
        return json.dumps(user_sessions), 200, {'Content-Type': 'application/json'}
    except Exception as e:
        logging.error(f"Error fetching user sessions: {e}")
        return Response("Internal server error", status=500)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
