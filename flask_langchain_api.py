import os
import logging
from flask import Flask, request, jsonify
from langchain_openai import AzureChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)


def get_env_var(var_name: str) -> str:
    """Retrieve an environment variable, raising an error if missing."""
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}. Check your .env file.")
    return value


# Validate and Retrieve Environment Variables
try:
    AZURE_OPENAI_API_KEY = get_env_var("AZURE_OPENAI_API_KEY")
    AZURE_OPENAI_ENDPOINT = get_env_var("AZURE_OPENAI_ENDPOINT")
    AZURE_OPENAI_API_VERSION = get_env_var("AZURE_OPENAI_API_VERSION")
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = get_env_var("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
except EnvironmentError as e:
    logging.error(e)
    raise

# Initialize Flask application
app = Flask(__name__)

# Initialize the Azure OpenAI Model with LangChain
try:
    llm = AzureChatOpenAI(
        api_version=AZURE_OPENAI_API_VERSION,
        azure_deployment=AZURE_OPENAI_CHAT_DEPLOYMENT_NAME,
        temperature=0.7,
        max_tokens=500
    )
    logging.info("AzureChatOpenAI successfully initialized.")
except Exception as e:
    logging.error(f"Failed to initialize AzureChatOpenAI: {e}")
    raise RuntimeError(f"Failed to initialize AzureChatOpenAI: {e}")

# Define Chat Prompt Template
prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant providing concise and accurate answers."),
    ("human", "{question}")
])

# Create a Chain
chain = prompt_template | llm


# Define the REST API Endpoint
@app.route('/ask', methods=['POST'])
def ask_question():
    """
    REST API endpoint to ask a question to GPT-4o.
    Expects a JSON payload with 'question' field.
    Returns the model's response as JSON.
    """
    try:
        # Get JSON data from the request
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400

        # Extract question from the request
        question = data.get('question', '').strip()
        if not question:
            return jsonify({"error": "Question cannot be empty"}), 400

        logging.info(f"Received question: {question}")

        # Invoke the chain with the user's question
        response = chain.invoke({"question": question})

        logging.info(f"Response generated: {response.content}")

        # Return the response
        return jsonify({
            "answer": response.content,
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
