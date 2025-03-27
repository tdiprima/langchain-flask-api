# Saving chat histories across server restarts
from flask import Flask, jsonify, request
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Validate Azure OpenAI Environment Variables
required_vars = {
    "AZURE_OPENAI_API_KEY": "API key",
    "AZURE_OPENAI_API_ENDPOINT": "endpoint",
    "AZURE_OPENAI_API_VERSION": "API version",
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": "deployment name"
}

for var, desc in required_vars.items():
    if not os.getenv(var):
        raise ValueError(f"Missing {desc} in environment variables. Check your .env file.")

# Initialize Azure OpenAI Model
try:
    llm = AzureChatOpenAI(
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        temperature=0.7,
        max_tokens=500
    )
except Exception as e:
    raise RuntimeError(f"Failed to initialize AzureChatOpenAI: {str(e)}")

# Constants for persistence
HISTORY_DIR = "chat_histories"
HISTORY_FILE = os.path.join(HISTORY_DIR, "chat_histories.json")
os.makedirs(HISTORY_DIR, exist_ok=True)

# Initialize chat histories
chat_histories = {}
MAX_HISTORY_LENGTH = 10


def load_chat_histories():
    global chat_histories
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                chat_histories = json.load(f)
            print(f"Chat histories loaded from {HISTORY_FILE}")
            return True
        else:
            print(f"No chat history file found at {HISTORY_FILE}")
            return False
    except Exception as e:
        print(f"Error loading chat histories: {str(e)}")
        return False


load_chat_histories()


def save_chat_histories():
    try:
        serializable_histories = {}
        for session_id, history in chat_histories.items():
            serializable_histories[session_id] = history
        with open(HISTORY_FILE, 'w') as f:
            json.dump(serializable_histories, f, indent=2)
        print(f"Chat histories saved to {HISTORY_FILE}")
        return True
    except Exception as e:
        print(f"Error saving chat histories: {str(e)}")
        return False


@app.route('/save-histories', methods=['POST'])
def save_histories_endpoint():
    success = save_chat_histories()
    if success:
        return jsonify({"message": "Chat histories saved successfully", "status": "success"}), 200
    else:
        return jsonify({"message": "Failed to save chat histories", "status": "error"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)
