import os
import sys
import json
import requests
from datetime import datetime, timedelta, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv 模块未安装，将直接使用环境变量")

def get_producthunt_token():
    """获取Product Hunt API访问令牌"""
    developer_token = os.getenv('PRODUCTHUNT_DEVELOPER_TOKEN')
    if not developer_token:
        raise Exception("PRODUCTHUNT_DEVELOPER_TOKEN not found in environment variables")
    print(f"成功获取PRODUCTHUNT_DEVELOPER_TOKEN: {developer_token[:5]}...{developer_token[-5:]}")
    return developer_token

def test_fetch_product_hunt_data():
    """测试从Product Hunt API获取数据"""
    token = get_producthunt_token()
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
    query = """
    {
      posts(order: VOTES, postedAfter: "%sT00:00:00Z", postedBefore: "%sT23:59:59Z") {
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
    """ % (date_str, date_str)
    
    try:
        print("发送API请求...")
        response = session.post(url, headers=headers, json={"query": query})
        response.raise_for_status()
        
        data = response.json()
        if 'errors' in data:
            print(f"API返回错误: {data['errors']}")
            return False
            
        posts = data['data']['posts']['nodes']
        print(f"成功获取 {len(posts)} 个产品数据")
        
        # 打印前3个产品的基本信息
        for i, post in enumerate(posts[:3], 1):
            print(f"\n产品 {i}:")
            print(f"  名称: {post['name']}")
            print(f"  标语: {post['tagline']}")
            print(f"  票数: {post['votesCount']}")
            print(f"  URL: {post['url']}")
        
        # 将完整响应保存到文件中
        with open('product_hunt_response.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("\n完整响应已保存到 product_hunt_response.json 文件")
        
        return True
    except Exception as e:
        print(f"测试失败: {e}")
        return False

def main():
    print("=== 开始测试 Product Hunt API ===")
    success = test_fetch_product_hunt_data()
    if success:
        print("\n✅ 测试成功: 成功从Product Hunt API获取数据")
    else:
        print("\n❌ 测试失败: 无法从Product Hunt API获取数据")

if __name__ == "__main__":
    main() 