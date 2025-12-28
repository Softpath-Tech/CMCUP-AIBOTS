import os
from litellm import completion
from langdetect import detect
from dotenv import load_dotenv

load_dotenv()

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
        2. If the answer is not in the context, say "मेरे पास यह जानकारी नहीं है. कृपया इस वेबसाइट पर जाएं: {fallback_url}"
        """
    elif language.lower() == "telugu":
        return f"""{base_prompt}
        INSTRUCTIONS:
        1. Respond in TELUGU.
        2. If the answer is not in the context, say "నా దగ్గర ఆ సమాచారం లేదు. దయచేసి ఈ వెబ్‌సైట్‌కి వెళ్లండి: {fallback_url}"
        """
    else:  # Default to English
        return f"""{base_prompt}
        INSTRUCTIONS:
        1. Respond in ENGLISH.
        2. If the answer is not in the context, say "I don't have that information. Please go to this website {fallback_url}"
        """

def detect_language(text: str) -> str:
    """
    Detects language using langdetect. Returns 'Hindi', 'Telugu', or 'English'.
    """
    try:
        lang_code = detect(text)
        if lang_code == 'hi':
            return "Hindi"
        elif lang_code == 'te':
            return "Telugu"
        else:
            return "English"
    except:
        return "English"

def ask_llm(context: str, question: str, language: str = None) -> dict:
    """
    Orchestrates the LLM call using LiteLLM with fallbacks.
    """
    
    # 1. Detect Language if not provided
    if not language:
        language = detect_language(question)
        
    # 2. Get System Prompt
    system_prompt = get_system_prompt(language)
    
    print(f"DEBUG: Context Content (First 200 chars): {context[:200]}")
    
    messages = [
        {"role": "system", "content": f"{system_prompt}\n\nContext:\n{context}"},
        {"role": "user", "content": question}
    ]
    
    # 3. Define Models (Tier 1: OpenAI, Tier 2: Gemini)
    # Using 'gemini/...' prefix for Google AI Studio
    primary_model = "openai/gpt-4o-mini"
    secondary_model = "gemini/gemini-2.5-flash"
    
    try:
        # Attempt Primary Model
        response = completion(
            model=primary_model,
            messages=messages,
            fallbacks=[secondary_model], # Auto-fallback handled by LiteLLM if configured, 
                                         # but explicit try/except is often safer for custom logic.
                                         # LiteLLM's `fallbacks` param handles list of models to try on failure.
            temperature=0.2
        )
        
        # Extract content and model
        answer = response.choices[0].message.content
        model_used = response.model
        
        return {
            "response": answer,
            "model_used": model_used
        }
        
    except Exception as e:
        # Fallback manual logic if LiteLLM fallbacks param behavior is unexpected in specific version
        # But 'fallbacks' param in completion method should handle it.
        # If it fails entirely:
        return {
            "response": f"Error fulfilling request: {str(e)}",
            "model_used": "None"
        }
