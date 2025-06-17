# AI资讯数据源扩展指南

## 概述

本文档提供了除Product Hunt之外的多种AI和科技资讯数据源，用于丰富AI资讯内容收集，提升信息覆盖面和内容质量。

## 数据源分类

### 1. 官方API数据源

#### GitHub Trending API
**数据内容**：每日/每周/每月热门开源项目
- **API地址**：`https://api.github.com/search/repositories`
- **费用**：免费（有速率限制）
- **数据特点**：
  - AI项目占比很高
  - 可按语言、时间筛选
  - 包含项目描述、星标数、语言等
- **API示例**：
```python
import requests

def get_github_trending_ai():
    url = "https://api.github.com/search/repositories"
    params = {
        "q": "machine learning OR artificial intelligence OR AI",
        "sort": "stars",
        "order": "desc",
        "per_page": 10,
        "created": ">2024-01-01"  # 最近项目
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### Hacker News API
**数据内容**：科技新闻、技术讨论热点
- **API地址**：`https://hacker-news.firebaseio.com/v0/`
- **费用**：完全免费
- **数据特点**：
  - 高质量技术讨论
  - 实时热点追踪
  - 社区投票排序
- **API示例**：
```python
def get_hacker_news_top():
    # 获取热门故事ID列表
    top_stories = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()

    stories = []
    for story_id in top_stories[:10]:  # 取前10个
        story = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json").json()
        if story and 'title' in story:
            stories.append(story)
    return stories
```

#### Reddit API
**数据内容**：AI相关subreddit讨论
- **主要subreddit**：r/MachineLearning, r/artificial, r/technology, r/singularity
- **API地址**：`https://www.reddit.com/r/{subreddit}/hot.json`
- **费用**：免费（需注册应用）
- **API示例**：
```python
def get_reddit_ai_posts():
    subreddits = ['MachineLearning', 'artificial', 'technology']
    posts = []

    for subreddit in subreddits:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
        headers = {'User-Agent': 'AI-News-Bot/1.0'}
        response = requests.get(url, headers=headers)
        data = response.json()
        posts.extend(data['data']['children'])

    return posts
```

### 2. 学术/研究数据源

#### arXiv API
**数据内容**：最新AI/ML学术论文
- **API地址**：`http://export.arxiv.org/api/query`
- **费用**：完全免费
- **数据特点**：
  - 最前沿研究成果
  - 每日更新
  - 包含摘要、作者、分类
- **API示例**：
```python
import feedparser

def get_arxiv_ai_papers():
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": "cat:cs.AI OR cat:cs.LG OR cat:cs.CL",
        "start": 0,
        "max_results": 10,
        "sortBy": "submittedDate",
        "sortOrder": "descending"
    }

    query_url = url + "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    feed = feedparser.parse(query_url)
    return feed.entries
```

#### Papers With Code
**数据内容**：AI论文+代码实现
- **网站**：https://paperswithcode.com/
- **特点**：
  - 论文与代码结合
  - 性能排行榜
  - 数据集信息
- **获取方式**：网页爬取或RSS订阅

### 3. 科技媒体RSS源

#### 主要RSS源列表
```python
RSS_SOURCES = {
    'techcrunch': 'https://techcrunch.com/feed/',
    'venturebeat_ai': 'https://venturebeat.com/ai/feed/',
    'mit_tech_review': 'https://www.technologyreview.com/feed/',
    'ai_news': 'https://www.artificialintelligence-news.com/feed/',
    'wired_ai': 'https://www.wired.com/feed/tag/ai/latest/rss',
    'the_verge': 'https://www.theverge.com/rss/index.xml',
    'ars_technica': 'https://feeds.arstechnica.com/arstechnica/index'
}
```

#### RSS解析示例
```python
import feedparser
from datetime import datetime, timedelta

def get_rss_news(days_back=1):
    news_items = []
    cutoff_date = datetime.now() - timedelta(days=days_back)

    for source_name, rss_url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(rss_url)
            for entry in feed.entries:
                pub_date = datetime(*entry.published_parsed[:6])
                if pub_date > cutoff_date:
                    news_items.append({
                        'source': source_name,
                        'title': entry.title,
                        'link': entry.link,
                        'summary': entry.summary,
                        'published': pub_date
                    })
        except Exception as e:
            print(f"Error fetching {source_name}: {e}")

    return sorted(news_items, key=lambda x: x['published'], reverse=True)
```

### 4. 开发者社区数据源

#### Dev.to API
**数据内容**：开发者技术文章
- **API地址**：`https://dev.to/api/articles`
- **费用**：免费
- **API示例**：
```python
def get_devto_ai_articles():
    url = "https://dev.to/api/articles"
    params = {
        "tag": "ai,machinelearning,artificialintelligence",
        "top": "7",  # 本周热门
        "per_page": 20
    }
    response = requests.get(url, params=params)
    return response.json()
```

#### Stack Overflow API
**数据内容**：技术问答、趋势标签
- **API地址**：`https://api.stackexchange.com/2.3/`
- **费用**：免费（有配额限制）

### 5. 投资/融资数据源

#### Crunchbase API
**数据内容**：创业公司融资信息
- **API地址**：`https://api.crunchbase.com/api/v4/`
- **费用**：付费API
- **数据特点**：
  - 权威投资数据
  - 公司详细信息
  - 融资轮次追踪

#### AngelList (Wellfound) API
**数据内容**：创业公司、投资信息
- **特点**：早期项目多
- **费用**：部分免费

### 6. 社交媒体数据源

#### Twitter API v2
**数据内容**：实时AI讨论、KOL观点
- **API地址**：`https://api.twitter.com/2/`
- **费用**：基础版免费，高级功能付费
- **API示例**：
```python
import tweepy

def get_twitter_ai_trends(api_key, api_secret, access_token, access_token_secret):
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # 搜索AI相关推文
    tweets = tweepy.Cursor(api.search_tweets,
                          q="artificial intelligence OR machine learning OR #AI -RT",
                          lang="en",
                          result_type="popular").items(50)

    return [tweet for tweet in tweets]
```

## 推荐组合方案

### 方案1：全面覆盖型
**适用场景**：综合AI资讯平台
```
Product Hunt (新产品) +
GitHub Trending (开源项目) +
arXiv (学术研究) +
TechCrunch RSS (行业新闻) +
Reddit (社区讨论)
```

### 方案2：开发者导向型
**适用场景**：技术开发者社区
```
Product Hunt +
GitHub Trending +
Hacker News +
Dev.to API +
Stack Overflow
```

### 方案3：投资视角型
**适用场景**：投资机构、创业者
```
Product Hunt +
Crunchbase +
TechCrunch +
VentureBeat +
AngelList
```

### 方案4：学术研究型
**适用场景**：研究机构、学者
```
arXiv +
Papers With Code +
Reddit r/MachineLearning +
MIT Technology Review +
Google Scholar
```

## 数据整合架构

### 多源数据聚合示例
```python
class AINewsAggregator:
    def __init__(self):
        self.sources = {
            'product_hunt': self.get_product_hunt_data,
            'github_trending': self.get_github_trending,
            'arxiv_papers': self.get_arxiv_papers,
            'tech_news': self.get_rss_feeds,
            'reddit_discussions': self.get_reddit_posts
        }

    def collect_daily_news(self):
        all_news = {}
        for source_name, fetch_func in self.sources.items():
            try:
                data = fetch_func()
                all_news[source_name] = data
                print(f"✅ {source_name}: {len(data)} items")
            except Exception as e:
                print(f"❌ {source_name}: {e}")

        return self.aggregate_and_rank(all_news)

    def aggregate_and_rank(self, news_data):
        # 数据去重、排序、分类逻辑
        aggregated = []
        for source, items in news_data.items():
            for item in items:
                aggregated.append({
                    'source': source,
                    'title': item.get('title', ''),
                    'url': item.get('url', ''),
                    'score': self.calculate_score(item),
                    'category': self.categorize_content(item)
                })

        return sorted(aggregated, key=lambda x: x['score'], reverse=True)
```

### 内容分类建议
```python
CONTENT_CATEGORIES = {
    '🚀 新产品发布': ['product_hunt'],
    '💻 开源项目': ['github_trending'],
    '📚 学术研究': ['arxiv_papers', 'papers_with_code'],
    '💰 投资融资': ['crunchbase', 'angellist'],
    '🗞️ 行业新闻': ['techcrunch', 'venturebeat', 'mit_tech_review'],
    '💬 社区讨论': ['reddit', 'hacker_news', 'devto'],
    '🔥 热门话题': ['twitter', 'trending_topics']
}
```

## 实施建议

### 更新频率建议
```python
UPDATE_SCHEDULE = {
    # 每日更新
    'daily': [
        'product_hunt',      # Product Hunt每日热榜
        'github_trending',   # GitHub每日趋势
        'hacker_news',       # Hacker News热门
        'reddit_hot'         # Reddit热门讨论
    ],

    # 每周汇总
    'weekly': [
        'arxiv_papers',      # 学术论文周报
        'investment_news',   # 投资融资周报
        'tech_analysis'      # 深度技术分析
    ],

    # 实时监控
    'realtime': [
        'twitter_trends',    # Twitter热点
        'breaking_news',     # 突发新闻
        'market_alerts'      # 市场动态
    ]
}
```

### 数据质量控制
```python
class DataQualityFilter:
    def __init__(self):
        self.spam_keywords = ['spam', 'advertisement', 'promotion']
        self.min_engagement = {
            'github_stars': 10,
            'reddit_upvotes': 5,
            'twitter_likes': 10
        }

    def filter_content(self, items, source_type):
        filtered = []
        for item in items:
            if self.is_high_quality(item, source_type):
                filtered.append(item)
        return filtered

    def is_high_quality(self, item, source_type):
        # 检查垃圾内容
        title = item.get('title', '').lower()
        if any(keyword in title for keyword in self.spam_keywords):
            return False

        # 检查参与度
        if source_type in self.min_engagement:
            engagement_key = {
                'github': 'stargazers_count',
                'reddit': 'ups',
                'twitter': 'favorite_count'
            }.get(source_type.split('_')[0])

            if engagement_key and item.get(engagement_key, 0) < self.min_engagement[source_type]:
                return False

        return True
```

## 注意事项

### 1. API限制和成本
```python
API_LIMITS = {
    'github': {
        'rate_limit': '5000/hour',
        'cost': 'Free',
        'auth_required': True
    },
    'twitter': {
        'rate_limit': '300/15min',
        'cost': 'Free tier available',
        'auth_required': True
    },
    'crunchbase': {
        'rate_limit': '200/day',
        'cost': '$29+/month',
        'auth_required': True
    },
    'reddit': {
        'rate_limit': '60/minute',
        'cost': 'Free',
        'auth_required': False
    }
}
```

### 2. 法律合规检查清单
- [ ] **API使用条款**：仔细阅读每个平台的使用条款
- [ ] **数据使用权限**：确认商业使用是否被允许
- [ ] **版权声明**：正确标注内容来源
- [ ] **用户隐私**：避免收集个人敏感信息
- [ ] **频率限制**：遵守API调用频率限制
- [ ] **内容过滤**：过滤不当或敏感内容

### 3. 技术实现建议
```python
# 错误处理和重试机制
import time
import random
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    wait_time = delay * (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait_time)
            return None
        return wrapper
    return decorator

# 缓存机制
import pickle
import os
from datetime import datetime, timedelta

class DataCache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, key, max_age_hours=1):
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        if os.path.exists(cache_file):
            mod_time = datetime.fromtimestamp(os.path.getmtime(cache_file))
            if datetime.now() - mod_time < timedelta(hours=max_age_hours):
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        return None

    def set(self, key, data):
        cache_file = os.path.join(self.cache_dir, f"{key}.pkl")
        with open(cache_file, 'wb') as f:
            pickle.dump(data, f)
```

## 扩展数据源

### 新兴平台
- **Discord服务器**：AI社区讨论
- **Telegram频道**：实时AI资讯
- **YouTube API**：AI教程和演讲
- **Podcast RSS**：AI播客内容
- **Newsletter APIs**：专业AI简报

### 垂直领域数据源
```python
VERTICAL_SOURCES = {
    'computer_vision': [
        'https://www.pyimagesearch.com/feed/',
        'https://distill.pub/rss.xml'
    ],
    'nlp': [
        'https://ruder.io/rss/',
        'https://thegradient.pub/rss/'
    ],
    'robotics': [
        'https://spectrum.ieee.org/robotics/feed',
        'https://www.therobotreport.com/feed/'
    ],
    'autonomous_vehicles': [
        'https://www.thedrive.com/tech/rss',
        'https://electrek.co/guides/autonomous/feed/'
    ]
}
```

## 监控和分析

### 数据源质量监控
```python
class SourceMonitor:
    def __init__(self):
        self.metrics = {}

    def track_source_performance(self, source_name, data):
        if source_name not in self.metrics:
            self.metrics[source_name] = {
                'total_items': 0,
                'quality_score': 0,
                'last_update': None,
                'error_count': 0
            }

        self.metrics[source_name]['total_items'] += len(data)
        self.metrics[source_name]['last_update'] = datetime.now()

    def get_source_health(self):
        health_report = {}
        for source, metrics in self.metrics.items():
            last_update = metrics['last_update']
            hours_since_update = (datetime.now() - last_update).total_seconds() / 3600

            health_report[source] = {
                'status': 'healthy' if hours_since_update < 24 else 'stale',
                'items_per_day': metrics['total_items'],
                'error_rate': metrics['error_count'] / max(1, metrics['total_items'])
            }

        return health_report
```

## 总结

本文档提供了丰富的AI资讯数据源选择，从免费的开源API到付费的专业服务，覆盖了学术研究、产品发布、投资融资、技术讨论等多个维度。

### 快速开始建议
1. **第一阶段**：集成GitHub Trending + Hacker News + RSS源（免费且稳定）
2. **第二阶段**：添加Reddit + arXiv（提升内容深度）
3. **第三阶段**：考虑付费API如Crunchbase（获取独家数据）

### 成功关键因素
- **数据质量**：实施严格的内容过滤机制
- **更新频率**：保持内容的时效性
- **用户体验**：提供清晰的分类和搜索功能
- **合规运营**：遵守所有平台的使用条款

通过合理组合这些数据源，可以构建一个全面、及时、高质量的AI资讯聚合平台。
```
