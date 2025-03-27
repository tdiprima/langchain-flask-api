# Our Flask API now remembers the last 10 chats per session—like a goldfish with a notepad 🐠📝
from flask import Flask, request, jsonify
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Add this: Initialize chat history storage
chat_history = []
MAX_HISTORY_LENGTH = 10

llm = AzureChatOpenAI(
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
        temperature=0.7,
        max_tokens=500
    )

# Prompt template with context awareness
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant providing concise and accurate answers. Maintain context from the conversation history."),
    ("human", "{question}")
])


chain = prompt_template | llm


@app.route('/ask', methods=['POST'])
def ask_question():
    """
    REST API endpoint to ask a question to GPT-4o.
    Expects a JSON payload with 'question' field.
    Returns the model's response as JSON along with the chat history.
    """
    global chat_history

    try:
        # Get JSON data from the request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        # Extract question from the request
        question = data['question']
        print(f"Question received: {question}")

        # Create context from chat history
        context = ""
        if chat_history:
            context = "Previous conversation:\n"
            for entry in chat_history:
                context += f"Human: {entry['question']}\nAI: {entry['answer']}\n"

        # Prepare the question with context if there's history
        contextualized_question = question
        if context:
            contextualized_question = f"{context}\nHuman: {question}"

        # Invoke the chain with the user's question
        response = chain.invoke({
            "question": contextualized_question
        })
        print(f"Response: {response.content}")

        # Update chat history
        chat_history.append({
            "question": question,
            "answer": response.content
        })

        # Limit chat history to MAX_HISTORY_LENGTH entries
        if len(chat_history) > MAX_HISTORY_LENGTH:
            chat_history = chat_history[-MAX_HISTORY_LENGTH:]

        # Return the response with chat history
        return jsonify({
            "answer": response.content,
            "status": "success",
            "history": chat_history
        }), 200

    except KeyError as e:
        return jsonify({"error": f"KeyError: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500


@app.route('/history', methods=['GET'])
def get_history():
    """
    REST API endpoint to retrieve the current chat history.
    Returns the current chat history as JSON.
    """
    return jsonify({
        "history": chat_history,
        "count": len(chat_history)
    }), 200


@app.route('/clear-history', methods=['POST'])
def clear_history():
    """
    REST API endpoint to clear the chat history.
    Returns a confirmation message.
    """
    global chat_history
    chat_history = []
    return jsonify({
        "message": "Chat history cleared successfully",
        "status": "success"
    }), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=3000, debug=True)  # localhost by IP
