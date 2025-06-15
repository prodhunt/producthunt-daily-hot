#!/usr/bin/env python3
"""
测试Hugo标签和关键词生成功能
"""

import os
import sys
import json
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载环境变量
load_dotenv()

from llm_provider import get_llm_provider

def test_hugo_tags_generation():
    """测试Hugo标签和关键词生成功能"""
    
    # 模拟产品信息
    test_products_info = """
1. AI Voice Cloning Tool
   - 标语: Clone any voice with just 3 seconds of audio
   - 描述: Advanced AI technology that can replicate human voices with incredible accuracy
   - 票数: 234

2. Productivity Dashboard
   - 标语: All your work tools in one place
   - 描述: Unified dashboard for managing tasks, calendar, notes, and team collaboration
   - 票数: 189

3. Code Review Assistant
   - 标语: AI-powered code review for better software quality
   - 描述: Automated code analysis and suggestions for improving code quality and security
   - 票数: 156
"""

    try:
        # 获取LLM提供商
        provider = get_llm_provider()
        print(f"使用LLM提供商: {type(provider).__name__}")
        
        # 生成Hugo标签和关键词
        print("\n正在生成Hugo标签和关键词...")
        result = provider.generate_hugo_tags_and_keywords(test_products_info)
        
        print(f"\n生成结果:")
        print(result)
        
        # 尝试解析JSON
        try:
            parsed_result = json.loads(result)
            print(f"\n✅ JSON格式验证通过")
            print(f"标签: {parsed_result.get('tags', [])}")
            print(f"关键词: {parsed_result.get('keywords', [])}")
            
            # 验证标签是否在预定义范围内
            predefined_tags = [
                "AI工具", "生产力工具", "设计工具", "开发工具", 
                "营销工具", "娱乐工具", "教育工具", "健康工具", "金融工具"
            ]
            
            generated_tags = parsed_result.get('tags', [])
            valid_tags = []
            invalid_tags = []
            
            for tag in generated_tags:
                if tag in predefined_tags or tag in ["Product Hunt", "每日热榜", "创新产品"]:
                    valid_tags.append(tag)
                else:
                    invalid_tags.append(tag)
            
            print(f"\n标签验证:")
            print(f"✅ 有效标签: {valid_tags}")
            if invalid_tags:
                print(f"⚠️ 无效标签: {invalid_tags}")
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON格式错误: {e}")
            print("原始输出:", result)
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_all_providers():
    """测试所有可用的LLM提供商"""
    providers = ["openai", "gemini", "deepseek", "openrouter"]
    
    for provider_name in providers:
        print(f"\n{'='*50}")
        print(f"测试 {provider_name.upper()} 提供商")
        print(f"{'='*50}")
        
        # 临时设置环境变量
        original_provider = os.getenv("LLM_PROVIDER")
        os.environ["LLM_PROVIDER"] = provider_name
        
        try:
            test_hugo_tags_generation()
        except Exception as e:
            print(f"❌ {provider_name} 提供商测试失败: {e}")
        
        # 恢复原始环境变量
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        elif "LLM_PROVIDER" in os.environ:
            del os.environ["LLM_PROVIDER"]

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试Hugo标签生成功能")
    parser.add_argument("--all", action="store_true", help="测试所有提供商")
    parser.add_argument("--provider", type=str, help="指定测试的提供商")
    
    args = parser.parse_args()
    
    if args.all:
        test_all_providers()
    elif args.provider:
        os.environ["LLM_PROVIDER"] = args.provider
        test_hugo_tags_generation()
    else:
        test_hugo_tags_generation()
