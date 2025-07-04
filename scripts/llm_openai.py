import os
import openai
import requests
from bs4 import BeautifulSoup

from llm_provider import BaseLLMProvider

class OpenAILLMProvider(BaseLLMProvider):
    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        self.api_base = os.getenv('OPENAI_API_BASE')  # 支持自定义API基础URL
        
        # 如果设置了自定义API基础URL，则使用它
        client_kwargs = {"api_key": self.api_key}
        if self.api_base:
            client_kwargs["base_url"] = self.api_base
            
        self.client = openai.Client(**client_kwargs)

    def generate_keywords(self, name, tagline, description):
        prompt = self.KEYWORDS_USER_PROMPT_TEMPLATE.format(
            name=name,
            tagline=tagline,
            description=description
        )
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.KEYWORDS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0.7,
        )
        keywords = response.choices[0].message.content.strip()
        return keywords

    def translate_text(self, text):
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.TRANSLATION_SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
        
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
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.WEBPAGE_ANALYSIS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=500,
                temperature=0.7,
            )
            
            return {
                "url": url,
                "title": title,
                "summary": response.choices[0].message.content.strip(),
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
            prompt = self.HUGO_TAGS_USER_PROMPT_TEMPLATE.format(
                products_info=products_info
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.HUGO_TAGS_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=200,
                temperature=0.3,  # 降低温度以获得更一致的结果
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"生成Hugo标签失败: {e}")
            # 返回默认标签和关键词
            return '''{"tags": ["Product Hunt", "每日热榜", "创新产品"], "keywords": ["Product Hunt", "PH热榜", "今日新品", "创新产品推荐", "科技产品"]}'''