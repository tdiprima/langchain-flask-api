# Import necessary libraries
from flask import Flask, request, jsonify
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import datetime
import uuid

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Initialize chat histories with session support
chat_histories = {}
MAX_HISTORY_LENGTH = 10

# Prompt template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a professional assistant focused on providing factual, business-appropriate information. Your responses should be clear, concise, and informative while maintaining professional standards. For any location or culture-related questions, focus on providing objective, factual information from reliable sources."),
    ("human", "{question}")
])

# Azure OpenAI setup
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    temperature=0.7,
    max_tokens=500
)

chain = prompt_template | llm

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

    response = chain.invoke({"question": contextualized_question})

    chat_histories[session_id].append({
        "question": question,
        "answer": response.content,
        "timestamp": str(datetime.datetime.now())
    })

    if len(chat_histories[session_id]) > MAX_HISTORY_LENGTH:
        chat_histories[session_id] = chat_histories[session_id][-MAX_HISTORY_LENGTH:]

    return jsonify({
        "answer": response.content,
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
    new_session_id = str(uuid.uuid4())
    return jsonify({"session_id": new_session_id, "status": "success"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)
