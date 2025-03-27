from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

# Persona flavors
PERSONAS = {
    "default": "You're a helpful assistant—keep it concise and accurate.",
    "expert": "You're a brainy expert—go technical and detailed.",
    "friendly": "You're a chill buddy—casual, fun, and simple.",
    "concise": "You're short and sweet—bullet points, no fluff."
}

# Few-shot examples (tiny taste)
FEW_SHOT_EXAMPLES = {
    "factual": [{"q": "What's 2+2?", "a": "2+2 is 4."}],
    "opinion": [{"q": "Best snack?", "a": "Tough call, but cookies rock!"}],
    "instruction": [{"q": "How to nap?", "a": "Lie down, close eyes, snooze."}]
}

# Azure OpenAI setup (replace with your creds)
llm = AzureChatOpenAI(
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    temperature=0.7
)


# Guess the question type
def classify_question(question):
    q = question.lower()
    if "what is" in q or "who" in q: return "factual"
    if "think" in q or "best" in q: return "opinion"
    if "how" in q: return "instruction"
    return None


# Build a dynamic prompt
def make_prompt(question, persona="default"):
    system = PERSONAS.get(persona, PERSONAS["default"])
    q_type = classify_question(question)
    if q_type and q_type in FEW_SHOT_EXAMPLES:
        example = FEW_SHOT_EXAMPLES[q_type][0]
        system += f"\nExample: Q: {example['q']} A: {example['a']}"
    return ChatPromptTemplate.from_messages([("system", system), ("human", question)])


# Ask and answer
def chat(question, persona="default"):
    prompt = make_prompt(question, persona)
    response = (prompt | llm).invoke({"question": question})
    print(f"🤖 [{persona}]: {response.content}")


# Test it out
if __name__ == "__main__":
    chat("What is quantum computing?", "expert")
    chat("What do you think of AI?", "friendly")
    chat("How do I code?", "concise")
