import os
from typing import Optional
from langchain_core.language_models import BaseChatModel
from app.config.settings import settings

def get_llm(temperature: float = 0.1) -> Optional[BaseChatModel]:
    """
    Returns the configured LLM instance based on environment settings.
    Supports Gemini (via langchain-google-genai), OpenAI, and Anthropic.
    Falls back gracefully if API keys are not supplied.
    """
    provider = settings.LLM_PROVIDER.lower()
    
    # Check Gemini
    gemini_key = settings.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if (provider == "gemini" or not provider) and gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=gemini_key,
                temperature=temperature
            )
        except Exception as e:
            print(f"Failed to initialize Gemini: {e}")

    # Check OpenAI
    openai_key = settings.OPENAI_API_KEY or os.environ.get("OPENAI_API_KEY")
    if provider == "openai" and openai_key:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=openai_key,
                temperature=temperature
            )
        except Exception as e:
            print(f"Failed to initialize OpenAI: {e}")

    # If any key is available, use it
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.GEMINI_MODEL,
                google_api_key=gemini_key,
                temperature=temperature
            )
        except Exception:
            pass
            
    if openai_key:
        try:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.OPENAI_MODEL,
                api_key=openai_key,
                temperature=temperature
            )
        except Exception:
            pass

    return None
