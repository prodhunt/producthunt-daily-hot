import os

class BaseLLMProvider:
    def generate_keywords(self, name, tagline, description):
        raise NotImplementedError

    def translate_text(self, text):
        raise NotImplementedError

def get_llm_provider():
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        from .llm_openai import OpenAILLMProvider
        return OpenAILLMProvider()
    elif provider == "gemini":
        from .llm_gemini import GeminiLLMProvider
        return GeminiLLMProvider()
    elif provider == "deepseek":
        from .llm_deepseek import DeepSeekLLMProvider
        return DeepSeekLLMProvider()
    elif provider == "openrouter":
        from .llm_openrouter import OpenRouterLLMProvider
        return OpenRouterLLMProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")