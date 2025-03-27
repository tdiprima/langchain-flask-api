from flask import Flask, jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
import uuid

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Constants
HISTORY_DIR = "chat_history"
USERS_FILE = os.path.join(HISTORY_DIR, "users.json")
SECRET_KEY = os.urandom(24)
app.config['SECRET_KEY'] = SECRET_KEY
chat_histories = {}
users = {}

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

# User management functions
def save_users(users_dict):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users_dict, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving users: {e}")
        return False

def load_users():
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        else:
            default_users = {'admin': {'password_hash': generate_password_hash('admin'), 'sessions': []}}
            save_users(default_users)
            return default_users
    except Exception as e:
        print(f"Error loading users: {e}")
        return {'admin': {'password_hash': generate_password_hash('admin'), 'sessions': []}}

# Load users on startup
users = load_users()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function

# Authentication endpoints
@app.route('/register', methods=['POST'])
def register():
    global users
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    username, password = data['username'], data['password']
    if username in users:
        return jsonify({"error": "Username already exists"}), 400
    users[username] = {'password_hash': generate_password_hash(password), 'sessions': []}
    save_users(users)
    return jsonify({"message": f"User {username} registered", "status": "success"}), 201

@app.route('/login', methods=['POST'])
def login():
    global users
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({"error": "Missing username or password"}), 400
    username, password = data['username'], data['password']
    if username not in users or not check_password_hash(users[username]['password_hash'], password):
        return jsonify({"error": "Invalid credentials"}), 401
    session_id = str(uuid.uuid4())
    users[username]['sessions'].append(session_id)
    session['username'] = username
    session['session_id'] = session_id
    save_users(users)
    return jsonify({"message": f"User {username} logged in", "session_id": session_id}), 200

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    global users
    data = request.get_json() or {}
    session_id = data.get('session_id', session.get('session_id'))
    username = session.get('username')
    if username in users and session_id in users[username]['sessions']:
        users[username]['sessions'].remove(session_id)
        save_users(users)
    session.pop('username', None)
    session.pop('session_id', None)
    return jsonify({"message": "Logged out successfully"}), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)
