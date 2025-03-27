from flask import Flask, jsonify, request
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

app = Flask(__name__)

# Load environment variables
load_dotenv()

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

# Persona definitions
PERSONAS = {
    "default": "You are a helpful assistant providing concise and accurate answers.",
    "expert": "You are an expert AI with deep knowledge. Provide detailed, technical answers.",
    "friendly": "You are a friendly assistant. Use casual language and occasional humor.",
    "concise": "You are a concise assistant. Provide short, direct answers with bullet points."
}

# Few-shot examples
FEW_SHOT_EXAMPLES = {
    "factual": [
        {"question": "What is the capital of France?", "answer": "The capital of France is Paris."},
        {"question": "Who wrote 'Romeo and Juliet'?", "answer": "William Shakespeare wrote 'Romeo and Juliet'."}
    ],
    "opinion": [
        {"question": "What's the best programming language for beginners?", "answer": "Python’s often recommended for its readable syntax."},
        {"question": "Is AI dangerous?", "answer": "AI has risks like job displacement but also huge potential—balance is key."}
    ],
    "instruction": [
        {"question": "How do I make pancakes?", "answer": "Mix flour, sugar, baking powder, milk, butter, egg. Cook on a hot pan."},
        {"question": "How can I improve public speaking?", "answer": "Practice, record yourself, join Toastmasters."}
    ]
}

# Question classification
def classify_question_type(question):
    question = question.lower()
    if any(q in question for q in ["what is", "who is", "when did", "where is"]):
        return "factual"
    if any(q in question for q in ["what do you think", "best", "should i"]):
        return "opinion"
    if any(q in question for q in ["how do i", "how to", "steps"]):
        return "instruction"
    return None

# Dynamic prompt creation
def create_prompt_template(persona="default", question_type=None):
    system_message = PERSONAS.get(persona, PERSONAS["default"])
    messages = [("system", system_message)]
    if question_type and question_type in FEW_SHOT_EXAMPLES:
        examples_text = "\n\nExamples:\n"
        for example in FEW_SHOT_EXAMPLES[question_type]:
            examples_text += f"\nQ: {example['question']}\nA: {example['answer']}\n"
        messages = [("system", system_message + examples_text)]
    messages.append(("human", "{question}"))
    return ChatPromptTemplate.from_messages(messages)

# Endpoints
@app.route('/ask', methods=['POST'])
def ask_question():
    data = request.get_json()
    if not data or 'question' not in data:
        return jsonify({"error": "Missing 'question'"}), 400
    question = data['question']
    persona = data.get('persona', 'default')
    question_type = classify_question_type(question)
    
    prompt_template = create_prompt_template(persona, question_type)
    dynamic_chain = prompt_template | llm
    response = dynamic_chain.invoke({"question": question})
    
    return jsonify({"answer": response.content, "persona": persona, "question_type": question_type}), 200

@app.route('/personas', methods=['GET'])
def get_personas():
    return jsonify({"personas": list(PERSONAS.keys()), "description": PERSONAS}), 200

if __name__ == '__main__':
    app.run(port=3000, debug=True)
