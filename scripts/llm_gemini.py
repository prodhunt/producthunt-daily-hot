import os
import requests
from .llm_provider import BaseLLMProvider

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        if not self.api_key:
            raise Exception("GEMINI_API_KEY not set.")

    def _call_gemini(self, prompt, max_tokens=512):
        headers = {"Content-Type": "application/json"}
        params = {"key": self.api_key}
        data = {
            "contents": [
                {"parts": [{"text": prompt}]}
            ],
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": 0.7,
            }
        }
        response = requests.post(self.api_url, headers=headers, params=params, json=data)
        print(f"Gemini API response status code: {response.status_code}")
        print(f"Gemini API response content: {response.content}")
        response.raise_for_status()
        result = response.json()
        # Gemini 返回结构通常为 result['candidates'][0]['content']['parts'][0]['text']
        try:
            return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            raise Exception(f"Gemini response error: {e}, full response: {result}")

    def generate_keywords(self, name, tagline, description):
        prompt = (
            f"根据以下内容生成适合的中文关键词，用英文逗号分隔开：\n\n"
            f"产品名称：{name}\n\n"
            f"标语：{tagline}\n\n"
            f"描述：{description}"
        )
        return self._call_gemini(prompt, max_tokens=50)

    def translate_text(self, text):
        prompt = (
            "你是一位精通英文和中文的专业翻译，尤其擅长将IT、科技、互联网等领域的英文内容翻译成流畅地道的中文。请将下面内容翻译成中文：\n\n"
            + text
        )
        return self._call_gemini(prompt, max_tokens=500)