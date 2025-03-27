# Spices up responses with personas and examples
from flask import Flask, jsonify, request
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

# Initialize Azure OpenAI Model
llm = AzureChatOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    temperature=0.7,
    max_tokens=500
)

# Persona constants
PERSONAS = {
    "default": "You are a helpful assistant providing concise and accurate answers.",
    "expert": "You are an expert AI assistant with deep knowledge. Provide detailed, technical info.",
    "friendly": "You are a friendly assistant. Use casual language and humor.",
    "concise": "You are a concise assistant. Provide short, direct answers."
}

# Few-shot examples
FEW_SHOT_EXAMPLES = {
    "factual": [
        {"question": "What is the capital of France?", "answer": "The capital of France is Paris."},
        {"question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare wrote 'Romeo and Juliet'."}
    ],
    "opinion": [
        {"question": "What's the best programming language?", "answer": "Python’s great for beginners—readable and easy!"},
        {"question": "Is AI dangerous?", "answer": "AI’s a mixed bag—cool benefits, but privacy’s a worry."}
    ],
    "instruction": [
        {"question": "How do I make pancakes?", "answer": "Mix flour, sugar, baking powder, milk, butter, egg. Cook on a hot pan."},
        {"question": "How can I improve public speaking?", "answer": "Practice, record yourself, join Toastmasters."}
    ]
}


def classify_question_type(question):
    question = question.lower()
    if any(q in question for q in ["what is", "who is", "when did", "where is", "how many"]):
        return "factual"
    if any(q in question for q in ["what do you think", "opinion", "best", "worst", "should i"]):
        return "opinion"
    if any(q in question for q in ["how do i", "how to", "steps", "guide", "instructions"]):
        return "instruction"
    return None


def create_prompt_template(persona="default", question_type=None):
    system_message = PERSONAS.get(persona, PERSONAS["default"])
    messages = [("system", system_message)]
    if question_type and question_type in FEW_SHOT_EXAMPLES:
        examples = FEW_SHOT_EXAMPLES[question_type]
        examples_text = "\n\nExamples:\n"
        for example in examples:
            examples_text += f"\nQ: {example['question']}\nA: {example['answer']}\n"
        messages = [("system", system_message + examples_text)]
    messages.append(("human", "{question}"))
    return ChatPromptTemplate.from_messages(messages)


@app.route('/personas', methods=['GET'])
def get_personas():
    return jsonify({"personas": list(PERSONAS.keys()), "descriptions": PERSONAS}), 200


@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "Missing 'question'"}), 400
        question = data['question']
        persona = data.get('persona', 'default')
        question_type = classify_question_type(question)
        prompt_template = create_prompt_template(persona, question_type)
        dynamic_chain = prompt_template | llm
        response = dynamic_chain.invoke({"question": question})
        return jsonify({"answer": response.content, "status": "success", "persona": persona, "question_type": question_type}), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {type(e).__name__}: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=True, port=3000)
