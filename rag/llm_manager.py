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
        - Maintain a FORMAL, NEUTRAL, and ADMINISTRATIVE tone (like a government official).
        - Be factual and precise. Avoid casual language, opinions, or phrases like "I think".
        - Use "As per official guidelines..." or "According to available documents..." where appropriate.

        HARD RULES (Non-Negotiable):
        1. **NO GUESSING:** If the answer is not in the context, do not invent it.
        2. **STRICT CONTEXT ADHERENCE:** Answer ONLY based on the provided Context.
        3. **OFFICIAL PHRASING:** Use professional terminology (e.g., "Eligibility Criteria" instead of "Who can join").
        
        RESPONSE STRUCTURE:
        - Use **Bullet Points** for lists and criteria.
        - **Bold** key entities, dates, and requirements.
        - Keep answers concise and structured (Header -> Details -> References).
        
        INSTRUCTIONS - RESPONSE STRATEGY:
        1. **Analyze Context Quality:** Determine if the retrieved context is a perfect match, partial match, or irrelevant.
        2. **Infer from Synonyms:** If the context mentions 'Sports' but the user asked for 'Games', use the info.
        
        FALLBACK GUIDELINES (Use these if you cannot answer fully):
        - **Type 1: True Absence** (Context irrelevant)
          -> "Based on the official documents available, this specific information is not explicitly mentioned. Please check {fallback_url}"
        - **Type 2: Partial Match / Date Mismatch** (e.g. User asks 2015, Context has 2025)
          -> "I don't have information for [User's Year], but I can tell you about [Available Year]. Here is what I know..."
        - **Type 3: Ambiguous** (Multiple interpretations)
          -> "Your question could be interpreted in a few ways. Are you asking about [Option A] or [Option B]?"
        - **Type 4: Out of Scope** (Completely unrelated topics, e.g. cooking, coding, politics)
          -> "I am the SATG Sports Assistant. Please ask questions ONLY related to Sports, the CM Cup, or Government Sports Schemes."
        
        PRIORITY:
        - If you have the answer, give it directly in the required structure.
        - If you have helpful partial info, share it formally.
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
    
    # 3. Define Models (Tier 1: OpenAI GPT-4o-mini - Verified Access)
    primary_model = "openai/gpt-4o-mini"
    secondary_model = "gemini/gemini-2.0-flash-exp"
    
    try:
        # Attempt Primary Model
        response = completion(
            model=primary_model,
            messages=messages,
            fallbacks=[secondary_model], 
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
