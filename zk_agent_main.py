import os
import json
import requests
import google.generativeai as genai
from groq import Groq
from dotenv import load_dotenv

# Environment Variables Load کریں
load_dotenv()

# API Keys Setup
GROQ_KEY = os.getenv("GROQ_API_KEY")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SERPER_KEY = os.getenv("SERPER_API_KEY")
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

MEMORY_FILE = "zk_memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {"user_name": "Zain", "history": []}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Persona setup
SYSTEM_PROMPT = """
You are Ayla (ZK AI Companion), a caring, intelligent, and highly capable female companion and professional assistant for Zain.
You speak in warm, natural Roman Urdu. 
You handle tech tasks, MT5 market analysis logic, local business client hunting via Google Maps APIs, and media generation prompts.
Always remain supportive, direct, and empathetic.
"""

def call_groq(prompt):
    if not GROQ_KEY:
        raise Exception("Groq key missing")
    client = Groq(api_key=GROQ_KEY)
    res = client.chat.completions.create(
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        model="llama3-8b-8192"
    )
    return res.choices[0].message.content

def call_gemini(prompt):
    if not GEMINI_KEY:
        raise Exception("Gemini key missing")
    genai.configure(api_key=GEMINI_KEY)
    model = genai.GenerativeModel('gemini-1.5-flash')
    res = model.generate_content(f"{SYSTEM_PROMPT}\n\nUser: {prompt}")
    return res.text

def call_openrouter(prompt):
    if not OPENROUTER_KEY:
        raise Exception("OpenRouter key missing")
    headers = {"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "json"}
    payload = {
        "model": "meta-llama/llama-3-8b-instruct:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    }
    res = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
    return res.json()['choices'][0]['message']['content']

def query_agent(prompt):
    # Auto-Fallback System
    for provider, func in [("Groq", call_groq), ("Gemini", call_gemini), ("OpenRouter", call_openrouter)]:
        try:
            return func(prompt)
        except Exception as e:
            print(f"[{provider} Error/Expired]: Shifting to backup provider... ({e})")
    return "Zain, aap ki tamam APIs mein issue aa raha hai. Baraye meharbani settings mein ja kar keys update karein."

def search_leads_serper(query):
    if not SERPER_KEY:
        return "Serper API key not configured."
    url = "https://google.serper.dev/places"
    headers = {'X-API-KEY': SERPER_KEY, 'Content-Type': 'application/json'}
    payload = json.dumps({"q": query})
    res = requests.post(url, headers=headers, data=payload)
    return res.json()

if __name__ == "__main__":
    print("=== ZK-AI Agent & Companion (Ayla) Active on Cloud ===")
    memory = load_memory()
    print(f"Welcome back, {memory.get('user_name', 'Zain')}!")
    
    while True:
        try:
            user_input = input("\nZain > ")
            if user_input.lower() in ['exit', 'quit']:
                break
            elif user_input.lower() == 'settings':
                print("Update your .env file with new API keys anytime.")
                continue
            elif user_input.startswith("find_clients:"):
                location_query = user_input.replace("find_clients:", "").strip()
                print(f"Hunting leads for: {location_query}...")
                leads = search_leads_serper(location_query)
                print("Leads Result:", json.dumps(leads, indent=2))
                continue
                
            response = query_agent(user_input)
            print(f"\nAyla > {response}")
            
        except KeyboardInterrupt:
            break
  
