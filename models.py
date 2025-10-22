import anthropic
from groq import Groq
from openai import OpenAI
import requests
from openai import OpenAI
import os
from dotenv import load_dotenv
import google.generativeai as genai
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
client = genai.Client(api_key=GEMINI_API_KEY)
gpt_clt = OpenAI(api_key=OPENAI_API_KEY)
deepseek_clt = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
# Mistral HTTP configuration
MISTRAL_URL = "https://api.mistral.ai/v1/chat/completions"


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
        elif provider == "openai":
            response = gpt_clt.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        elif provider == "deepseek":
            response = deepseek_clt.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        elif provider == "gemini":
            response = client.models.generate_content(
                model=model,
                contents=prompt
            )
            return response.text
        elif provider == "mistral":
            response = requests.post(
                MISTRAL_URL,
                headers={
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )

            data = response.json()

            if "choices" not in data:
                return f"Erreur Mistral : {data}"

            return data["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Erreur {model_name} : {str(e)}"
def call_all_models(prompt):
    return {name: call_model(prompt, name) for name in MODELS}