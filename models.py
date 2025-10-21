import anthropic
from groq import Groq
from openai import OpenAI
import requests


import os
from dotenv import load_dotenv

load_dotenv()


CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") 
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY") 
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") 
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

MODELS = {
    "Claude Sonnet": {"provider": "claude", "model": "claude-sonnet-4-6"},
    "Llama 70B (Meta)": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
    "Mistral Large": {"provider": "mistral", "model": "mistral-large-latest"},
    "Gemini Flash": {"provider": "gemini", "model":  "gemini-1.5-flash"},
    "ChatGPT": {"provider": "openai", "model": "gpt-4o"},
    "DeepSeek": {"provider": "deepseek", "model": "deepseek-chat"},
}
    

claude_clt = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
groq_clt = Groq(api_key=GROQ_API_KEY)

def call_model(prompt, model_name):
    config = MODELS[model_name]
    provider = config["provider"]
    model = config["model"]
    try:
        if provider == "claude":
            response = claude_clt.messages.create(
                model=model,
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        elif provider == "groq":
            response = groq_clt.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
    except Exception as e:
        return f"Erreur {model_name} : {str(e)}"
