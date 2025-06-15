#!/usr/bin/env python3
"""
Product Hunt图片选择器
从Product Hunt产品数据中智能选择最佳封面图片
"""

import re
from urllib.parse import urlparse, parse_qs
from typing import List, Dict, Optional, Tuple

class ProductHuntImageSelector:
    """Product Hunt图片选择器"""
    
    # 图片格式优先级（数字越小优先级越高）
    FORMAT_PRIORITY = {
        'png': 1,
        'jpg': 2,
        'jpeg': 2,
        'webp': 3,
        'gif': 4
    }
    
    def __init__(self):
        pass
    
    def get_image_format(self, url: str) -> str:
        """从URL中提取图片格式"""
        # 从URL路径中提取格式
        path = urlparse(url).path
        if '.' in path:
            return path.split('.')[-1].lower()
        return 'unknown'
    
    def score_image(self, media_item: Dict, is_top_product: bool = False) -> int:
        """为图片打分，分数越高越优先"""
        score = 0
        
        # 基础分数
        if media_item.get('type') == 'image':
            score += 100
        elif media_item.get('type') == 'video':
            score += 50  # 视频缩略图次优
        
        # 格式分数
        image_format = self.get_image_format(media_item.get('url', ''))
        format_score = 10 - self.FORMAT_PRIORITY.get(image_format, 5)
        score += format_score
        
        # 如果是票数最高的产品，额外加分
        if is_top_product:
            score += 50
        
        return score
    
    def select_best_cover_image(self, products: List[Dict]) -> Tuple[str, str]:
        """
        选择最佳封面图片
        
        Args:
            products: Product Hunt产品列表
            
        Returns:
            Tuple[str, str]: (图片URL, Alt文本)
        """
        if not products:
            return "", ""
        
        # 按票数排序，找到最热门的产品
        sorted_products = sorted(products, key=lambda x: x.get('votesCount', 0), reverse=True)
        top_product = sorted_products[0]
        
        best_image = None
        best_score = -1
        
        # 遍历所有产品的图片，但优先考虑热门产品
        for i, product in enumerate(sorted_products[:3]):  # 只考虑前3个产品
            is_top = (i == 0)
            media_list = product.get('media', [])
            
            for media_item in media_list:
                if not media_item.get('url'):
                    continue
                
                score = self.score_image(media_item, is_top)
                
                if score > best_score:
                    best_score = score
                    best_image = {
                        'url': media_item['url'],
                        'product': product,
                        'media_item': media_item
                    }
        
        if not best_image:
            return "", ""
        
        # 优化图片URL
        optimized_url = self.optimize_image_url(best_image['url'])
        
        # 生成Alt文本
        alt_text = self.generate_alt_text(best_image['product'], len(products))
        
        return optimized_url, alt_text
    
    def optimize_image_url(self, url: str) -> str:
        """优化图片URL，添加适合社交媒体的参数"""
        if 'imgix.net' in url:
            # 如果已经有参数，先移除
            base_url = url.split('?')[0]
            # 添加优化参数
            return f"{base_url}?auto=format&w=1200&h=630&fit=crop&q=80"
        return url
    
    def generate_alt_text(self, product: Dict, total_products: int) -> str:
        """生成Alt文本"""
        name = product.get('name', '未知产品')
        votes = product.get('votesCount', 0)
        tagline = product.get('tagline', '')
        
        # 简化tagline，只取前30个字符
        if tagline and len(tagline) > 30:
            tagline = tagline[:30] + "..."
        
        if tagline:
            return f"Product Hunt今日热榜：{name} - {tagline} ({votes}票)"
        else:
            return f"Product Hunt今日热榜：{name} ({votes}票)"
    
    def get_product_images_summary(self, products: List[Dict]) -> Dict:
        """获取产品图片统计信息"""
        total_images = 0
        total_videos = 0
        formats = {}
        
        for product in products:
            media_list = product.get('media', [])
            for media_item in media_list:
                if media_item.get('type') == 'image':
                    total_images += 1
                    img_format = self.get_image_format(media_item.get('url', ''))
                    formats[img_format] = formats.get(img_format, 0) + 1
                elif media_item.get('type') == 'video':
                    total_videos += 1
        
        return {
            'total_images': total_images,
            'total_videos': total_videos,
            'formats': formats,
            'total_products': len(products)
        }

def demo_image_selection():
    """演示图片选择功能"""
    import json
    
    # 读取Product Hunt响应数据
    try:
        with open('product_hunt_response.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        products = data['data']['posts']['nodes']
        
        selector = ProductHuntImageSelector()
        
        print("🖼️ Product Hunt图片选择演示")
        print("=" * 50)
        
        # 获取统计信息
        summary = selector.get_product_images_summary(products)
        print(f"📊 图片统计:")
        print(f"   产品数量: {summary['total_products']}")
        print(f"   图片总数: {summary['total_images']}")
        print(f"   视频总数: {summary['total_videos']}")
        print(f"   图片格式: {summary['formats']}")
        
        # 选择最佳封面图片
        cover_url, alt_text = selector.select_best_cover_image(products)
        
        print(f"\n🎯 选择的封面图片:")
        print(f"   URL: {cover_url}")
        print(f"   Alt: {alt_text}")
        
        # 生成Hugo Front Matter示例
        print(f"\n📝 Hugo Front Matter示例:")
        print("cover:")
        print(f'  image: "{cover_url}"')
        print(f'  alt: "{alt_text}"')
        
        # 显示前3个产品的图片信息
        print(f"\n📋 前3个产品的图片详情:")
        for i, product in enumerate(products[:3], 1):
            print(f"\n{i}. {product['name']} ({product['votesCount']}票)")
            media_list = product.get('media', [])
            for j, media in enumerate(media_list[:2], 1):  # 只显示前2张图片
                img_format = selector.get_image_format(media.get('url', ''))
                print(f"   图片{j}: {media['type']} ({img_format}) - {media['url'][:60]}...")
        
    except FileNotFoundError:
        print("❌ 未找到 product_hunt_response.json 文件")
        print("请先运行 python scripts/test_producthunt_api.py 生成数据")
    except Exception as e:
        print(f"❌ 演示失败: {e}")

if __name__ == "__main__":
    demo_image_selection()
