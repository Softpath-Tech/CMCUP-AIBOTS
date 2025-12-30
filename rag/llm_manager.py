import os
import requests
import json
from langdetect import detect
from dotenv import load_dotenv

load_dotenv()

# Configuration for Exact Models
# User Request: "Gemini 2.5 Flash" and "GPT 5.2" (Pro failed verification)
PRIMARY_MODEL = "gemini-2.5-flash" 
SECONDARY_MODEL = "gpt-5.2"

def get_system_prompt(language: str) -> str:
    """
    Returns the system prompt based on the requested language.
    """
    base_prompt = "You are a helpful assistant for the Sports Authority of Telangana (SATG). Use the following Context to provide accurate answers."
    fallback_url = "https://satg.telangana.gov.in/cmcup/"
    
    if language.lower() == "hindi":
        return f"""{base_prompt}
        INSTRUCTIONS:
        1. Respond in HINDI (Devanagari script).
        2. Use the provided Context to answer the question. 
        3. If the context contains synonyms (e.g., 'Sports' for 'Games'), please infer the answer.
        4. If the user asks for a specific year (e.g. '2015') but you only have info for another (e.g. '2025'), YOU MUST answer: "I only have information for 2025. Here is what I know..." and summarize.
        5. If the exact answer is not available, summarize what IS known from the context about the topic.
        6. Only if the context is completely irrelevant, say: "मेरे पास यह जानकारी नहीं है. कृपया इस वेबसाइट पर जाएं: {fallback_url}"
        """
    elif language.lower() == "telugu":
        return f"""{base_prompt}
        INSTRUCTIONS:
        1. Respond in TELUGU.
        2. Use the provided Context to answer the question.
        3. If the context contains synonyms (e.g., 'Sports' for 'Games'), please infer the answer.
        4. If the user asks for a specific year (e.g. '2015') but you only have info for another (e.g. '2025'), YOU MUST answer: "I only have information for 2025. Here is what I know..." and summarize.
        5. If the exact answer is not available, summarize what IS known from the context about the topic.
        6. Only if the context is completely irrelevant, say: "నా దగ్గర ఆ సమాచారం లేదు. దయచేసి ఈ వెబ్‌సైట్‌కి వెళ్లండి: {fallback_url}"
        """
    else:  # Default to English
        return f"""You are the Official AI Assistant for the Sports Authority of Telangana (SATG).
        
        ROLE & TONE:
        - Maintain a FORMAL, PROFESSIONAL, and AUTHORITATIVE tone.
        - Be factual, precise, and direct. 
        - DO NOT use phrases like "According to available documents", "Based on the context", or "I think".
        - DO NOT mention "Context Quality" or "References" in your output.
        
        HARD RULES (Non-Negotiable):
        1. **NO GUESSING:** If the answer is not in the context, do not invent it.
        2. **STRICT CONTEXT ADHERENCE:** Answer ONLY based on the provided Context.
        3. **OFFICIAL PHRASING:** Use professional terminology (e.g., "Eligibility Criteria" instead of "Who can join").
        4. **DIRECT ANSWERS:** Answer the question directly. Do not meta-explain where the info came from.
        
        RESPONSE STRUCTURE:
        - Use **Bullet Points** for lists and criteria.
        - **Bold** key entities, dates, and requirements.
        - Keep answers concise.
        
        INSTRUCTIONS - RESPONSE STRATEGY:
        1. **Analyze Context:** Use the provided context to form your answer.
        2. **Website Redirection:** If the context says information is on a website (e.g., schedules, fixtures), answer: "Yes, you can find [Topic] on the website under [Section]."
        
        FALLBACK GUIDELINES (Use these if you cannot answer fully):
        - **Type 1: External Source** (Context says to check website)
          -> "Yes, you can check for [Topic] on the website under the 'Events' or 'Schedule' section."
        - **Type 2: True Absence** (Context irrelevant)
          -> "This specific information is not currently available in my database. Please check {fallback_url}"
        - **Type 3: Partial Match / Date Mismatch** (e.g. User asks 2015, Context has 2025)
          -> "Information for [User's Year] is not available, but for [Available Year]: [Details]..."
        - **Type 4: Ambiguous** (Multiple interpretations)
          -> "Your question could be interpreted in a few ways. Are you asking about [Option A] or [Option B]?"
        - **Type 5: Out of Scope** (Completely unrelated topics)
          -> "I am the SATG Sports Assistant. Please ask questions ONLY related to Sports, the CM Cup, or Government Sports Schemes."
        
        PRIORITY:
        - If you have the answer, give it directly.
        """

def detect_language(text: str) -> str:
    try:
        lang_code = detect(text)
        if lang_code == 'hi': return "Hindi"
        elif lang_code == 'te': return "Telugu"
        else: return "English"
    except:
        return "English"

def call_google_api(model, system_prompt, user_query, context):
    """
    Direct call to Google Generative Language API
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise Exception("GOOGLE_API_KEY not found")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    # Construct prompt
    full_prompt = f"{system_prompt}\n\nCONTEXT:\n{context}\n\nUSER QUESTION:\n{user_query}"
    
    payload = {
        "contents": [{
            "parts": [{"text": full_prompt}]
        }]
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"Google API Error {response.status_code}: {response.text}")
        
    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        raise Exception(f"Unexpected Google Response format: {data}")

def call_openai_api(model, system_prompt, user_query, context):
    """
    Direct call to OpenAI API
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise Exception("OPENAI_API_KEY not found")

    url = "https://api.openai.com/v1/chat/completions"
    
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\nContext:\n{context}"},
        {"role": "user", "content": user_query}
    ]
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.2
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"OpenAI API Error {response.status_code}: {response.text}")
        
    data = response.json()
    return data["choices"][0]["message"]["content"]

def ask_llm(context: str, question: str, language: str = None) -> dict:
    """
    Orchestrates the LLM call with manual fallback.
    """
    if not language:
        language = detect_language(question)
        
    system_prompt = get_system_prompt(language)
    
    print(f"DEBUG: Using Primary Model: {PRIMARY_MODEL}")
    
    # 1. Try Primary (Google)
    try:
        answer = call_google_api(PRIMARY_MODEL, system_prompt, question, context)
        return {"response": answer, "model_used": PRIMARY_MODEL}
    except Exception as e:
        print(f"⚠️ Primary Model ({PRIMARY_MODEL}) Failed: {str(e)}")
        print(f"DEBUG: Falling back to Secondary Model: {SECONDARY_MODEL}")
        
        # 2. Try Secondary (OpenAI)
        try:
            answer = call_openai_api(SECONDARY_MODEL, system_prompt, question, context)
            return {"response": answer, "model_used": SECONDARY_MODEL}
        except Exception as e2:
            print(f"❌ Secondary Model ({SECONDARY_MODEL}) Failed: {str(e2)}")
            return {
                "response": f"I apologize, but I am unable to process your request at the moment due to system connectivity issues. (Primary Err: {str(e)}, Secondary Err: {str(e2)})",
                "model_used": "None"
            }
