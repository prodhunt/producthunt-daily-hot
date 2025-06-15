#!/usr/bin/env python3
"""
比较同步和异步版本的性能
模拟 GitHub Actions 环境
"""

import os
import sys
import time
import asyncio
from datetime import datetime

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv 模块未安装，将直接使用环境变量")

def test_sync_version():
    """测试同步版本性能"""
    print("🔄 测试同步版本...")
    start_time = time.time()
    
    try:
        from scripts_product_hunt_list_to_md import fetch_mock_data
        from llm_provider import get_llm_provider
        
        # 获取模拟数据
        products = fetch_mock_data()
        llm = get_llm_provider()
        
        print(f"📊 处理 {len(products)} 个产品（同步）...")
        
        # 模拟同步处理
        processed_count = 0
        for i, product in enumerate(products):
            try:
                # 模拟LLM调用（实际会更慢）
                keywords = llm.generate_keywords(product.name, product.tagline, product.description)
                tagline_cn = llm.translate_text(product.tagline)
                description_cn = llm.translate_text(product.description)
                
                processed_count += 1
                print(f"  ✅ 完成产品 {i+1}: {product.name}")
                
            except Exception as e:
                print(f"  ❌ 产品 {i+1} 处理失败: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"📈 同步版本结果:")
        print(f"  - 总耗时: {total_time:.1f}秒")
        print(f"  - 成功处理: {processed_count}/{len(products)}")
        print(f"  - 平均每个产品: {total_time/len(products):.1f}秒")
        
        return {
            'version': 'sync',
            'total_time': total_time,
            'processed_count': processed_count,
            'total_products': len(products),
            'avg_per_product': total_time/len(products)
        }
        
    except Exception as e:
        print(f"❌ 同步版本测试失败: {e}")
        return None

async def test_async_version():
    """测试异步版本性能"""
    print("\n🚀 测试异步版本...")
    start_time = time.time()
    
    try:
        from scripts_product_hunt_list_to_md import fetch_mock_data
        from async_product_processor import AsyncProductProcessor
        from llm_provider import get_llm_provider
        
        # 获取模拟数据
        products = fetch_mock_data()
        llm = get_llm_provider()
        
        print(f"📊 处理 {len(products)} 个产品（异步）...")
        
        # 转换为数据格式
        products_data = []
        for product in products:
            products_data.append({
                'name': product.name,
                'tagline': product.tagline,
                'description': product.description,
                'votesCount': product.votes_count
            })
        
        # 创建异步处理器
        processor = AsyncProductProcessor(llm, max_concurrent=3)  # 限制并发数
        
        # 异步处理
        results = await processor.process_all_products(products_data)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"📈 异步版本结果:")
        print(f"  - 总耗时: {total_time:.1f}秒")
        print(f"  - 成功处理: {len(results)}/{len(products)}")
        print(f"  - 平均每个产品: {total_time/len(products):.1f}秒")
        
        return {
            'version': 'async',
            'total_time': total_time,
            'processed_count': len(results),
            'total_products': len(products),
            'avg_per_product': total_time/len(products)
        }
        
    except Exception as e:
        print(f"❌ 异步版本测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_results(sync_result, async_result):
    """分析测试结果"""
    print("\n📊 性能对比分析")
    print("=" * 50)
    
    if not sync_result or not async_result:
        print("❌ 无法进行对比，某个版本测试失败")
        return
    
    # 时间对比
    time_improvement = ((sync_result['total_time'] - async_result['total_time']) / sync_result['total_time']) * 100
    
    print(f"⏱️ 执行时间对比:")
    print(f"  同步版本: {sync_result['total_time']:.1f}秒")
    print(f"  异步版本: {async_result['total_time']:.1f}秒")
    print(f"  性能提升: {time_improvement:.1f}%")
    
    # 成功率对比
    sync_success_rate = (sync_result['processed_count'] / sync_result['total_products']) * 100
    async_success_rate = (async_result['processed_count'] / async_result['total_products']) * 100
    
    print(f"\n✅ 成功率对比:")
    print(f"  同步版本: {sync_success_rate:.1f}%")
    print(f"  异步版本: {async_success_rate:.1f}%")
    
    # GitHub Actions 建议
    print(f"\n🎯 GitHub Actions 建议:")
    
    if time_improvement > 50 and async_success_rate >= 90:
        print("  ✅ 推荐使用异步版本")
        print("  理由: 显著的性能提升且成功率高")
    elif time_improvement > 30 and async_success_rate >= 95:
        print("  ✅ 推荐使用异步版本")
        print("  理由: 良好的性能提升且稳定性好")
    elif async_success_rate < sync_success_rate:
        print("  ⚠️ 推荐使用同步版本")
        print("  理由: 异步版本成功率较低，稳定性优先")
    else:
        print("  🤔 建议使用同步版本")
        print("  理由: 性能提升不明显，同步版本更稳定")

def github_actions_simulation():
    """模拟 GitHub Actions 环境特点"""
    print("🔧 GitHub Actions 环境模拟")
    print("=" * 50)
    
    # 检查环境变量
    required_vars = ['LLM_PROVIDER', 'OPENROUTER_API_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"⚠️ 缺少环境变量: {missing_vars}")
        print("这在 GitHub Actions 中会导致失败")
        return False
    
    # 检查网络连接（简单测试）
    try:
        import requests
        response = requests.get("https://httpbin.org/get", timeout=5)
        if response.status_code == 200:
            print("✅ 网络连接正常")
        else:
            print("⚠️ 网络连接异常")
    except Exception as e:
        print(f"❌ 网络测试失败: {e}")
        return False
    
    print("✅ GitHub Actions 环境模拟通过")
    return True

async def main():
    """主测试函数"""
    print("🚀 GitHub Actions 同步 vs 异步性能测试")
    print(f"🕐 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 环境检查
    if not github_actions_simulation():
        print("❌ 环境检查失败，跳过测试")
        return
    
    # 运行测试
    sync_result = test_sync_version()
    async_result = await test_async_version()
    
    # 分析结果
    analyze_results(sync_result, async_result)
    
    print(f"\n🕐 结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # 检查是否在异步环境中
    try:
        loop = asyncio.get_running_loop()
        print("检测到现有事件循环")
    except RuntimeError:
        # 没有事件循环，创建新的
        asyncio.run(main())
