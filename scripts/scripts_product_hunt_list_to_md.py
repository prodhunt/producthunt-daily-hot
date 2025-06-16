import sys
import os
import json
import asyncio
import time

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv 模块未安装，将直接使用环境变量")

import requests
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
import pytz
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor

from scripts.llm_provider import get_llm_provider
from scripts.image_selector import ProductHuntImageSelector

llm = get_llm_provider()

class Product:
    def __init__(self, id: str, name: str, tagline: str, description: str, votesCount: int, createdAt: str, featuredAt: str, website: str, url: str, media=None, **kwargs):
        self.name = name
        self.tagline = tagline
        self.description = description
        self.votes_count = votesCount
        self.created_at = self.convert_to_beijing_time(createdAt)
        self.featured = "是" if featuredAt else "否"
        self.website = website
        self.url = url
        self.og_image_url = self.get_image_url_from_media(media)
        self.keyword = self.generate_keywords()
        self.translated_tagline = self.translate_text(self.tagline)
        self.translated_description = self.translate_text(self.description)

    def get_image_url_from_media(self, media):
        try:
            if media and isinstance(media, list) and len(media) > 0:
                image_url = media[0].get('url', '')
                if image_url:
                    print(f"成功从API获取图片URL: {self.name}")
                    return image_url
            print(f"API未返回图片，尝试使用备用方法: {self.name}")
            backup_url = self.fetch_og_image_url()
            if backup_url:
                print(f"使用备用方法获取图片URL成功: {self.name}")
                return backup_url
            else:
                print(f"无法获取图片URL: {self.name}")
            return ""
        except Exception as e:
            print(f"获取图片URL时出错: {self.name}, 错误: {e}")
            return ""

    def fetch_og_image_url(self) -> str:
        try:
            response = requests.get(self.url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                og_image = soup.find("meta", property="og:image")
                if og_image:
                    return og_image["content"]
                twitter_image = soup.find("meta", name="twitter:image")
                if twitter_image:
                    return twitter_image["content"]
            return ""
        except Exception as e:
            print(f"获取OG图片URL时出错: {self.name}, 错误: {e}")
            return ""

    def generate_keywords(self) -> str:
        try:
            print(f"正在为 {self.name} 生成关键词...")
            keywords = llm.generate_keywords(self.name, self.tagline, self.description)
            if ',' not in keywords:
                keywords = ', '.join(keywords.split())
            print(f"成功为 {self.name} 生成关键词")
            return keywords
        except Exception as e:
            print(f"关键词生成失败: {e}")
            words = set((self.name + ", " + self.tagline).replace("&", ",").replace("|", ",").replace("-", ",").split(","))
            return ", ".join([word.strip() for word in words if word.strip()])

    def translate_text(self, text: str) -> str:
        try:
            print(f"正在翻译 {self.name} 的内容...")
            translated_text = llm.translate_text(text)
            print(f"成功翻译 {self.name} 的内容")
            return translated_text
        except Exception as e:
            print(f"翻译过程中出错: {e}")
            return text

    def convert_to_beijing_time(self, utc_time_str: str) -> str:
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
        return beijing_time.strftime('%Y年%m月%d日 %p%I:%M (北京时间)')

    def to_markdown(self, rank: int) -> str:
        # 优化图片Alt文本，提供更详细的SEO描述
        seo_alt_text = f"{self.name} - {self.translated_tagline}，获得{self.votes_count}票"
        if self.featured == "是":
            seo_alt_text += "，Product Hunt精选产品"

        # 优化图片URL，清理现有参数避免重复
        if "?" in self.og_image_url:
            base_url = self.og_image_url.split("?")[0]
        else:
            base_url = self.og_image_url
        optimized_image_url = f"{base_url}?auto=format&w=800&h=400&fit=crop&q=85&fm=webp"
        og_image_markdown = f"![{seo_alt_text}]({optimized_image_url})"

        return (
            f"### {rank}. {self.name} - {self.translated_tagline}\n\n"
            f"**介绍**：{self.translated_description}  \n"
            f"**官方网站**: [立即访问]({self.website})  \n\n"
            f"{og_image_markdown}\n\n"
            f"**票数**: 🔺{self.votes_count}  \n"
            f"**是否精选**：{self.featured}  \n"
            f"**发布时间**：{self.created_at}\n\n"
            f"---\n\n"
        )

def get_producthunt_token():
    developer_token = os.getenv('PRODUCTHUNT_DEVELOPER_TOKEN')
    if developer_token:
        print("使用 PRODUCTHUNT_DEVELOPER_TOKEN 环境变量")
        return developer_token
    client_id = os.getenv('PRODUCTHUNT_CLIENT_ID')
    client_secret = os.getenv('PRODUCTHUNT_CLIENT_SECRET')
    if not client_id or not client_secret:
        raise Exception("Product Hunt client ID or client secret not found in environment variables")
    token_url = "https://api.producthunt.com/v2/oauth/token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials"
    }
    try:
        response = requests.post(token_url, json=payload)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")
    except Exception as e:
        print(f"获取 Product Hunt 访问令牌时出错: {e}")
        raise Exception(f"Failed to get Product Hunt access token: {e}")

def fetch_product_hunt_data():
    token = get_producthunt_token()
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    url = "https://api.producthunt.com/v2/api/graphql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "DecohackBot/1.0 (https://decohack.com)",
        "Origin": "https://decohack.com",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Connection": "keep-alive"
    }
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    base_query = """
    {
      posts(order: VOTES, postedAfter: "%sT00:00:00Z", postedBefore: "%sT23:59:59Z", after: "%s") {
        nodes {
          id
          name
          tagline
          description
          votesCount
          createdAt
          featuredAt
          website
          url
          media {
            url
            type
            videoUrl
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
    """
    all_posts = []
    has_next_page = True
    cursor = ""
    while has_next_page and len(all_posts) < 10:
        query = base_query % (date_str, date_str, cursor)
        try:
            response = session.post(url, headers=headers, json={"query": query})
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            raise Exception(f"Failed to fetch data from Product Hunt: {e}")
        data = response.json()['data']['posts']
        posts = data['nodes']
        all_posts.extend(posts)
        has_next_page = data['pageInfo']['hasNextPage']
        cursor = data['pageInfo']['endCursor']
    return [Product(**post) for post in sorted(all_posts, key=lambda x: x['votesCount'], reverse=True)[:10]]

def fetch_mock_data():
    print("使用模拟数据进行测试...")
    mock_products = [
        {
            "id": "1",
            "name": "Venice",
            "tagline": "Private & censorship-resistant AI | Unlock unlimited intelligence",
            "description": "Venice is a private, censorship-resistant AI platform powered by open-source models and decentralized infrastructure.",
            "votesCount": 566,
            "createdAt": "2025-03-07T16:01:00Z",
            "featuredAt": "2025-03-07T16:01:00Z",
            "website": "https://www.producthunt.com/r/4D6Z6F7I3SXTGN",
            "url": "https://www.producthunt.com/posts/venice-3",
            "media": [
                {
                    "url": "https://ph-files.imgix.net/97baee49-6dda-47f5-8a47-91d2c56e1976.jpeg",
                    "type": "image",
                    "videoUrl": None
                }
            ]
        },
        {
            "id": "2",
            "name": "Mistral OCR",
            "tagline": "Introducing the world's most powerful document understanding API",
            "description": "Mistral OCR—an advanced, lightweight optical character recognition model focused on speed, accuracy, and efficiency.",
            "votesCount": 477,
            "createdAt": "2025-03-07T16:01:00Z",
            "featuredAt": "2025-03-07T16:01:00Z",
            "website": "https://www.producthunt.com/r/SPXNTAWQSVRLGH",
            "url": "https://www.producthunt.com/posts/mistral-ocr",
            "media": [
                {
                    "url": "https://ph-files.imgix.net/4224517b-29e4-4944-98c9-2eee59374870.png",
                    "type": "image",
                    "videoUrl": None
                }
            ]
        }
    ]
    return [Product(**product) for product in mock_products]

def generate_hugo_front_matter(products, date_str):
    """生成Hugo Front Matter"""
    try:
        # 准备产品信息用于标签生成
        products_info = ""
        total_votes = 0

        for i, product in enumerate(products[:5], 1):  # 只使用前5个产品
            total_votes += product.votes_count
            products_info += f"{i}. {product.name}\n"
            products_info += f"   - 标语: {product.tagline}\n"
            products_info += f"   - 描述: {product.description[:100]}...\n"
            products_info += f"   - 票数: {product.votes_count}\n\n"

        # 生成标签和关键词
        print("🔄 正在生成Hugo标签和关键词...")
        tags_result = llm.generate_hugo_tags_and_keywords(products_info)

        # 解析JSON结果
        try:
            tags_data = json.loads(tags_result)
            tags = tags_data.get('tags', ['Product Hunt', '每日热榜', '创新产品'])
            keywords = tags_data.get('keywords', ['Product Hunt', 'PH热榜', '今日新品'])
        except json.JSONDecodeError:
            print("⚠️ 标签生成结果解析失败，使用默认标签")
            tags = ['Product Hunt', '每日热榜', '创新产品']
            keywords = ['Product Hunt', 'PH热榜', '今日新品', '创新产品推荐', '科技产品']

        # 选择封面图片
        image_selector = ProductHuntImageSelector()
        # 转换产品数据格式
        products_data = []
        for product in products:
            product_dict = {
                'name': product.name,
                'tagline': product.tagline,
                'votesCount': product.votes_count,
                'media': []
            }
            # 如果有图片URL，添加到media中
            if hasattr(product, 'og_image_url') and product.og_image_url:
                product_dict['media'] = [{'url': product.og_image_url, 'type': 'image'}]
            products_data.append(product_dict)

        cover_url, alt_text = image_selector.select_best_cover_image(products_data)

        # 生成优化的标题和描述
        top_product = products[0] if products else None
        featured_count = sum(1 for p in products if p.featured == "是")
        ai_count = sum(1 for p in products if 'ai' in (p.name + p.tagline + p.description).lower())

        if top_product:
            # 计算AI工具占比
            ai_percentage = round((ai_count / len(products)) * 100) if products else 0

            # 优化标题，包含更多SEO信息
            if ai_percentage >= 50:
                title = f"Product Hunt 今日热榜 {date_str} | AI工具占据{ai_percentage}%份额，{top_product.name}{top_product.votes_count}票领跑"
            else:
                title = f"Product Hunt 今日热榜 {date_str} | {top_product.name}{top_product.votes_count}票领跑，{len(products)}款创新产品"

            # 优化描述，提供更多价值信息
            second_product = products[1].name if len(products) > 1 else ""
            description = f"Product Hunt {date_str}热榜深度分析：{top_product.name}获{top_product.votes_count}票领跑"
            if second_product:
                description += f"，{second_product}等"
            description += f"{len(products)}款创新产品完整解析。总票数{total_votes}票，精选产品{featured_count}款"
            if ai_percentage >= 50:
                description += f"，AI工具占据{ai_percentage}%份额"
            description += "。"
        else:
            title = f"Product Hunt 今日热榜 {date_str}"
            description = f"今日Product Hunt热榜精选创新产品推荐"

        # 优化封面图片URL
        if cover_url:
            # 清理现有参数，避免重复
            if "?" in cover_url:
                base_url = cover_url.split("?")[0]
            else:
                base_url = cover_url
            # 添加SEO友好的图片参数
            cover_url = f"{base_url}?auto=format&w=1200&h=630&fit=crop&q=85&fm=webp"

        # 构建专业SEO优化的Front Matter
        front_matter = "---\n"
        front_matter += f'title: "{title}"\n'
        front_matter += f'date: {date_str}T00:00:00+08:00\n'
        front_matter += f'lastmod: {date_str}T12:00:00+08:00\n'
        front_matter += f'description: "{description}"\n'
        front_matter += f'slug: "product-hunt-daily-{date_str}"\n'
        front_matter += f'categories: ["科技产品", "Product Hunt"]\n'
        front_matter += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
        front_matter += f'keywords: {json.dumps(keywords, ensure_ascii=False)}\n'
        front_matter += f'author: "Product Hunt Daily"\n'

        # 添加Hugo Stack支持的封面图片字段（使用正确的cover结构）
        if cover_url:
            front_matter += f'cover:\n'
            front_matter += f'  image: "{cover_url}"\n'
            front_matter += f'  alt: "Product Hunt今日热榜：{top_product.name if top_product else "创新产品"} - {top_product.translated_tagline if top_product and top_product.translated_tagline else "热门产品"} ({top_product.votes_count if top_product else 0}票)"\n'

        # Hugo Stack主题配置（只保留支持的字段）
        front_matter += '\n# Hugo Stack主题配置\n'
        front_matter += 'featured: true\n'
        front_matter += 'toc: true\n'
        front_matter += 'math: false\n'
        front_matter += 'lightgallery: true\n'
        front_matter += 'comments: true\n'
        front_matter += 'readingTime: true\n'
        front_matter += "---\n\n"

        print("✅ Hugo Front Matter生成成功")
        return front_matter

    except Exception as e:
        print(f"⚠️ Hugo Front Matter生成失败: {e}")
        # 返回基础的Front Matter
        return f"""---
title: "Product Hunt 今日热榜 {date_str}"
date: {date_str}
description: "今日Product Hunt热榜精选创新产品推荐"
tags: ["Product Hunt", "每日热榜", "创新产品"]
keywords: ["Product Hunt", "PH热榜", "今日新品", "创新产品推荐", "科技产品"]
votes: {sum(p.votes_count for p in products) if products else 0}
---

"""

def generate_industry_analysis_content(products):
    """生成行业分析内容"""
    try:
        # 获取LLM提供商
        llm = get_llm_provider()

        # 准备产品信息用于行业分析
        products_info = ""
        for i, product in enumerate(products[:10], 1):  # 使用所有产品进行分析
            products_info += f"{i}. {product.name}\n"
            products_info += f"   - 标语: {product.tagline}\n"
            products_info += f"   - 描述: {product.description[:100]}...\n"
            products_info += f"   - 票数: {product.votes_count}\n"
            products_info += f"   - 类别: {categorize_product(product)}\n\n"

        print("🔄 正在生成行业趋势分析...")
        industry_analysis = llm.generate_industry_analysis(products_info)
        print("✅ 行业趋势分析生成成功")

        return industry_analysis

    except Exception as e:
        print(f"⚠️ 行业分析生成失败: {e}")
        return "## 🔍 今日科技趋势分析\n\n今日Product Hunt热榜展现了科技产品的多元化发展趋势，涵盖人工智能、生产力工具、开发者工具等多个领域，反映了当前科技创新的活跃态势。"

def categorize_product(product):
    """简单的产品分类逻辑"""
    name_and_desc = (product.name + " " + product.tagline + " " + product.description).lower()

    if any(keyword in name_and_desc for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml', 'neural', 'gpt', 'llm']):
        return "AI工具"
    elif any(keyword in name_and_desc for keyword in ['finance', 'money', 'investment', 'trading', 'stock', 'crypto', 'payment']):
        return "金融工具"
    elif any(keyword in name_and_desc for keyword in ['code', 'developer', 'programming', 'api', 'github', 'software']):
        return "开发工具"
    elif any(keyword in name_and_desc for keyword in ['design', 'ui', 'ux', 'creative', 'visual', 'graphic']):
        return "设计工具"
    elif any(keyword in name_and_desc for keyword in ['productivity', 'task', 'project', 'team', 'collaboration', 'workflow']):
        return "生产力工具"
    elif any(keyword in name_and_desc for keyword in ['marketing', 'seo', 'social', 'analytics', 'campaign']):
        return "营销工具"
    else:
        return "其他工具"

def generate_markdown(products, date_str):
    today = datetime.now(timezone.utc)
    date_today = today.strftime('%Y-%m-%d')

    # 生成Hugo Front Matter
    front_matter = generate_hugo_front_matter(products, date_today)

    # 生成行业分析内容
    industry_analysis = generate_industry_analysis_content(products)

    # 生成优化的内容结构
    ai_count = sum(1 for p in products if 'ai' in (p.name + p.tagline + p.description).lower())
    ai_percentage = round((ai_count / len(products)) * 100) if products else 0
    top_product = products[0] if products else None

    # 生成标题和描述（用于结构化数据）
    total_votes = sum(p.votes_count for p in products)
    featured_count = sum(1 for p in products if p.featured == "是")

    if top_product:
        if ai_percentage >= 50:
            title = f"Product Hunt 今日热榜 {date_today} | AI工具占据{ai_percentage}%份额，{top_product.name}{top_product.votes_count}票领跑"
        else:
            title = f"Product Hunt 今日热榜 {date_today} | {top_product.name}{top_product.votes_count}票领跑，{len(products)}款创新产品"

        second_product = products[1].name if len(products) > 1 else ""
        description = f"Product Hunt {date_today}热榜深度分析：{top_product.name}获{top_product.votes_count}票领跑"
        if second_product:
            description += f"，{second_product}等"
        description += f"{len(products)}款创新产品完整解析。总票数{total_votes}票，精选产品{featured_count}款"
        if ai_percentage >= 50:
            description += f"，AI工具占据{ai_percentage}%份额"
        description += "。"
    else:
        title = f"Product Hunt 今日热榜 {date_today}"
        description = f"今日Product Hunt热榜精选创新产品推荐"

    # 获取封面图片URL
    cover_url = None
    if products and hasattr(products[0], 'og_image_url') and products[0].og_image_url:
        # 清理现有参数，避免重复
        if "?" in products[0].og_image_url:
            base_url = products[0].og_image_url.split("?")[0]
        else:
            base_url = products[0].og_image_url
        cover_url = f"{base_url}?auto=format&w=1200&h=630&fit=crop&q=85&fm=webp"

    markdown_content = front_matter

    # 添加完整的SEO标签（直接HTML输出，不依赖主题支持）
    # 先处理标题和描述中的引号
    safe_title = title.replace('"', '&quot;')
    safe_description = description.replace('"', '&quot;')

    # 社交媒体标签 + 结构化数据
    seo_tags = f'''<!-- SEO优化标签 -->
<meta property="og:title" content="{safe_title}">
<meta property="og:description" content="{safe_description}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Product Hunt 每日中文热榜">
<meta property="og:url" content="https://yourdomain.com/news/product-hunt-daily-{date_today}/">'''

    if cover_url:
        seo_tags += f'''
<meta property="og:image" content="{cover_url}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">'''

    seo_tags += f'''

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="Product Hunt 今日热榜 | {len(products)}款创新产品推荐">
<meta name="twitter:description" content="{top_product.name if top_product else "创新产品"}等热门产品推荐 #ProductHunt #AI #科技">'''

    if cover_url:
        seo_tags += f'''
<meta name="twitter:image" content="{cover_url}">'''

    seo_tags += f'''

<script type="application/ld+json">
{{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{safe_title}",
  "description": "{safe_description}",
  "author": {{
    "@type": "Organization",
    "name": "Product Hunt Daily"
  }},
  "publisher": {{
    "@type": "Organization",
    "name": "Product Hunt Daily"
  }},
  "datePublished": "{date_today}T00:00:00+08:00",
  "dateModified": "{date_today}T12:00:00+08:00",
  "mainEntityOfPage": {{
    "@type": "WebPage",
    "@id": "https://yourdomain.com/news/product-hunt-daily-{date_today}/"
  }},
  "articleSection": "Technology",
  "wordCount": 2500'''

    if cover_url:
        seo_tags += f''',
  "image": {{
    "@type": "ImageObject",
    "url": "{cover_url}",
    "width": 1200,
    "height": 630
  }}'''

    seo_tags += '''
}
</script>

'''

    markdown_content += seo_tags

    # 优化主标题
    if ai_percentage >= 50:
        markdown_content += f"# Product Hunt 今日热榜 {date_today}：AI工具占据主导地位\n\n"
    else:
        markdown_content += f"# Product Hunt 今日热榜 {date_today}：{top_product.name if top_product else '创新产品'}领跑科技前沿\n\n"

    # 添加今日亮点总览
    markdown_content += "## 📋 今日亮点总览\n\n"
    if products:
        top_3 = products[:3]
        markdown_content += "### 🏆 热门产品推荐\n"
        for i, product in enumerate(top_3, 1):
            rating = "⭐⭐⭐⭐⭐" if product.votes_count >= 300 else "⭐⭐⭐⭐" if product.votes_count >= 200 else "⭐⭐⭐"
            markdown_content += f"- **[{product.name}](#{i}-{product.name.lower().replace(' ', '-')})** - {product.translated_tagline} ({product.votes_count}票) {rating}\n"
        markdown_content += "\n"

    # 添加数据概览
    total_votes = sum(p.votes_count for p in products)
    featured_count = sum(1 for p in products if p.featured == "是")
    hot_products = sum(1 for p in products if p.votes_count >= 200)

    markdown_content += "### 📊 数据统计\n"
    markdown_content += f"- **总产品数**：{len(products)}款创新产品\n"
    markdown_content += f"- **总票数**：{total_votes:,}票\n"
    markdown_content += f"- **平均票数**：{total_votes//len(products) if products else 0}票\n"
    markdown_content += f"- **精选产品**：{featured_count}款\n"
    markdown_content += f"- **热门产品**：{hot_products}款(200+票)\n"
    if ai_percentage > 0:
        markdown_content += f"- **AI工具占比**：{ai_percentage}%\n"
    markdown_content += "\n"

    # 添加行业分析
    markdown_content += "## 🔍 科技趋势深度分析\n\n"
    markdown_content += industry_analysis.replace("## 🔍 今日科技趋势分析", "").strip() + "\n\n"

    # 添加产品详情
    markdown_content += "## 🏆 热门产品详细解析\n\n"

    for rank, product in enumerate(products, 1):
        markdown_content += product.to_markdown(rank)

    # 确保文件生成到项目根目录的data文件夹
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)

    file_name = f"producthunt-daily-{date_today}.md"
    file_path = os.path.join(data_dir, file_name)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    print(f"文件 {file_path} 生成成功并已覆盖。")

def main():
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')

    try:
        products = fetch_product_hunt_data()
    except Exception as e:
        print(f"获取Product Hunt数据失败: {e}")
        print("使用模拟数据继续...")
        products = fetch_mock_data()

    generate_markdown(products, date_str)

if __name__ == "__main__":
    main()