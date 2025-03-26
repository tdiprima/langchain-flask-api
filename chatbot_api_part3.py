# Required imports
import json
import os
import uuid
from datetime import datetime
from functools import wraps
from dotenv import load_dotenv
from flask import Flask, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from langchain_openai import AzureChatOpenAI

# Load environment variables
load_dotenv()

# Constants
HISTORY_DIR = "chat_histories"
HISTORY_FILE = os.path.join(HISTORY_DIR, "chat_histories.json")
USERS_FILE = os.path.join(HISTORY_DIR, "users.json")
SECRET_KEY = os.urandom(24)
MAX_HISTORY_LENGTH = 10

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Create directories if they don't exist
os.makedirs(HISTORY_DIR, exist_ok=True)

# Initialize Azure OpenAI client
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    temperature=0.7,
    max_tokens=500
)

from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Initialize the chain
chain = ConversationChain(
    llm=llm,
    memory=ConversationBufferMemory()
)

# Load and save chat histories
def save_chat_histories():
    with open(HISTORY_FILE, 'w') as f:
        json.dump(chat_histories, f, indent=2)

def load_chat_histories():
    global chat_histories
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            chat_histories = json.load(f)
    else:
        chat_histories = {}

chat_histories = {}
load_chat_histories()

# User management functions
def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    return {}

users = load_users()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if username in users:
        return jsonify({"error": "Username already exists"}), 400

    users[username] = {'password_hash': generate_password_hash(password), 'sessions': []}
    save_users(users)
    return jsonify({"message": f"User {username} registered successfully", "status": "success"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data['username']
    password = data['password']

    if username not in users or not check_password_hash(users[username]['password_hash'], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session_id = str(uuid.uuid4())
    users[username]['sessions'].append(session_id)
    session['username'] = username
    session['session_id'] = session_id
    save_users(users)

    return jsonify({"message": f"User {username} logged in successfully", "session_id": session_id}), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    username = session.get('username')
    session_id = session.get('session_id')

    users[username]['sessions'].remove(session_id)
    session.pop('username', None)
    session.pop('session_id', None)
    save_users(users)

    return jsonify({"message": "Logged out successfully"}), 200

@app.route('/ask', methods=['POST'])
def ask_question():
    global chat_histories

    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Missing 'question' in request body"}), 400

    question = data['question']
    session_id = data.get('session_id', 'default_session')

    if session_id not in chat_histories:
        chat_histories[session_id] = []

    session_history = chat_histories[session_id]
    context = ""
    if session_history:
        context = "Previous conversation:\n"
        for entry in session_history:
            context += f"Human: {entry['question']}\nAI: {entry['answer']}\n"

    contextualized_question = f"{context}\nHuman: {question}" if context else question

    # Get response from the chain
    response = chain.invoke({"input": question})
    ai_response = response["response"]

    chat_histories[session_id].append({
        "question": question,
        "answer": ai_response,
        "timestamp": str(datetime.now())
    })

    if len(chat_histories[session_id]) > MAX_HISTORY_LENGTH:
        chat_histories[session_id] = chat_histories[session_id][-MAX_HISTORY_LENGTH:]

    return jsonify({
        "answer": ai_response,
        "status": "success",
        "session_id": session_id,
        "history": chat_histories[session_id]
    }), 200

@app.route('/history', methods=['GET'])
def get_history():
    session_id = request.args.get('session_id', 'default_session')
    return jsonify({
        "history": chat_histories.get(session_id, []),
        "count": len(chat_histories.get(session_id, [])),
        "session_id": session_id
    }), 200

@app.route('/clear-history', methods=['POST'])
def clear_history():
    data = request.get_json() or {}
    session_id = data.get('session_id', 'default_session')
    chat_histories[session_id] = []
    return jsonify({"message": f"Chat history for session {session_id} cleared successfully", "status": "success"}), 200

@app.route('/clear-all-history', methods=['POST'])
def clear_all_history():
    global chat_histories
    session_count = len(chat_histories)
    chat_histories = {}
    return jsonify({"message": f"Chat history cleared for all {session_count} sessions", "status": "success"}), 200

@app.route('/generate-session', methods=['GET'])
def generate_session():
    session_id = str(uuid.uuid4())
    # Initialize an empty history for the new session
    chat_histories[session_id] = []
    save_chat_histories()
    return jsonify({"session_id": session_id}), 200


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=3000)
