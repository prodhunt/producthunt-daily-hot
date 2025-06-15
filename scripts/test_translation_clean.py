#!/usr/bin/env python3
"""
测试清洁翻译功能 - 确保没有翻译说明
"""

import sys
import os

# 添加项目根目录到 sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv 模块未安装，将直接使用环境变量")

from scripts.llm_provider import get_llm_provider

def test_clean_translation():
    """测试清洁翻译功能"""
    
    # 获取LLM提供商
    llm = get_llm_provider()
    print(f"使用LLM提供商: {type(llm).__name__}")
    
    # 测试文本（这些是容易产生翻译说明的文本）
    test_texts = [
        "A Website Builder for Everyone - Create stunning, high-performing websites in minutes without any code",
        "V-JEPA 2 - Meta's world model for physical understanding through video training",
        "Spill 2.0 - Visual conversations for culture-first social media with humor, insight, and authentic connection"
    ]
    
    print("\n🧪 测试清洁翻译功能...")
    print("=" * 60)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n📝 测试文本 {i}:")
        print(f"原文: {text}")
        print("-" * 40)
        
        try:
            # 调用翻译
            translation = llm.translate_text(text)
            print(f"译文: {translation}")
            
            # 检查是否包含翻译说明
            problematic_phrases = [
                "翻译说明", "注：", "说明：", "（翻译", "（说明", 
                "译者注", "注释", "解释", "翻译技巧", "处理方式"
            ]
            
            has_explanation = any(phrase in translation for phrase in problematic_phrases)
            
            if has_explanation:
                print("❌ 检测到翻译说明！")
                for phrase in problematic_phrases:
                    if phrase in translation:
                        print(f"   发现: '{phrase}'")
            else:
                print("✅ 翻译干净，无额外说明")
                
        except Exception as e:
            print(f"❌ 翻译失败: {e}")
        
        print("-" * 40)
    
    print(f"\n📊 测试完成！")

def test_with_different_providers():
    """测试不同的LLM提供商"""
    providers = ["deepseek", "openai", "gemini", "openrouter"]
    
    test_text = "Revolutionary social experience with culture-first mindset"
    
    for provider_name in providers:
        print(f"\n{'='*50}")
        print(f"测试 {provider_name.upper()} 提供商")
        print(f"{'='*50}")
        
        # 临时设置环境变量
        original_provider = os.getenv("LLM_PROVIDER")
        os.environ["LLM_PROVIDER"] = provider_name
        
        try:
            llm = get_llm_provider()
            translation = llm.translate_text(test_text)
            
            print(f"原文: {test_text}")
            print(f"译文: {translation}")
            
            # 检查清洁度
            problematic_phrases = ["翻译说明", "注：", "说明：", "（翻译", "（说明"]
            has_explanation = any(phrase in translation for phrase in problematic_phrases)
            
            if has_explanation:
                print("❌ 包含翻译说明")
            else:
                print("✅ 翻译干净")
                
        except Exception as e:
            print(f"❌ {provider_name} 提供商测试失败: {e}")
        
        # 恢复原始环境变量
        if original_provider:
            os.environ["LLM_PROVIDER"] = original_provider
        elif "LLM_PROVIDER" in os.environ:
            del os.environ["LLM_PROVIDER"]

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试清洁翻译功能")
    parser.add_argument("--all", action="store_true", help="测试所有提供商")
    
    args = parser.parse_args()
    
    if args.all:
        test_with_different_providers()
    else:
        test_clean_translation()
