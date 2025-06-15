#!/usr/bin/env python3
"""
演示Hugo标签和关键词生成功能
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

def demo_hugo_tags_generation():
    """演示Hugo标签生成功能"""
    
    # 设置使用DeepSeek提供商（因为它工作得很好）
    os.environ["LLM_PROVIDER"] = "deepseek"
    
    try:
        from llm_provider import get_llm_provider
        
        # 模拟真实的Product Hunt产品数据
        products_info = """
1. Cursor AI - AI代码编辑器
   - 标语: The AI-first code editor
   - 描述: 智能代码编辑器，集成GPT-4，提供实时代码建议和自动补全
   - 票数: 1247
   - 类别: 开发工具

2. Notion Calendar - 智能日历应用
   - 标语: Calendar that connects your tasks and time
   - 描述: 将任务管理与时间规划完美结合的智能日历应用
   - 票数: 892
   - 类别: 生产力工具

3. Midjourney V6 - AI图像生成
   - 标语: Create stunning images with AI
   - 描述: 最新版本的AI图像生成工具，支持更高质量的图像创作
   - 票数: 756
   - 类别: AI工具

4. Figma Dev Mode - 设计开发协作
   - 标语: Bridge design and development
   - 描述: 连接设计师和开发者的新功能，简化设计到代码的转换
   - 票数: 634
   - 类别: 设计工具

5. Linear Insights - 项目分析工具
   - 标语: Data-driven project insights
   - 描述: 为开发团队提供项目进度和效率分析的数据洞察工具
   - 票数: 523
   - 类别: 生产力工具
"""

        print("🚀 Hugo标签和关键词生成演示")
        print("=" * 50)
        
        # 获取LLM提供商
        provider = get_llm_provider()
        print(f"📡 使用LLM提供商: {type(provider).__name__}")
        
        # 生成Hugo标签和关键词
        print("\n🔄 正在生成Hugo标签和关键词...")
        result = provider.generate_hugo_tags_and_keywords(products_info)
        
        print(f"\n📄 生成结果:")
        print("-" * 30)
        print(result)
        
        # 解析并验证JSON
        try:
            parsed_result = json.loads(result)
            
            print(f"\n✅ JSON格式验证通过")
            print("-" * 30)
            
            tags = parsed_result.get('tags', [])
            keywords = parsed_result.get('keywords', [])
            
            print(f"🏷️  标签 ({len(tags)}个):")
            for i, tag in enumerate(tags, 1):
                print(f"   {i}. {tag}")
            
            print(f"\n🔑 关键词 ({len(keywords)}个):")
            for i, keyword in enumerate(keywords, 1):
                print(f"   {i}. {keyword}")
            
            # 生成Hugo Front Matter示例
            print(f"\n📝 Hugo Front Matter 示例:")
            print("-" * 30)
            print("---")
            print('title: "Product Hunt 今日热榜 2025-06-14 | AI工具与生产力应用精选"')
            print('date: 2025-06-14')
            print('description: "今日Product Hunt热榜精选：AI代码编辑器Cursor、智能日历Notion Calendar等5款创新产品，助力提升工作效率"')
            print(f'tags: {json.dumps(tags, ensure_ascii=False)}')
            print(f'keywords: {json.dumps(keywords, ensure_ascii=False)}')
            print('votes: 4052')
            print('cover:')
            print('  image: "https://your-cdn.com/images/ph-daily-2025-06-14.png"')
            print('  alt: "Product Hunt 今日热榜产品展示"')
            print("---")
            
            print(f"\n🎯 SEO优化建议:")
            print("-" * 30)
            print("✅ 标签涵盖了主要产品类别")
            print("✅ 关键词包含具体产品名称")
            print("✅ 适合搜索引擎优化")
            print("✅ 符合Hugo Front Matter格式")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON格式错误: {e}")
            print("原始输出:", result)
            
    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_hugo_tags_generation()
