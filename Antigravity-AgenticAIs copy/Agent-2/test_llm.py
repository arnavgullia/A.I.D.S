"""Test LLM with Gemini 2.5 Flash Lite"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

api_key = os.getenv("AGENT2_GOOGLE_API_KEY")
print(f"API Key loaded: {api_key[:20]}...")

# Use Gemini 2.5 Flash Lite
MODEL = "gemini-2.5-flash-lite-preview-06-17"

print(f"Initializing LLM with model: {MODEL}")
llm = ChatGoogleGenerativeAI(
    model=MODEL,
    google_api_key=api_key,
    temperature=0.1
)

print("Sending test message...")
response = llm.invoke([HumanMessage(content="Say 'Hello' in one word")])
print(f"Response: {response.content}")
print("LLM test successful!")
