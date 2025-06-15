import os
import requests
from bs4 import BeautifulSoup
from llm_provider import BaseLLMProvider

class GeminiLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        # 支持自定义API基础URL
        self.base_url = os.getenv("GEMINI_API_BASE", "https://generativelanguage.googleapis.com/v1beta/models")
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY in environment variables.")

    def _call_gemini(self, messages, max_tokens=256, temperature=0.7):
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        data = {
            "contents": [{"role": m["role"], "parts": [{"text": m["content"]}]} for m in messages],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        response = requests.post(url, json=data)
        response.raise_for_status()

        # 添加调试信息
        response_data = response.json()
        if "candidates" not in response_data or not response_data["candidates"]:
            raise Exception(f"Gemini API响应格式错误: {response_data}")

        candidate = response_data["candidates"][0]

        # 检查是否被安全过滤器阻止
        if "finishReason" in candidate and candidate["finishReason"] != "STOP":
            raise Exception(f"Gemini请求被拒绝，原因: {candidate.get('finishReason', 'UNKNOWN')}")

        if "content" not in candidate:
            raise Exception(f"Gemini响应中没有content字段: {candidate}")

        content = candidate["content"]
        if "parts" not in content or not content["parts"]:
            raise Exception(f"Gemini响应中没有parts字段: {content}")

        return content["parts"][0]["text"]

    def generate_keywords(self, name, tagline, description):
        prompt = self.KEYWORDS_USER_PROMPT_TEMPLATE.format(
            name=name,
            tagline=tagline,
            description=description
        )
        messages = [
            {"role": "user", "content": prompt}
        ]
        return self._call_gemini(messages, max_tokens=50, temperature=0.7)

    def translate_text(self, text):
        messages = [
            {"role": "user", "content": f"请将以下内容进行翻译：\n{text}"}
        ]
        return self._call_gemini(messages, max_tokens=500, temperature=0.7)
        
    def process_url(self, url):
        """处理URL内容并返回分析结果"""
        try:
            # 获取URL内容
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 提取标题和正文内容
            title = soup.title.string if soup.title else "无标题"
            
            # 提取正文内容（简单实现，可能需要针对不同网站优化）
            paragraphs = soup.find_all('p')
            content = "\n".join([p.text for p in paragraphs[:10]])  # 限制内容长度
            
            # 使用LLM分析内容
            prompt = self.WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE.format(
                title=title,
                content=content[:3000] + "..."  # 限制内容长度
            )
            
            messages = [
                {"role": "user", "content": prompt}
            ]
            summary = self._call_gemini(messages, max_tokens=500, temperature=0.7)
            
            return {
                "url": url,
                "title": title,
                "summary": summary,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "url": url,
                "error": str(e),
                "status": "error"
            }

    def generate_hugo_tags_and_keywords(self, products_info):
        """生成Hugo Front Matter的标签和关键词"""
        try:
            # 组合系统提示和用户提示
            system_prompt = self.HUGO_TAGS_SYSTEM_PROMPT
            user_prompt = self.HUGO_TAGS_USER_PROMPT_TEMPLATE.format(
                products_info=products_info
            )

            # Gemini需要将系统提示和用户提示合并
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"

            messages = [
                {"role": "user", "content": combined_prompt}
            ]

            result = self._call_gemini(messages, max_tokens=200, temperature=0.3)
            return result

        except Exception as e:
            print(f"生成Hugo标签失败: {e}")
            # 返回默认标签和关键词
            return '''{"tags": ["Product Hunt", "每日热榜", "创新产品"], "keywords": ["Product Hunt", "PH热榜", "今日新品", "创新产品推荐", "科技产品"]}'''