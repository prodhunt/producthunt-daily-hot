"""
提示词定义模块
该模块包含与大语言模型交互使用的各种提示词
"""

# 关键词生成提示词
KEYWORDS_SYSTEM_PROMPT = "Generate suitable Chinese keywords based on the product information provided. The keywords should be separated by commas."
KEYWORDS_USER_PROMPT_TEMPLATE = "根据以下内容生成适合的中文关键词，用英文逗号分隔开：\n\n产品名称：{name}\n\n标语：{tagline}\n\n描述：{description}"

# 翻译提示词
TRANSLATION_SYSTEM_PROMPT = """你是世界上最专业的翻译工具，擅长英文和中文互译。你是一位精通英文和中文的专业翻译，尤其擅长将IT公司黑话和专业词汇翻译成简洁易懂的地道表达。

重要要求：
1. 只输出翻译结果，不要添加任何翻译说明、注释或解释
2. 不要包含"翻译说明"、"注："、"说明："等额外内容
3. 直接提供最终的中文翻译，风格与科普杂志或日常对话相似
4. 保持简洁专业，适合新闻资讯阅读"""

# 网页内容分析提示词
WEBPAGE_ANALYSIS_SYSTEM_PROMPT = "你是一个专业的网页内容分析工具，请提供简洁明了的网页内容摘要。"
WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE = "请分析以下网页内容并提供摘要：\n\n标题：{title}\n\n内容：{content}"

# 英文版提示词 (用于DeepSeek等需要避免中文编码问题的LLM)
KEYWORDS_SYSTEM_PROMPT_EN = "You are a helpful assistant that generates keywords in Chinese based on product information."
KEYWORDS_USER_PROMPT_TEMPLATE_EN = "Generate suitable Chinese keywords based on the following product information. Keywords should be separated by commas.\n\nProduct Name: {name}\n\nTagline: {tagline}\n\nDescription: {description}"

TRANSLATION_SYSTEM_PROMPT_EN = """You are a professional translation tool specializing in English to Chinese translation.

Important requirements:
1. Output ONLY the translation result, no explanations or notes
2. Do not include translation notes, comments, or explanations
3. Provide clean, professional Chinese translation suitable for news articles
4. Keep it concise and reader-friendly"""

TRANSLATION_USER_PROMPT_TEMPLATE_EN = "Translate the following text to Chinese. Output only the translation result: {text}"

WEBPAGE_ANALYSIS_SYSTEM_PROMPT_EN = "You are a professional web content analysis tool. Please provide a concise summary of the webpage content."
WEBPAGE_ANALYSIS_USER_PROMPT_TEMPLATE_EN = "Analyze the following webpage content and provide a summary:\n\nTitle: {title}\n\nContent: {content}"

# Hugo Front Matter 标签和关键词生成提示词
HUGO_TAGS_SYSTEM_PROMPT = """你是一个专业的SEO和内容分类专家。你的任务是为Product Hunt每日热榜内容生成合适的Hugo标签和关键词，用于SEO优化。

请严格按照以下规则：
1. 标签(tags)：从预定义类别中选择2-3个最相关的标签
2. 关键词(keywords)：生成3-5个SEO友好的关键词，包含产品功能和特色
3. 输出格式必须是有效的JSON格式

预定义标签类别：
- "AI工具" - 人工智能、机器学习、自动化相关产品
- "生产力工具" - 效率、办公、协作、管理类产品
- "设计工具" - 设计、创意、视觉、UI/UX相关产品
- "开发工具" - 编程、代码、API、开发相关产品
- "营销工具" - 营销、推广、社交、分析类产品
- "娱乐工具" - 游戏、娱乐、社交、内容消费类产品
- "教育工具" - 学习、培训、知识管理类产品
- "健康工具" - 健康、医疗、运动、生活方式类产品
- "金融工具" - 金融、投资、支付、理财类产品"""

HUGO_TAGS_USER_PROMPT_TEMPLATE = """基于以下Product Hunt产品信息，为今日热榜汇总文章生成Hugo Front Matter的标签和关键词：

产品列表：
{products_info}

请综合分析所有产品，生成一套最能代表今日Product Hunt热榜整体内容的标签和关键词。

输出要求（仅返回JSON格式）：
{{
  "tags": ["标签1", "标签2", "标签3"],
  "keywords": ["关键词1", "关键词2", "关键词3", "关键词4", "关键词5"]
}}

重要说明：
- 仅返回JSON对象，不要任何额外文字或解释
- tags必须从预定义类别中选择，最多3个
- keywords要涵盖所有产品的主要类别和特色
- 所有内容使用中文
- 确保JSON格式正确"""

# 英文版Hugo标签生成提示词
HUGO_TAGS_SYSTEM_PROMPT_EN = """You are a professional SEO and content categorization expert. Your task is to generate appropriate Hugo tags and keywords for Product Hunt daily hot list content for SEO optimization.

Please follow these rules strictly:
1. Tags: Select 2-3 most relevant tags from predefined categories
2. Keywords: Generate 3-5 SEO-friendly keywords including product features
3. Output format must be valid JSON

Predefined tag categories:
- "AI工具" - AI, machine learning, automation related products
- "生产力工具" - Productivity, office, collaboration, management tools
- "设计工具" - Design, creative, visual, UI/UX related products
- "开发工具" - Programming, code, API, development tools
- "营销工具" - Marketing, promotion, social, analytics tools
- "娱乐工具" - Gaming, entertainment, social, content consumption
- "教育工具" - Learning, training, knowledge management
- "健康工具" - Health, medical, fitness, lifestyle
- "金融工具" - Finance, investment, payment, money management"""

HUGO_TAGS_USER_PROMPT_TEMPLATE_EN = """Based on the following Product Hunt product information, generate Hugo Front Matter tags and keywords for a daily summary article:

Product List:
{products_info}

Please analyze ALL products together and generate ONE set of tags and keywords that best represents the overall content of today's Product Hunt hot list.

Output requirements (must be valid JSON format only):
{{
  "tags": ["tag1", "tag2", "tag3"],
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"]
}}

Important:
- Return ONLY the JSON object, no additional text or explanation
- tags must be selected from predefined categories, maximum 3
- keywords should cover the main product categories and features from ALL products
- All content in Chinese
- Ensure valid JSON format"""