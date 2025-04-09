![OpenAI](https://img.shields.io/badge/OpenAI-API--Powered-blueviolet?logo=openai&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-API-green?logo=flask)
![LangChain](https://img.shields.io/badge/LangChain-Integrated-orange?logo=brain)

# 🧠 LangChain Chatbot API – Multi-User Edition

A modular, Flask-based chatbot API powered by LangChain and OpenAI. Now with multi-user support, persistent chat history, persona control, and built-in authentication. Lightweight, flexible, and ready to roll for experimentation or production.

---

## 🚀 Features

- 🧍‍♂️ **Multi-user support** – Users can authenticate and maintain their own chat sessions
- 💬 **Persistent conversation memory** – Chats survive app restarts via JSON/db-backed persistence
- 🧠 **LangChain integration** – For advanced prompting and context-aware conversations
- 🎭 **Personas** – Modify chatbot tone/behavior using preset styles
- 🔐 **Authentication** – Token-based auth via `/login` and `/register` endpoints
- 🔄 **Modular structure** – Each component is standalone/testable
- 🧪 **Shell test scripts** – Each major function has a matching `.sh` tester

---

## 📁 Project Structure

| File                        | Description                                     |
|-----------------------------|-------------------------------------------------|
| `app.py` / `app_multiuser.py` | Flask app entry points                        |
| `chatbot_api.py`            | Main API logic and routing                     |
| `authentication.py`         | Handles login, registration, and auth checks   |
| `user_authentication.py`    | User credential storage + token management     |
| `chat_history.py`           | In-memory and persistent chat history manager  |
| `persistence.py`            | Low-level storage logic (files/db/etc)         |
| `conversation_persistence.py` | Combines memory + file-backed storage        |
| `prompt_engineering.py`     | Prompt construction + persona injection        |
| `prompt_engineering1.py`    | (Optional) Extended prompt engineering module  |

> ⚙️ Each file likely has a companion shell script for curl-based testing.

---

## 🔐 Authentication Flow

```bash
# Register a new user
curl -X POST http://localhost:3000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice", "password":"secret"}'

# Login and receive auth token
curl -X POST http://localhost:3000/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice", "password":"secret"}'
```

Use the returned token in all future requests via `Authorization: Bearer <token>`.

---

## 🧠 Example Chat Flow

```bash
# Ask a question
curl -X POST http://localhost:3000/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of Switzerland?"}'

# Continue with a persona
curl -X POST http://localhost:3000/ask \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"question": "Tell me something cool about it.", "persona": "friendly"}'
```

---

## ⚙️ Setup

```bash
# Install dependencies
pip install flask langchain openai

# Set environment variables
export OPENAI_API_KEY="your-key"
export OPENAI_API_VERSION="2023-05-15"

# Start the app
python app_multiuser.py  # or app.py for basic version
```

---

## ✅ Shell Test Scripts

Each major module has a matching shell script (not shown here) that includes cURL-based API tests. Great for verifying:
- Authentication
- Chat memory
- Persona behavior
- Conversation persistence

Run them from your terminal to simulate real-world usage.

---

## 🎯 Use Cases

- 🧪 Prototype chatbot UIs or assistant backends
- 🧰 Develop and test LangChain memory chains
- 🧑‍💻 Practice secure API design with authentication
- 🤹 Experiment with persona-aware LLM behaviors

---

## 📣 Contributions & Feedback

PRs welcome. If it breaks, log it. If it's awesome, share it. Let’s build cool stuff. 🚀
