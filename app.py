import os
import json
import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse

load_dotenv()

# System Prompts
SYSTEM_PROMPT = """
You are an expert English Language Curriculum Designer and Tutor.
Your task is to generate a natural, realistic English conversation between two speakers for a given scenario.
The conversation should highlight practical, everyday English or Corporate English vocabulary, phrases, and idioms.

You MUST return the output as a valid JSON object matching the following structure (do NOT add any extra markdown format or text, return only the raw JSON):
{
  "scenario": "Clean name of the scenario",
  "dialogue": [
    {
      "speaker": "Name/Role of the speaker (e.g. interviewer, cashier, boss)",
      "text": "The English sentence spoken.",
      "translation": "Hindi/Hinglish translation of the sentence in natural, conversational Roman script (Hinglish) so it is easy to understand.",
      "tip": "A practical tip or alternative/advanced phrasing (e.g., 'Instead of \"I want a salary hike\", say \"I would like to discuss a compensation review.\"'). Keep it short and useful. Leave empty string if no specific tip applies.",
      "vocabulary": [
        {
          "word": "A highlighted word/phrase from the text",
          "meaning": "Its meaning in simple English"
        }
      ]
    }
  ]
}

Generate exactly 8 to 12 conversation turns. Make the dialogue flow naturally, like a real-world interaction.
"""

EXAMPLE_SYSTEM_PROMPT = """
You are an expert English Language Tutor.
Your task is to generate a realistic English example sentence that showcases the usage of a specific vocabulary word, along with a natural Hinglish/Hindi translation.

You MUST return the output as a valid JSON object matching the following structure (do NOT add any extra markdown format or text, return only the raw JSON):
{
  "sentence": "The generated English example sentence using the word naturally.",
  "translation": "Hindi/Hinglish translation of the sentence in natural, conversational Roman script (Hinglish) so it is easy to understand."
}
"""

def get_mistral_api_key():
    for name in ["MISTRAL_API_KEY", "mistral_api_key", "MISTRAL_KEY", "API_KEY"]:
        val = os.getenv(name, "").strip()
        if val:
            return val
    return ""

def run_model_inference(system_content, user_content):
    api_key = get_mistral_api_key()
    if not api_key:
        raise ValueError("MISTRAL_API_KEY Secret is missing! Please set MISTRAL_API_KEY in environment variables.")

    base_url = os.getenv("MISTRAL_API_URL", "https://api.mistral.ai/v1").strip().rstrip("/")
    endpoint = f"{base_url}/chat/completions"
    model_name = os.getenv("MISTRAL_MODEL", "mistral-small-latest").strip()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }

    response = requests.post(endpoint, headers=headers, json=payload, timeout=60)
    
    # Fallback if model doesn't support response_format param
    if response.status_code != 200 and "response_format" in response.text:
        payload.pop("response_format", None)
        response = requests.post(endpoint, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        raise RuntimeError(f"Mistral API returned HTTP {response.status_code}: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]

def parse_llm_json(raw_text):
    raw_text = raw_text.strip()
    if raw_text.startswith("```"):
        first_newline = raw_text.find('\n')
        if first_newline != -1:
            raw_text = raw_text[first_newline:].strip()
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3].strip()
            
    start = raw_text.find('{')
    end = raw_text.rfind('}')
    if start != -1 and end != -1:
        json_str = raw_text[start:end+1]
        return json.loads(json_str)
    return json.loads(raw_text)

# Create FastAPI application
app = FastAPI(title="Master English - AI Tutor")

# Serve index.html directly on root '/' and '/static/index.html'
@app.get("/", response_class=HTMLResponse)
@app.get("/index.html", response_class=HTMLResponse)
@app.get("/static/index.html", response_class=HTMLResponse)
async def serve_index():
    possible_paths = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "index.html"),
        os.path.join(os.getcwd(), "templates", "index.html"),
        "templates/index.html",
        "index.html"
    ]
    for p in possible_paths:
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return HTMLResponse(content=f.read(), status_code=200)
    
    return HTMLResponse(content="<h1>Error: templates/index.html file not found!</h1>", status_code=500)

@app.post("/generate_scenario")
async def generate_scenario(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    scenario = data.get("scenario", "").strip()
    if not scenario:
        return JSONResponse(content={"error": "Please provide a scenario description."}, status_code=400)

    user_prompt = f"Generate a conversation scenario for: '{scenario}'"
    
    try:
        raw_output = run_model_inference(SYSTEM_PROMPT, user_prompt)
        parsed_json = parse_llm_json(raw_output)
        return JSONResponse(content=parsed_json, status_code=200)
    except Exception as e:
        print(f"Mistral Scenario Generation Error: {e}")
        return JSONResponse(content={
            "error": f"Failed to generate conversation: {str(e)}"
        }, status_code=500)

@app.post("/generate_example")
async def generate_example(request: Request):
    try:
        data = await request.json()
    except Exception:
        data = {}

    word = data.get("word", "").strip()
    meaning = data.get("meaning", "").strip()

    if not word:
        return JSONResponse(content={"error": "Please provide a word."}, status_code=400)

    user_prompt = f"Generate an example sentence and Hinglish translation for the word: '{word}' (meaning: '{meaning}')"

    try:
        raw_output = run_model_inference(EXAMPLE_SYSTEM_PROMPT, user_prompt)
        parsed_json = parse_llm_json(raw_output)
        return JSONResponse(content=parsed_json, status_code=200)
    except Exception as e:
        print(f"Mistral Example Generation Error: {e}")
        return JSONResponse(content={
            "error": f"Failed to generate example sentence: {str(e)}"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
