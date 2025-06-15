#!/usr/bin/env python3
"""
异步优化版本的Product Hunt内容生成器
大幅提升LLM调用性能
"""

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

from datetime import datetime, timedelta, timezone
from scripts.llm_provider import get_llm_provider
from scripts.image_selector import ProductHuntImageSelector
from scripts.async_product_processor import AsyncProductProcessor, create_optimized_products
from scripts.scripts_product_hunt_list_to_md import fetch_product_hunt_data, fetch_mock_data

async def async_generate_hugo_front_matter(products_data, date_str, llm_provider):
    """异步生成Hugo Front Matter"""
    try:
        # 创建异步处理器
        processor = AsyncProductProcessor(llm_provider, max_concurrent=5)
        
        # 异步生成Hugo标签
        print("🔄 正在异步生成Hugo标签和关键词...")
        tags_result = await processor.generate_hugo_tags(products_data)
        
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
        cover_url, alt_text = image_selector.select_best_cover_image(products_data)
        
        # 计算总票数
        total_votes = sum(p.get('votesCount', 0) for p in products_data)
        
        # 生成标题和描述
        if products_data:
            top_product = products_data[0]
            title = f"Product Hunt 今日热榜 {date_str} | {top_product['name']}等{len(products_data)}款创新产品"
            second_name = products_data[1]['name'] if len(products_data) > 1 else ''
            description = f"今日Product Hunt热榜精选：{top_product['name']}、{second_name}等{len(products_data)}款创新产品，总票数{total_votes}票"
        else:
            title = f"Product Hunt 今日热榜 {date_str}"
            description = f"今日Product Hunt热榜精选创新产品推荐"
        
        # 构建Front Matter
        front_matter = "---\n"
        front_matter += f'title: "{title}"\n'
        front_matter += f'date: {date_str}\n'
        front_matter += f'description: "{description}"\n'
        front_matter += f'tags: {json.dumps(tags, ensure_ascii=False)}\n'
        front_matter += f'keywords: {json.dumps(keywords, ensure_ascii=False)}\n'
        front_matter += f'votes: {total_votes}\n'
        if cover_url:
            front_matter += 'cover:\n'
            front_matter += f'  image: "{cover_url}"\n'
            front_matter += f'  alt: "{alt_text}"\n'
        front_matter += "---\n\n"
        
        print("✅ Hugo Front Matter生成成功")
        return front_matter
        
    except Exception as e:
        print(f"⚠️ Hugo Front Matter生成失败: {e}")
        # 返回基础的Front Matter
        total_votes = sum(p.get('votesCount', 0) for p in products_data)
        return f"""---
title: "Product Hunt 今日热榜 {date_str}"
date: {date_str}
description: "今日Product Hunt热榜精选创新产品推荐"
tags: ["Product Hunt", "每日热榜", "创新产品"]
keywords: ["Product Hunt", "PH热榜", "今日新品", "创新产品推荐", "科技产品"]
votes: {total_votes}
---

"""

async def async_generate_markdown(products_data, date_str):
    """异步生成Markdown内容"""
    start_time = time.time()
    
    # 获取LLM提供商
    llm = get_llm_provider()
    
    # 创建异步处理器
    processor = AsyncProductProcessor(llm, max_concurrent=5)
    
    print(f"🚀 开始异步处理 {len(products_data)} 个产品...")
    
    # 并发执行产品处理和Hugo Front Matter生成
    products_task = processor.process_all_products(products_data)
    front_matter_task = async_generate_hugo_front_matter(products_data, date_str, llm)
    
    # 等待两个任务完成
    async_results, front_matter = await asyncio.gather(products_task, front_matter_task)
    
    # 创建优化的产品对象
    optimized_products = create_optimized_products(products_data, async_results)
    
    # 生成Markdown内容
    markdown_content = front_matter
    markdown_content += f"# PH今日热榜 | {date_str}\n\n"
    
    for rank, product in enumerate(optimized_products, 1):
        markdown_content += product.to_markdown(rank)
    
    # 保存文件
    os.makedirs('data', exist_ok=True)
    file_name = f"data/producthunt-daily-{date_str}.md"
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(markdown_content)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"✅ 文件 {file_name} 生成成功！")
    print(f"⏱️ 总耗时: {total_time:.1f}秒")
    
    # 估算性能提升
    estimated_sync_time = len(products_data) * 9 + 10  # 每个产品9秒 + Hugo生成10秒
    time_saved = estimated_sync_time - total_time
    print(f"🚀 相比同步版本节省: {time_saved:.1f}秒")

def convert_products_to_data(products):
    """将Product对象转换为数据字典"""
    products_data = []
    for product in products:
        product_data = {
            'id': getattr(product, 'id', '1'),
            'name': product.name,
            'tagline': product.tagline,
            'description': product.description,
            'votesCount': product.votes_count,
            'createdAt': '2025-06-14T16:01:00Z',  # 使用固定时间
            'featuredAt': '2025-06-14T16:01:00Z' if product.featured == "是" else None,
            'website': product.website,
            'url': product.url,
            'media': [{'url': product.og_image_url, 'type': 'image'}] if product.og_image_url else []
        }
        products_data.append(product_data)
    return products_data

async def main():
    """主函数"""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    date_str = yesterday.strftime('%Y-%m-%d')
    
    print("🔄 获取Product Hunt数据...")
    
    try:
        # 获取真实数据
        products = fetch_product_hunt_data()
        print(f"✅ 成功获取 {len(products)} 个产品")
    except Exception as e:
        print(f"❌ 获取Product Hunt数据失败: {e}")
        print("🔄 使用模拟数据继续...")
        products = fetch_mock_data()
    
    # 转换为数据格式
    products_data = convert_products_to_data(products)
    
    # 异步生成Markdown
    await async_generate_markdown(products_data, date_str)

def run_sync():
    """同步运行入口（用于兼容性）"""
    asyncio.run(main())

if __name__ == "__main__":
    # 检查是否在异步环境中
    try:
        # 如果已经在事件循环中，使用create_task
        loop = asyncio.get_running_loop()
        print("检测到现有事件循环，创建任务...")
        task = loop.create_task(main())
    except RuntimeError:
        # 没有事件循环，创建新的
        print("🚀 启动异步Product Hunt内容生成器...")
        asyncio.run(main())
