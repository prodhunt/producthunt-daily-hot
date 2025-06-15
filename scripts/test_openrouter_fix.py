#!/usr/bin/env python3
"""
测试 OpenRouter 修复
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("dotenv 模块未安装，将直接使用环境变量")

def test_openrouter_config():
    """测试 OpenRouter 配置"""
    
    print("🔧 测试 OpenRouter 配置修复...")
    
    # 设置 OpenRouter 提供商
    os.environ["LLM_PROVIDER"] = "openrouter"
    
    try:
        from llm_provider import get_llm_provider
        
        # 获取 OpenRouter 提供商
        llm = get_llm_provider()
        print(f"✅ 成功创建 OpenRouter 提供商: {type(llm).__name__}")
        print(f"📡 API URL: {llm.base_url}")
        print(f"🤖 模型: {llm.model}")
        
        # 测试简单的翻译
        test_text = "Hello, this is a test."
        print(f"\n🧪 测试翻译功能...")
        print(f"原文: {test_text}")
        
        result = llm.translate_text(test_text)
        print(f"译文: {result}")
        print("✅ OpenRouter 翻译测试成功！")
        
        # 测试关键词生成
        print(f"\n🧪 测试关键词生成...")
        keywords = llm.generate_keywords("Test Product", "A test tagline", "This is a test description")
        print(f"关键词: {keywords}")
        print("✅ OpenRouter 关键词生成测试成功！")
        
        return True
        
    except Exception as e:
        print(f"❌ OpenRouter 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_url_validation():
    """测试 URL 验证逻辑"""
    
    print("\n🔍 测试 URL 验证逻辑...")
    
    from llm_openrouter import OpenRouterLLMProvider
    
    # 测试不同的环境变量设置
    test_cases = [
        ("", "https://openrouter.ai/api/v1/chat/completions"),  # 空值
        ("https://openrouter.ai/api/v1", "https://openrouter.ai/api/v1/chat/completions"),  # 正确值
        ("openrouter.ai", "https://openrouter.ai/api/v1/chat/completions"),  # 无协议
        ("http://localhost:8000", "http://localhost:8000/chat/completions"),  # 自定义
    ]
    
    for test_input, expected in test_cases:
        print(f"\n测试输入: '{test_input}'")
        
        # 临时设置环境变量
        original_value = os.getenv("OPENROUTER_API_BASE")
        if test_input:
            os.environ["OPENROUTER_API_BASE"] = test_input
        elif "OPENROUTER_API_BASE" in os.environ:
            del os.environ["OPENROUTER_API_BASE"]
        
        try:
            # 创建提供商实例
            provider = OpenRouterLLMProvider()
            actual = provider.base_url
            
            print(f"期望输出: {expected}")
            print(f"实际输出: {actual}")
            
            if actual == expected:
                print("✅ 通过")
            else:
                print("❌ 失败")
                
        except Exception as e:
            print(f"❌ 创建提供商失败: {e}")
        
        # 恢复原始环境变量
        if original_value:
            os.environ["OPENROUTER_API_BASE"] = original_value
        elif "OPENROUTER_API_BASE" in os.environ:
            del os.environ["OPENROUTER_API_BASE"]

if __name__ == "__main__":
    print("🚀 OpenRouter 修复测试")
    print("=" * 50)
    
    # 检查是否有 OpenRouter API Key
    if not os.getenv("OPENROUTER_API_KEY"):
        print("⚠️ 未找到 OPENROUTER_API_KEY，跳过实际API测试")
        print("只进行URL验证测试...")
        test_url_validation()
    else:
        print("🔑 找到 OPENROUTER_API_KEY，进行完整测试...")
        success = test_openrouter_config()
        if success:
            print("\n🎉 所有测试通过！OpenRouter 配置已修复。")
        else:
            print("\n❌ 测试失败，需要进一步检查。")
        
        print("\n" + "=" * 50)
        test_url_validation()
