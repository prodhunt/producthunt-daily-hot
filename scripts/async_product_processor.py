#!/usr/bin/env python3
"""
异步产品处理器 - 专门优化Product Hunt产品的LLM处理
"""

import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

class AsyncProductProcessor:
    """异步产品处理器"""
    
    def __init__(self, llm_provider, max_concurrent=5):
        self.llm = llm_provider
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.executor = ThreadPoolExecutor(max_workers=max_concurrent)
    
    async def safe_llm_call(self, method, *args, **kwargs):
        """带信号量控制的安全LLM调用"""
        async with self.semaphore:
            loop = asyncio.get_event_loop()
            try:
                result = await loop.run_in_executor(
                    self.executor, 
                    lambda: method(*args, **kwargs)
                )
                return result
            except Exception as e:
                print(f"LLM调用失败: {e}")
                return None
    
    async def process_single_product(self, product_data, product_index):
        """异步处理单个产品"""
        name = product_data.get('name', f'Product_{product_index}')
        tagline = product_data.get('tagline', '')
        description = product_data.get('description', '')
        
        print(f"🔄 开始处理产品 {product_index}: {name}")
        
        # 并发执行三个LLM任务
        tasks = [
            self.safe_llm_call(
                self.llm.generate_keywords, 
                name, tagline, description
            ),
            self.safe_llm_call(self.llm.translate_text, tagline),
            self.safe_llm_call(self.llm.translate_text, description)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        keywords = results[0] if results[0] and not isinstance(results[0], Exception) else f"{name},产品推荐,创新工具"
        translated_tagline = results[1] if results[1] and not isinstance(results[1], Exception) else tagline
        translated_description = results[2] if results[2] and not isinstance(results[2], Exception) else description
        
        print(f"✅ 完成处理产品 {product_index}: {name}")
        
        return {
            'index': product_index,
            'keywords': keywords,
            'translated_tagline': translated_tagline,
            'translated_description': translated_description
        }
    
    async def process_all_products(self, products_data):
        """异步处理所有产品"""
        start_time = time.time()
        print(f"🚀 开始异步处理 {len(products_data)} 个产品...")
        
        # 创建所有产品的处理任务
        tasks = [
            self.process_single_product(product_data, i)
            for i, product_data in enumerate(products_data)
        ]
        
        # 并发执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 过滤异常结果
        valid_results = [r for r in results if r and not isinstance(r, Exception)]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ 异步处理完成！")
        print(f"⏱️ 总耗时: {total_time:.1f}秒")
        print(f"📊 成功处理: {len(valid_results)}/{len(products_data)} 个产品")
        
        # 估算性能提升
        estimated_sync_time = len(products_data) * 9  # 每个产品约9秒
        time_saved = estimated_sync_time - total_time
        print(f"🚀 预计节省时间: {time_saved:.1f}秒")
        
        return valid_results
    
    async def generate_hugo_tags(self, products_data):
        """生成Hugo标签和关键词"""
        print("🏷️ 生成Hugo标签和关键词...")
        
        # 准备产品信息
        products_info = ""
        for i, product in enumerate(products_data[:5], 1):
            products_info += f"{i}. {product.get('name', '')}\n"
            products_info += f"   - 标语: {product.get('tagline', '')}\n"
            products_info += f"   - 描述: {product.get('description', '')[:100]}...\n"
            products_info += f"   - 票数: {product.get('votesCount', 0)}\n\n"
        
        # 异步调用
        result = await self.safe_llm_call(
            self.llm.generate_hugo_tags_and_keywords,
            products_info
        )
        
        return result

def create_optimized_products(products_data, async_results):
    """使用异步结果创建优化的产品对象"""
    from scripts.scripts_product_hunt_list_to_md import Product
    
    # 创建结果映射
    results_map = {r['index']: r for r in async_results}
    
    optimized_products = []
    
    for i, product_data in enumerate(products_data):
        # 创建产品对象，但跳过LLM调用
        product = OptimizedProduct(**product_data)
        
        # 应用异步处理结果
        if i in results_map:
            result = results_map[i]
            product.keyword = result['keywords']
            product.translated_tagline = result['translated_tagline']
            product.translated_description = result['translated_description']
        
        optimized_products.append(product)
    
    return optimized_products

class OptimizedProduct:
    """优化的产品类，跳过初始化时的LLM调用"""
    
    def __init__(self, id: str, name: str, tagline: str, description: str, votesCount: int, createdAt: str, featuredAt: str, website: str, url: str, media=None, **kwargs):
        from scripts.scripts_product_hunt_list_to_md import Product
        
        self.name = name
        self.tagline = tagline
        self.description = description
        self.votes_count = votesCount
        self.featured = "是" if featuredAt else "否"
        self.website = website
        self.url = url
        
        # 创建临时Product实例来复用现有方法
        temp_product = Product.__new__(Product)
        temp_product.name = name
        temp_product.url = url
        
        # 复用时间转换和图片获取方法
        self.created_at = temp_product.convert_to_beijing_time(createdAt)
        self.og_image_url = temp_product.get_image_url_from_media(media)
        
        # 这些将由异步处理结果填充
        self.keyword = ""
        self.translated_tagline = tagline
        self.translated_description = description
    
    def to_markdown(self, rank: int) -> str:
        """生成Markdown内容"""
        og_image_markdown = f"![{self.name}]({self.og_image_url})"
        return (
            f"## [{rank}. {self.name}]({self.url})\n"
            f"**标语**：{self.translated_tagline}\n"
            f"**介绍**：{self.translated_description}\n"
            f"**产品网站**: [立即访问]({self.website})\n"
            f"**Product Hunt**: [View on Product Hunt]({self.url})\n\n"
            f"{og_image_markdown}\n\n"
            f"**关键词**：{self.keyword}\n"
            f"**票数**: 🔺{self.votes_count}\n"
            f"**是否精选**：{self.featured}\n"
            f"**发布时间**：{self.created_at}\n\n"
            f"---\n\n"
        )

async def demo_async_processing():
    """演示异步处理效果"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from scripts.llm_provider import get_llm_provider
    from scripts.scripts_product_hunt_list_to_md import fetch_mock_data
    
    # 获取LLM提供商和测试数据
    llm = get_llm_provider()
    products = fetch_mock_data()
    
    # 转换为原始数据格式
    products_data = []
    for product in products:
        products_data.append({
            'id': '1',
            'name': product.name,
            'tagline': product.tagline,
            'description': product.description,
            'votesCount': product.votes_count,
            'createdAt': '2025-06-14T16:01:00Z',
            'featuredAt': '2025-06-14T16:01:00Z',
            'website': product.website,
            'url': product.url,
            'media': [{'url': product.og_image_url, 'type': 'image'}] if product.og_image_url else []
        })
    
    # 创建异步处理器
    processor = AsyncProductProcessor(llm, max_concurrent=3)
    
    # 异步处理
    async_results = await processor.process_all_products(products_data)
    hugo_tags = await processor.generate_hugo_tags(products_data)
    
    # 创建优化的产品对象
    optimized_products = create_optimized_products(products_data, async_results)
    
    print(f"\n📋 处理结果:")
    print(f"成功处理产品: {len(optimized_products)}")
    print(f"Hugo标签: {hugo_tags}")
    
    return optimized_products, hugo_tags

if __name__ == "__main__":
    asyncio.run(demo_async_processing())
