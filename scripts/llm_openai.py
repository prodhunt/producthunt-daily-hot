import os
import openai

from .llm_provider import BaseLLMProvider

class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        openai.api_key = api_key
        self.client = openai.Client(api_key=api_key)

    def generate_keywords(self, name, tagline, description):
        prompt = f"根据以下内容生成适合的中文关键词，用英文逗号分隔开：\n\n产品名称：{name}\n\n标语：{tagline}\n\n描述：{description}"
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate suitable Chinese keywords based on the product information provided. The keywords should be separated by commas."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0.7,
        )
        keywords = response.choices[0].message.content.strip()
        return keywords

    def translate_text(self, text):
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "你是世界上最专业的翻译工具，擅长英文和中文互译。"},
                {"role": "user", "content": text},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()