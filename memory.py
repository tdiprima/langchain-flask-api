import os
import uuid
import logging
from flask import Flask, request, jsonify
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Configure and Validate Azure OpenAI Environment Variables
required_vars = {
    "AZURE_OPENAI_API_KEY": os.getenv("AZURE_OPENAI_API_KEY"),
    "AZURE_OPENAI_ENDPOINT": os.getenv("AZURE_OPENAI_ENDPOINT"),
    "AZURE_OPENAI_API_VERSION": os.getenv("AZURE_OPENAI_API_VERSION"),
    "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
}

# Ensure all required environment variables are set
for var, value in required_vars.items():
    if not value:
        raise ValueError(f"Missing required environment variable: {var}. Check your .env file.")

# Initialize Flask application
app = Flask(__name__)

# Initialize the Azure OpenAI Model with LangChain
try:
    llm = AzureChatOpenAI(
        api_version=required_vars["AZURE_OPENAI_API_VERSION"],
        azure_deployment=required_vars["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"],
        temperature=0.7,
        max_tokens=500
    )
    logging.info("AzureChatOpenAI successfully initialized.")
except Exception as e:
    logging.error(f"Failed to initialize AzureChatOpenAI: {e}")
    raise RuntimeError(f"Failed to initialize AzureChatOpenAI: {e}")

# Set Up a Dictionary to Store Session Memories
session_memories = {}  # Key: session_id, Value: ConversationBufferWindowMemory

# Define a Prompt Template with Chat History
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant providing concise and accurate answers."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}")
])

# Create a Chain
chain = prompt_template | llm


def get_session_memory(session_id: str) -> ConversationBufferWindowMemory:
    """
    Retrieve or create a conversation memory instance for a given session.
    """
    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferWindowMemory(
            k=10, return_messages=True
        )
    return session_memories[session_id]


# Define the REST API Endpoint
@app.route('/ask', methods=['POST'])
def ask_question():
    """
    REST API endpoint to ask a question to GPT-4o with chat history.
    Expects a JSON payload with 'question' and optional 'session_id' and 'new_conversation' fields.
    Returns the model's response, updated chat history, and session_id as JSON.
    """
    try:
        # Get JSON data from the request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        # Extract fields from the request
        question = data.get("question", "").strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400

        session_id = data.get("session_id", str(uuid.uuid4()))  # Generate new session_id if not provided
        new_conversation = data.get("new_conversation", False)  # Default to False

        # Get or create memory for this session
        memory = get_session_memory(session_id)

        # Clear chat history if new conversation is requested
        if new_conversation:
            memory.clear()
            logging.info(f"Cleared history for session_id: {session_id}")

        # Load current chat history from memory
        chat_history = memory.load_memory_variables({}).get("history", [])

        logging.info(f"Chat History before invoke (session {session_id}): {chat_history}")

        # Ensure chat_history is a list
        if not isinstance(chat_history, list):
            chat_history = []

        # Invoke the chain with the user's question and chat history
        response = chain.invoke({
            "question": question,
            "history": chat_history
        })

        logging.info(f"Response (session {session_id}): {response.content}")

        # Save the question and answer to memory
        memory.save_context(
            {"input": question},
            {"output": response.content}
        )

        # Fetch the updated chat history
        updated_history = memory.load_memory_variables({}).get("history", [])

        logging.info(f"Updated Chat History (session {session_id}): {updated_history}")

        # Return the response, updated chat history, and session_id
        return jsonify({
            "answer": response.content,
            "chat_history": [
                {"role": msg.type, "content": msg.content}
                for msg in updated_history
            ],
            "session_id": session_id,  # Return session_id for client to reuse
            "status": "success"
        }), 200

    except KeyError as e:
        logging.error(f"KeyError: {e}")
        return jsonify({"error": f"KeyError: {str(e)}"}), 500
    except Exception as e:
        logging.error(f"Unexpected error: {type(e).__name__}: {e}")
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500


# Run the Flask Application
if __name__ == '__main__':
    # Start the Flask server on port 3000
    logging.info("Starting Flask server on port 3000...")
    app.run(host='0.0.0.0', port=3000, debug=True)
