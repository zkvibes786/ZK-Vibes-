import os
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# Environment Variables Load کریں
load_dotenv()

# API Keys Setup
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
GROQ_KEY = os.getenv("GROQ_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

def run_gemini(prompt):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

def run_groq(prompt):
    try:
        client = Groq(api_key=GROQ_KEY)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Groq Error: {e}"

if __name__ == "__main__":
    print("ZK-AI Agent is running successfully on Cloud!")
    test_prompt = "Hello, respond with 'ZK-Tech AI Agent Online!'"
    
    if GEMINI_KEY:
        print("\n--- Gemini Response ---")
        print(run_gemini(test_prompt))
        
    if GROQ_KEY:
        print("\n--- Groq Response ---")
        print(run_groq(test_prompt))
  
