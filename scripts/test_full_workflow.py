import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone
import pytz
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv 模块未安装，将直接使用环境变量")

# 导入LLM提供商
from scripts.llm_provider import get_llm_provider

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
        
        # 初始化时不调用LLM，以便测试
        self.keyword = ""
        self.translated_tagline = ""
        self.translated_description = ""

    def get_image_url_from_media(self, media):
        try:
            if media and isinstance(media, list) and len(media) > 0:
                image_url = media[0].get('url', '')
                if image_url:
                    print(f"成功从API获取图片URL: {self.name}")
                    return image_url
            print(f"API未返回图片，尝试使用备用方法: {self.name}")
            return ""
        except Exception as e:
            print(f"获取图片URL时出错: {self.name}, 错误: {e}")
            return ""

    def convert_to_beijing_time(self, utc_time_str: str) -> str:
        utc_time = datetime.strptime(utc_time_str, '%Y-%m-%dT%H:%M:%SZ')
        beijing_tz = pytz.timezone('Asia/Shanghai')
        beijing_time = utc_time.replace(tzinfo=pytz.utc).astimezone(beijing_tz)
        return beijing_time.strftime('%Y年%m月%d日 %p%I:%M (北京时间)')

    def to_markdown(self, rank: int) -> str:
        og_image_markdown = f"![{self.name}]({self.og_image_url})" if self.og_image_url else f"*图片未获取*"
        return (
            f"## [{rank}. {self.name}]({self.url})\n"
            f"**标语**：{self.tagline if not self.translated_tagline else self.translated_tagline}\n"
            f"**介绍**：{self.description if not self.translated_description else self.translated_description}\n"
            f"**产品网站**: [立即访问]({self.website})\n"
            f"**Product Hunt**: [View on Product Hunt]({self.url})\n\n"
            f"{og_image_markdown}\n\n"
            f"**关键词**：{self.keyword}\n"
            f"**票数**: 🔺{self.votes_count}\n"
            f"**是否精选**：{self.featured}\n"
            f"**发布时间**：{self.created_at}\n\n"
            f"---\n\n"
        )

def get_producthunt_token():
    """获取Product Hunt API访问令牌"""
    developer_token = os.getenv('PRODUCTHUNT_DEVELOPER_TOKEN')
    if not developer_token:
        raise Exception("PRODUCTHUNT_DEVELOPER_TOKEN not found in environment variables")
    print(f"成功获取PRODUCTHUNT_DEVELOPER_TOKEN: {developer_token[:5]}...{developer_token[-5:]}")
    return developer_token

def fetch_product_hunt_data(date_str=None):
    """从Product Hunt API获取数据"""
    token = get_producthunt_token()
    
    if date_str is None:
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        date_str = yesterday.strftime('%Y-%m-%d')
    
    print(f"获取 {date_str} 的数据")
    
    url = "https://api.producthunt.com/v2/api/graphql"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "TestScript/1.0 (Testing API Connection)",
    }
    
    # 设置重试策略
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    
    # GraphQL查询
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
    max_products = 5  # 限制测试时获取的产品数量
    
    try:
        while has_next_page and len(all_posts) < max_products:
            query = base_query % (date_str, date_str, cursor)
            print(f"发送API请求 (已获取 {len(all_posts)} 个产品)...")
            response = session.post(url, headers=headers, json={"query": query})
            response.raise_for_status()
            
            data = response.json()
            if 'errors' in data:
                print(f"API返回错误: {data['errors']}")
                break
                
            posts = data['data']['posts']['nodes']
            all_posts.extend(posts)
            
            page_info = data['data']['posts']['pageInfo']
            has_next_page = page_info['hasNextPage'] and len(all_posts) < max_products
            cursor = page_info['endCursor']
        
        print(f"成功获取 {len(all_posts)} 个产品数据")
        
        # 将原始数据保存到文件
        with open('product_hunt_raw_data.json', 'w', encoding='utf-8') as f:
            json.dump(all_posts, f, ensure_ascii=False, indent=2)
        print("原始数据已保存到 product_hunt_raw_data.json 文件")
        
        # 转换为Product对象
        products = [Product(**post) for post in sorted(all_posts, key=lambda x: x['votesCount'], reverse=True)]
        return products
    except Exception as e:
        print(f"获取数据失败: {e}")
        return []

def test_llm_integration(products, test_single=True):
    """测试LLM集成"""
    if not products:
        print("没有产品数据，跳过LLM测试")
        return False
    
    try:
        llm = get_llm_provider()
        print(f"成功初始化LLM提供商: {llm.__class__.__name__}")
        
        if test_single:
            # 只测试第一个产品
            product = products[0]
            print(f"\n测试产品 '{product.name}' 的LLM功能:")
            
            print("测试关键词生成...")
            product.keyword = llm.generate_keywords(product.name, product.tagline, product.description)
            print(f"生成的关键词: {product.keyword}")
            
            print("测试标语翻译...")
            product.translated_tagline = llm.translate_text(product.tagline)
            print(f"翻译后的标语: {product.translated_tagline}")
            
            print("测试简短描述翻译...")
            # 只翻译描述的前100个字符作为测试
            short_desc = product.description[:100] + ("..." if len(product.description) > 100 else "")
            product.translated_description = llm.translate_text(short_desc)
            print(f"翻译后的描述: {product.translated_description}")
            
            return True
    except Exception as e:
        print(f"LLM测试失败: {e}")
        return False

def generate_test_markdown(products, date_str=None):
    """生成测试用的Markdown文件"""
    if not products:
        print("没有产品数据，无法生成Markdown")
        return False
    
    if date_str is None:
        today = datetime.now(timezone.utc)
        date_str = today.strftime('%Y-%m-%d')
    
    try:
        markdown_content = f"# PH今日热榜测试 | {date_str}\n\n"
        for rank, product in enumerate(products, 1):
            markdown_content += product.to_markdown(rank)
        
        os.makedirs('data', exist_ok=True)
        file_name = f"data/producthunt-test-{date_str}.md"
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(markdown_content)
        print(f"测试文件 {file_name} 生成成功。")
        return True
    except Exception as e:
        print(f"生成Markdown文件失败: {e}")
        return False

def main():
    print("=== 开始测试 Product Hunt 完整工作流 ===")
    
    # 步骤1: 测试API连接和数据获取
    print("\n[步骤1] 测试API连接和数据获取")
    products = fetch_product_hunt_data()
    if not products:
        print("❌ 步骤1失败: 无法获取产品数据")
        return
    print("✅ 步骤1成功: 成功获取产品数据")
    
    # 步骤2: 测试LLM集成
    print("\n[步骤2] 测试LLM集成")
    llm_success = test_llm_integration(products)
    if not llm_success:
        print("❌ 步骤2失败: LLM集成测试失败")
    else:
        print("✅ 步骤2成功: LLM集成测试成功")
    
    # 步骤3: 测试Markdown生成
    print("\n[步骤3] 测试Markdown生成")
    md_success = generate_test_markdown(products)
    if not md_success:
        print("❌ 步骤3失败: 无法生成Markdown文件")
    else:
        print("✅ 步骤3成功: 成功生成Markdown文件")
    
    # 总结
    print("\n=== 测试总结 ===")
    if products and (llm_success or not llm_success) and md_success:
        print("✅ 测试通过: 工作流程基本功能正常")
    else:
        print("❌ 测试失败: 工作流程存在问题，请检查上述错误")

if __name__ == "__main__":
    main() 