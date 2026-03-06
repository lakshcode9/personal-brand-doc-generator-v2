import os
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path)

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set in .env")
    return Groq(api_key=api_key)

def generate_completion(prompt, system_prompt="You are a personal brand strategist and expert copywriter.", model="llama-3.3-70b-versatile", temperature=0.7, json_mode=False):
    client = get_groq_client()
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]
    
    kwargs = {
        "messages": messages,
        "model": model,
        "temperature": temperature,
        "max_tokens": 4000
    }
    
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}
        
    response = client.chat.completions.create(**kwargs)
    return response.choices[0].message.content
