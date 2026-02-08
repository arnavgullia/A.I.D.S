#!/usr/bin/env python3
"""Simple API test for Agent 1."""

import os
import time

# Set working directory
os.chdir('/home/pranjay/workspace/Antigravity-AgenticAIs/Agent-1')

from dotenv import load_dotenv
load_dotenv('.env')

print("=== Agent 1 API Test ===")
print(f"Time: {time.strftime('%H:%M:%S')}")

api_key = os.getenv('GOOGLE_API_KEY')
if not api_key:
    print("ERROR: No API key found!")
    exit(1)

print(f"API Key: {api_key[:12]}...")
print("Model: gemini-2.5-flash-lite")
print()
print("Initializing LLM...")

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

llm = ChatGoogleGenerativeAI(
    model='gemini-2.5-flash-lite',
    google_api_key=api_key,
    temperature=0.1
)

print("Making API call at:", time.strftime('%H:%M:%S'))
try:
    response = llm.invoke([HumanMessage(content='Say OK')])
    print(f"SUCCESS at {time.strftime('%H:%M:%S')}")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"ERROR: {e}")
