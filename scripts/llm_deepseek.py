import os
import json
import requests
from bs4 import BeautifulSoup
from llm_provider import BaseLLMProvider

class DeepSeekLLMProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        # 支持自定义API基础URL
        self.base_url = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1/chat/completions")
        if not self.api_key:
            raise ValueError("Missing DEEPSEEK_API_KEY in environment variables.")

    def _call_deepseek(self, messages, max_tokens=256, temperature=0.7):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 创建请求数据
        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        # 使用json.dumps和requests.post的data参数，而不是json参数
        # 这样可以确保请求体的编码由requests库正确处理
        json_data = json.dumps(data)
        response = requests.post(
            self.base_url, 
            headers=headers, 
            data=json_data.encode('utf-8')
        )
        
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"].strip()

    def generate_keywords(self, name, tagline, description):
        # 使用英文提示，避免中文字符可能导致的编码问题
        prompt = self.KEYWORDS_USER_PROMPT_TEMPLATE_EN.format(
            name=name,
            tagline=tagline,
            description=description
        )
        messages = [
            {"role": "system", "content": self.KEYWORDS_SYSTEM_PROMPT_EN},
            {"role": "user", "content": prompt}
        ]
        return self._call_deepseek(messages, max_tokens=50, temperature=0.7)

    def translate_text(self, text):
        # 使用英文提示，避免中文字符可能导致的编码问题
        prompt = self.TRANSLATION_USER_PROMPT_TEMPLATE_EN.format(text=text)
        messages = [
            {"role": "system", "content": self.TRANSLATION_SYSTEM_PROMPT_EN},
            {"role": "user", "content": prompt}
        ]
        return self._call_deepseek(messages, max_tokens=500, temperature=0.7)
        
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
            title = soup.title.string if soup.title else "No title"
            
            # 提取正文内容（简单实现，可能需要针对不同网站优化）
            paragraphs = soup.find_all('p')
            content = "\n".join([p.text for p in paragraphs[:10]])  # 限制内容长度
            
            # 使用LLM分析内容，使用英文提示避免编码问题
            prompt = self.WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE_EN.format(
                title=title,
                content=content[:3000] + "..."  # 限制内容长度
            )
            
            messages = [
                {"role": "system", "content": self.WEBPAGE_ANALYSIS_SYSTEM_PROMPT_EN},
                {"role": "user", "content": prompt}
            ]
            summary = self._call_deepseek(messages, max_tokens=500, temperature=0.7)
            
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
            # 使用英文提示，避免中文字符可能导致的编码问题
            prompt = self.HUGO_TAGS_USER_PROMPT_TEMPLATE_EN.format(
                products_info=products_info
            )

            messages = [
                {"role": "system", "content": self.HUGO_TAGS_SYSTEM_PROMPT_EN},
                {"role": "user", "content": prompt}
            ]

            result = self._call_deepseek(messages, max_tokens=200, temperature=0.3)
            return result

        except Exception as e:
            print(f"生成Hugo标签失败: {e}")
            # 返回默认标签和关键词
            return '''{"tags": ["Product Hunt", "每日热榜", "创新产品"], "keywords": ["Product Hunt", "PH热榜", "今日新品", "创新产品推荐", "科技产品"]}'''