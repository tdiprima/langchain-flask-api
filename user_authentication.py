# Adds user login/logout magic
from flask import Flask, jsonify, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)

HISTORY_DIR = "chat_histories"
USERS_FILE = os.path.join(HISTORY_DIR, "users.json")
os.makedirs(HISTORY_DIR, exist_ok=True)

users = {}


def save_users():
    try:
        with open(USERS_FILE, 'w') as f:
            serializable_users = {}
            for username, user_data in users.items():
                serializable_users[username] = {
                    'password_hash': user_data['password_hash'],
                    'sessions': user_data['sessions']
                }
            json.dump(serializable_users, f, indent=2)
        print(f"Users saved to {USERS_FILE}")
        return True
    except Exception as e:
        print(f"Error saving users: {str(e)}")
        return False


def load_users():
    global users
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r') as f:
                users = json.load(f)
            print(f"Users loaded from {USERS_FILE}")
            return users
        else:
            print(f"No users file found at {USERS_FILE}, creating default users")
            default_users = {
                'admin': {
                    'password_hash': generate_password_hash('admin'),
                    'sessions': []
                }
            }
            save_users()
            return default_users
    except Exception as e:
        print(f"Error loading users: {str(e)}")
        return {'admin': {'password_hash': generate_password_hash('admin'), 'sessions': []}}


users = load_users()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return f(*args, **kwargs)
    return decorated_function


@app.route('/register', methods=['POST'])
def register():
    global users
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Missing username or password"}), 400
        username, password = data['username'], data['password']
        if username in users:
            return jsonify({"error": "Username already exists"}), 400
        users[username] = {'password_hash': generate_password_hash(password), 'sessions': []}
        save_users()
        return jsonify({"message": f"User {username} registered successfully", "status": "success"}), 201
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500


@app.route('/login', methods=['POST'])
def login():
    global users
    try:
        data = request.get_json()
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({"error": "Missing username or password"}), 400
        username, password = data['username'], data['password']
        if username not in users or not check_password_hash(users[username]['password_hash'], password):
            return jsonify({"error": "Invalid username or password"}), 401
        new_session_id = str(os.urandom(16).hex())
        users[username]['sessions'].append(new_session_id)
        session['username'] = username
        session['session_id'] = new_session_id
        save_users()
        return jsonify({"message": f"User {username} logged in", "status": "success", "session_id": new_session_id}), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500


@app.route('/logout', methods=['POST'])
@login_required
def logout():
    global users
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id', session.get('session_id'))
        username = session.get('username')
        if username in users and session_id in users[username]['sessions']:
            users[username]['sessions'].remove(session_id)
            save_users()
        session.pop('username', None)
        session.pop('session_id', None)
        return jsonify({"message": "Logged out successfully", "status": "success"}), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)
