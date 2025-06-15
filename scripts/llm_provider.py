import os
# 导入所有提示词常量
try:
    # 尝试从scripts包导入（从项目根目录运行时）
    from scripts.prompts import (
        # 中文提示词
        KEYWORDS_SYSTEM_PROMPT,
        KEYWORDS_USER_PROMPT_TEMPLATE,
        TRANSLATION_SYSTEM_PROMPT,
        WEBPAGE_ANALYSIS_SYSTEM_PROMPT,
        WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE,
        HUGO_TAGS_SYSTEM_PROMPT,
        HUGO_TAGS_USER_PROMPT_TEMPLATE,
        # 英文提示词
        KEYWORDS_SYSTEM_PROMPT_EN,
        KEYWORDS_USER_PROMPT_TEMPLATE_EN,
        TRANSLATION_SYSTEM_PROMPT_EN,
        TRANSLATION_USER_PROMPT_TEMPLATE_EN,
        WEBPAGE_ANALYSIS_SYSTEM_PROMPT_EN,
        WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE_EN,
        HUGO_TAGS_SYSTEM_PROMPT_EN,
        HUGO_TAGS_USER_PROMPT_TEMPLATE_EN
    )
except ImportError:
    # 从当前目录导入（从scripts目录内运行时）
    from prompts import (
        # 中文提示词
        KEYWORDS_SYSTEM_PROMPT,
        KEYWORDS_USER_PROMPT_TEMPLATE,
        TRANSLATION_SYSTEM_PROMPT,
        WEBPAGE_ANALYSIS_SYSTEM_PROMPT,
        WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE,
        HUGO_TAGS_SYSTEM_PROMPT,
        HUGO_TAGS_USER_PROMPT_TEMPLATE,
        # 英文提示词
        KEYWORDS_SYSTEM_PROMPT_EN,
        KEYWORDS_USER_PROMPT_TEMPLATE_EN,
        TRANSLATION_SYSTEM_PROMPT_EN,
        TRANSLATION_USER_PROMPT_TEMPLATE_EN,
        WEBPAGE_ANALYSIS_SYSTEM_PROMPT_EN,
        WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE_EN,
        HUGO_TAGS_SYSTEM_PROMPT_EN,
        HUGO_TAGS_USER_PROMPT_TEMPLATE_EN
    )

class BaseLLMProvider:
    # 中文提示词
    KEYWORDS_SYSTEM_PROMPT = KEYWORDS_SYSTEM_PROMPT
    KEYWORDS_USER_PROMPT_TEMPLATE = KEYWORDS_USER_PROMPT_TEMPLATE
    TRANSLATION_SYSTEM_PROMPT = TRANSLATION_SYSTEM_PROMPT
    WEBPAGE_ANALYSIS_SYSTEM_PROMPT = WEBPAGE_ANALYSIS_SYSTEM_PROMPT
    WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE = WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE
    HUGO_TAGS_SYSTEM_PROMPT = HUGO_TAGS_SYSTEM_PROMPT
    HUGO_TAGS_USER_PROMPT_TEMPLATE = HUGO_TAGS_USER_PROMPT_TEMPLATE

    # 英文提示词
    KEYWORDS_SYSTEM_PROMPT_EN = KEYWORDS_SYSTEM_PROMPT_EN
    KEYWORDS_USER_PROMPT_TEMPLATE_EN = KEYWORDS_USER_PROMPT_TEMPLATE_EN
    TRANSLATION_SYSTEM_PROMPT_EN = TRANSLATION_SYSTEM_PROMPT_EN
    TRANSLATION_USER_PROMPT_TEMPLATE_EN = TRANSLATION_USER_PROMPT_TEMPLATE_EN
    WEBPAGE_ANALYSIS_SYSTEM_PROMPT_EN = WEBPAGE_ANALYSIS_SYSTEM_PROMPT_EN
    WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE_EN = WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE_EN
    HUGO_TAGS_SYSTEM_PROMPT_EN = HUGO_TAGS_SYSTEM_PROMPT_EN
    HUGO_TAGS_USER_PROMPT_TEMPLATE_EN = HUGO_TAGS_USER_PROMPT_TEMPLATE_EN
    
    def generate_keywords(self, name, tagline, description):
        raise NotImplementedError

    def translate_text(self, text):
        raise NotImplementedError

    def process_url(self, url):
        """处理URL内容并返回分析结果"""
        raise NotImplementedError

    def generate_hugo_tags_and_keywords(self, products_info):
        """生成Hugo Front Matter的标签和关键词"""
        raise NotImplementedError

def get_llm_provider():
    """
    根据环境变量获取LLM提供商实例
    支持通过LLM_PROVIDER环境变量选择提供商
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    
    if provider == "openai":
        from llm_openai import OpenAILLMProvider
        return OpenAILLMProvider()
    elif provider == "gemini":
        from llm_gemini import GeminiLLMProvider
        return GeminiLLMProvider()
    elif provider == "deepseek":
        from llm_deepseek import DeepSeekLLMProvider
        return DeepSeekLLMProvider()
    elif provider == "openrouter":
        from llm_openrouter import OpenRouterLLMProvider
        return OpenRouterLLMProvider()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")