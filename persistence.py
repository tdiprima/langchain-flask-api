from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Constants
HISTORY_DIR = "chat_history"
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")
MAX_HISTORY_LENGTH = 10
chat_histories = {}

# Validate Azure OpenAI credentials
required_vars = {
    "AZURE_OPENAI_API_KEY": "API key",
    "AZURE_OPENAI_API_ENDPOINT": "endpoint",
    "AZURE_OPENAI_API_VERSION": "API version",
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": "deployment name"
}
for var, desc in required_vars.items():
    if not os.getenv(var):
        raise ValueError(f"Missing {desc} in environment variables!")

# Initialize Azure OpenAI client
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    temperature=0.7
)

# Ensure history directory exists
os.makedirs(HISTORY_DIR, exist_ok=True)

# Persistence functions
def save_chat_histories():
    try:
        serializable_histories = {sid: hist for sid, hist in chat_histories.items()}
        with open(HISTORY_FILE, 'w') as f:
            json.dump(serializable_histories, f, indent=2)
        print(f"Chat histories saved to {HISTORY_FILE}")
        return True
    except Exception as e:
        print(f"Error saving chat histories: {e}")
        return False

def load_chat_histories():
    global chat_histories
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                chat_histories = json.load(f)
            print(f"Chat histories loaded from {HISTORY_FILE}")
            return True
        print(f"No chat history file found at {HISTORY_FILE}")
        return False
    except Exception as e:
        print(f"Error loading chat histories: {e}")
        return False

# Load histories on startup
load_chat_histories()

# Endpoints
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Missing 'question'"}), 400
    question = data['question']
    session_id = data.get('session_id', 'default_session')
    
    if session_id not in chat_histories:
        chat_histories[session_id] = []
    
    response = llm.invoke(question)
    chat_histories[session_id].append({
        "question": question,
        "answer": response.content,
        "timestamp": str(datetime.now())
    })
    
    if len(chat_histories[session_id]) > MAX_HISTORY_LENGTH:
        chat_histories[session_id] = chat_histories[session_id][-MAX_HISTORY_LENGTH:]
    
    save_chat_histories()
    return jsonify({"answer": response.content, "history": chat_histories[session_id]}), 200

@app.route('/save-histories', methods=['POST'])
def save_histories_endpoint():
    success = save_chat_histories()
    return jsonify({"message": "Chat histories saved" if success else "Failed to save", "status": "success" if success else "error"}), 200 if success else 500

if __name__ == '__main__':
    app.run(port=3000, debug=True)
