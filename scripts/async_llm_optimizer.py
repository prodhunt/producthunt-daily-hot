#!/usr/bin/env python3
"""
异步LLM调用优化器
通过并发和批量处理大幅提升性能
"""

import asyncio
import aiohttp
import time
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import json

class AsyncLLMOptimizer:
    """异步LLM调用优化器"""
    
    def __init__(self, llm_provider, max_concurrent=10, batch_size=5):
        self.llm = llm_provider
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def safe_llm_call(self, method, *args, **kwargs):
        """带信号量控制的安全LLM调用"""
        async with self.semaphore:
            # 将同步LLM调用转为异步
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                try:
                    result = await loop.run_in_executor(
                        executor, 
                        lambda: method(*args, **kwargs)
                    )
                    return result
                except Exception as e:
                    print(f"LLM调用失败: {e}")
                    return None
    
    async def generate_keywords_async(self, product):
        """异步生成关键词"""
        result = await self.safe_llm_call(
            self.llm.generate_keywords,
            product.name,
            product.tagline,
            product.description
        )
        return {'product_id': id(product), 'type': 'keywords', 'result': result}
    
    async def translate_text_async(self, text, text_type, product_id):
        """异步翻译文本"""
        result = await self.safe_llm_call(self.llm.translate_text, text)
        return {'product_id': product_id, 'type': text_type, 'result': result}
    
    async def batch_translate_async(self, texts_with_info):
        """批量翻译优化"""
        if len(texts_with_info) <= 1:
            # 单个文本直接调用
            if texts_with_info:
                text_info = texts_with_info[0]
                result = await self.translate_text_async(
                    text_info['text'], 
                    text_info['type'], 
                    text_info['product_id']
                )
                return [result]
            return []
        
        # 构建批量翻译提示
        batch_prompt = "请分别翻译以下内容，用'---SPLIT---'分隔每个翻译结果：\n\n"
        for i, text_info in enumerate(texts_with_info):
            batch_prompt += f"{i+1}. {text_info['text']}\n\n"
        
        # 批量调用
        batch_result = await self.safe_llm_call(self.llm.translate_text, batch_prompt)
        
        if not batch_result:
            return []
        
        # 解析批量结果
        try:
            translations = batch_result.split('---SPLIT---')
            results = []
            for i, text_info in enumerate(texts_with_info):
                translation = translations[i].strip() if i < len(translations) else text_info['text']
                results.append({
                    'product_id': text_info['product_id'],
                    'type': text_info['type'],
                    'result': translation
                })
            return results
        except Exception as e:
            print(f"批量翻译解析失败: {e}")
            # 降级为单个翻译
            tasks = [
                self.translate_text_async(info['text'], info['type'], info['product_id'])
                for info in texts_with_info
            ]
            return await asyncio.gather(*tasks, return_exceptions=True)
    
    async def process_products_optimized(self, products):
        """优化的产品处理流程"""
        start_time = time.time()
        print(f"🚀 开始异步处理 {len(products)} 个产品...")
        
        # 第一阶段：并发生成关键词
        print("📝 第一阶段：并发生成关键词...")
        keyword_tasks = [self.generate_keywords_async(product) for product in products]
        keyword_results = await asyncio.gather(*keyword_tasks, return_exceptions=True)
        
        # 第二阶段：批量翻译
        print("🌐 第二阶段：批量翻译...")
        translation_tasks = []
        
        # 收集所有需要翻译的文本
        for product in products:
            product_id = id(product)
            translation_tasks.extend([
                {'text': product.tagline, 'type': 'tagline', 'product_id': product_id},
                {'text': product.description, 'type': 'description', 'product_id': product_id}
            ])
        
        # 分批处理翻译任务
        translation_results = []
        for i in range(0, len(translation_tasks), self.batch_size):
            batch = translation_tasks[i:i + self.batch_size]
            batch_results = await self.batch_translate_async(batch)
            translation_results.extend(batch_results)
        
        # 第三阶段：生成Hugo标签
        print("🏷️ 第三阶段：生成Hugo标签...")
        products_info = self._prepare_products_info(products)
        hugo_tags_result = await self.safe_llm_call(
            self.llm.generate_hugo_tags_and_keywords,
            products_info
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"✅ 异步处理完成！总耗时: {total_time:.1f}秒")
        print(f"📊 性能提升: 预计节省 {90 - total_time:.1f}秒")
        
        return {
            'keyword_results': keyword_results,
            'translation_results': translation_results,
            'hugo_tags_result': hugo_tags_result,
            'processing_time': total_time
        }
    
    def _prepare_products_info(self, products):
        """准备产品信息用于Hugo标签生成"""
        products_info = ""
        for i, product in enumerate(products[:5], 1):
            products_info += f"{i}. {product.name}\n"
            products_info += f"   - 标语: {product.tagline}\n"
            products_info += f"   - 描述: {product.description[:100]}...\n"
            products_info += f"   - 票数: {product.votes_count}\n\n"
        return products_info
    
    def apply_results_to_products(self, products, results):
        """将异步处理结果应用到产品对象"""
        # 创建结果映射
        keyword_map = {}
        translation_map = {}
        
        # 处理关键词结果
        for result in results['keyword_results']:
            if result and not isinstance(result, Exception):
                keyword_map[result['product_id']] = result['result']
        
        # 处理翻译结果
        for result in results['translation_results']:
            if result and not isinstance(result, Exception):
                product_id = result['product_id']
                if product_id not in translation_map:
                    translation_map[product_id] = {}
                translation_map[product_id][result['type']] = result['result']
        
        # 应用结果到产品
        for product in products:
            product_id = id(product)
            
            # 应用关键词
            if product_id in keyword_map:
                product.keywords = keyword_map[product_id]
            
            # 应用翻译
            if product_id in translation_map:
                translations = translation_map[product_id]
                if 'tagline' in translations:
                    product.tagline_cn = translations['tagline']
                if 'description' in translations:
                    product.description_cn = translations['description']
        
        return results['hugo_tags_result']

async def demo_async_optimization():
    """演示异步优化效果"""
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    from scripts.llm_provider import get_llm_provider
    from scripts.scripts_product_hunt_list_to_md import fetch_mock_data
    
    # 获取LLM提供商和模拟数据
    llm = get_llm_provider()
    products = fetch_mock_data()
    
    # 创建优化器
    optimizer = AsyncLLMOptimizer(llm, max_concurrent=5, batch_size=3)
    
    # 异步处理
    results = await optimizer.process_products_optimized(products)
    
    # 应用结果
    hugo_tags = optimizer.apply_results_to_products(products, results)
    
    print(f"\n📋 处理结果:")
    print(f"关键词结果: {len([r for r in results['keyword_results'] if r])}")
    print(f"翻译结果: {len([r for r in results['translation_results'] if r])}")
    print(f"Hugo标签: {hugo_tags}")

if __name__ == "__main__":
    asyncio.run(demo_async_optimization())
