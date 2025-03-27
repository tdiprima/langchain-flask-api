# export OPENAI_API_VERSION="2023-05-15" && python app.py
from flask import Flask, jsonify, request, session
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from datetime import datetime

app = Flask(__name__)

# Constants for personas
PERSONAS = {
    "default": "You are a helpful assistant providing concise and accurate answers. Maintain context from the conversation history.",
    "expert": "You are an expert AI assistant with deep knowledge across many fields. Provide detailed, technical, and accurate information. Use academic language and cite sources when possible.",
    "friendly": "You are a friendly and approachable assistant. Use casual language, be conversational, and add occasional humor. Keep explanations simple and relatable.",
    "concise": "You are a concise assistant that values brevity. Provide short, direct answers with minimal elaboration. Use bullet points when appropriate."
}

# Few-shot examples for question types
FEW_SHOT_EXAMPLES = {
    "factual": [
        {"question": "What is the capital of France?", "answer": "The capital of France is Paris."},
        {"question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare wrote 'Romeo and Juliet'."}
    ],
    "opinion": [
        {"question": "What's the best programming language for beginners?", "answer": "For beginners, Python is often recommended due to its readable syntax and gentle learning curve. However, the 'best' language depends on your goals. JavaScript is great for web development, Swift for iOS apps, etc."},
        {"question": "Is artificial intelligence dangerous?", "answer": "AI presents both opportunities and risks. While it can solve complex problems, concerns exist about job displacement, privacy, and autonomous weapons. Responsible development with ethical guidelines is important."}
    ],
    "instruction": [
        {"question": "How do I make pancakes?", "answer": "Basic pancake recipe: Mix 1 cup flour, 2 tbsp sugar, 2 tsp baking powder, and a pinch of salt. Add 1 cup milk, 2 tbsp melted butter, and 1 egg. Stir until just combined (lumps are okay). Cook on a hot greased pan until bubbles form, then flip and cook until golden."},
        {"question": "How can I improve my public speaking?", "answer": "To improve public speaking: 1) Practice regularly, 2) Record yourself and review, 3) Join a group like Toastmasters, 4) Know your material thoroughly, 5) Start with small audiences, and 6) Focus on breathing and posture."}
    ]
}

# Global chat histories (assuming from earlier sections)
chat_histories = {}
MAX_HISTORY_LENGTH = 10

# Azure OpenAI setup (assuming from earlier sections)
llm = AzureChatOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    temperature=0.7
)


# Classify question type
def classify_question_type(question):
    question = question.lower()
    if any(q in question for q in ["what is", "who is", "when did", "where is", "how many"]):
        return "factual"
    if any(q in question for q in ["what do you think", "opinion", "best", "worst", "should i", "better"]):
        return "opinion"
    if any(q in question for q in ["how do i", "how to", "steps", "guide", "tutorial", "instructions"]):
        return "instruction"
    return None


# Create dynamic prompt template
def create_prompt_template(persona="default", question_type=None):
    system_message = PERSONAS.get(persona, PERSONAS["default"])
    messages = [("system", system_message)]
    
    if question_type and question_type in FEW_SHOT_EXAMPLES:
        examples = FEW_SHOT_EXAMPLES[question_type]
        examples_text = "\n\nHere are some examples of how to answer this type of question: \n"
        for example in examples:
            examples_text += f"\nQuestion: {example['question']}\nAnswer: {example['answer']}\n"
        messages = [("system", system_message + examples_text)]
    
    messages.append(("human", "{question}"))
    return ChatPromptTemplate.from_messages(messages)


# Ask endpoint with dynamic prompts
@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question' in request body"}), 400
        
        question = data['question']
        session_id = data.get('session_id', session.get('session_id', 'default_session'))
        persona = data.get('persona', 'default')

        # Authentication check (simplified, assuming full logic from earlier)
        is_authenticated = 'username' in session and session.get('session_id') == session_id
        session_username = session.get('username') if is_authenticated else None

        # Initialize session history
        if session_id not in chat_histories:
            chat_histories[session_id] = []

        # Build context
        session_history = chat_histories[session_id]
        context = ""
        if session_history:
            context = "Previous conversation: \n"
            for entry in session_history:
                context += f"Human: {entry['question']}\nAI: {entry['answer']}\n"
        contextualized_question = f"{context}\nHuman: {question}" if context else question

        # Dynamic prompt and response
        question_type = classify_question_type(question)
        prompt_template = create_prompt_template(persona, question_type)
        dynamic_chain = prompt_template | llm
        response = dynamic_chain.invoke({"question": contextualized_question})

        # Update chat history
        chat_histories[session_id].append({
            "question": question,
            "answer": response.content,
            "timestamp": str(datetime.now()),
            "persona": persona
        })
        if len(chat_histories[session_id]) > MAX_HISTORY_LENGTH:
            chat_histories[session_id] = chat_histories[session_id][-MAX_HISTORY_LENGTH:]

        # Return response
        return jsonify({
            "answer": response.content,
            "status": "success",
            "session_id": session_id,
            "authenticated": is_authenticated,
            "username": session_username,
            "persona": persona,
            "question_type": question_type,
            "history": chat_histories[session_id]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500


# List personas endpoint
@app.route('/personas', methods=['GET'])
def get_personas():
    return jsonify({
        "personas": list(PERSONAS.keys()),
        "descriptions": PERSONAS
    }), 200


if __name__ == '__main__':
    app.run(port=3000, debug=True)
