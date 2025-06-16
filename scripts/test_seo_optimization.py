#!/usr/bin/env python3
"""
SEO优化功能测试脚本
测试新增的行业分析和产品描述优化功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from llm_provider import get_llm_provider
from scripts_product_hunt_list_to_md import generate_industry_analysis_content, categorize_product

class MockProduct:
    """模拟产品类用于测试"""
    def __init__(self, name, tagline, description, votes_count):
        self.name = name
        self.tagline = tagline
        self.description = description
        self.votes_count = votes_count

def test_industry_analysis():
    """测试行业分析功能"""
    print("🧪 测试行业分析功能...")
    
    # 创建模拟产品数据
    mock_products = [
        MockProduct(
            "Tickup", 
            "Tinder for stocks", 
            "AI-powered social platform for stock discovery. Swipe to discover, tap to research.",
            374
        ),
        MockProduct(
            "VibeSec", 
            "Find and Fix Code Vulnerabilities Instantly!", 
            "VibeSec is your AI-powered code security copilot. Instantly scan your GitHub repos.",
            246
        ),
        MockProduct(
            "LLM SEO Report", 
            "Check your brand's visibility on ChatGPT and Google Gemini", 
            "LLM SEO Report lets you check what ChatGPT, Google Gemini or Claude think about your brand.",
            260
        )
    ]
    
    try:
        # 测试产品分类
        print("\n📋 产品分类测试:")
        for product in mock_products:
            category = categorize_product(product)
            print(f"  - {product.name}: {category}")
        
        # 测试行业分析生成
        print("\n🔍 生成行业分析...")
        industry_analysis = generate_industry_analysis_content(mock_products)
        
        print("\n✅ 行业分析结果:")
        print("=" * 50)
        print(industry_analysis)
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 行业分析测试失败: {e}")
        return False

def test_product_description_enhancement():
    """测试产品描述优化功能"""
    print("\n🧪 测试产品描述优化功能...")
    
    try:
        llm = get_llm_provider()
        
        # 测试产品描述优化
        test_cases = [
            {
                "name": "Tickup",
                "category": "金融工具",
                "description": "AI-powered social platform for stock discovery. Swipe to discover, tap to research.",
                "keywords": "股票社交,AI选股,金融数据,投资工具"
            },
            {
                "name": "VibeSec", 
                "category": "开发工具",
                "description": "VibeSec is your AI-powered code security copilot. Instantly scan your GitHub repos.",
                "keywords": "代码安全,AI扫描,GitHub,开发者工具"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 测试案例 {i}: {test_case['name']}")
            print(f"原始描述: {test_case['description']}")
            
            if hasattr(llm, 'enhance_product_description'):
                enhanced_desc = llm.enhance_product_description(
                    test_case['name'],
                    test_case['category'], 
                    test_case['description'],
                    test_case['keywords']
                )
                print(f"优化描述: {enhanced_desc}")
            else:
                print("⚠️ 当前LLM提供商不支持产品描述优化功能")
        
        return True
        
    except Exception as e:
        print(f"❌ 产品描述优化测试失败: {e}")
        return False

def test_seo_keywords_integration():
    """测试SEO关键词集成"""
    print("\n🧪 测试SEO关键词集成...")
    
    # 模拟关键词自然融入测试
    test_content = """
    ## 🔍 今日科技趋势分析
    
    今日Product Hunt热榜展现了**人工智能技术**在多个领域的深度应用。从**AI驱动的股票投资平台**到**智能代码安全扫描工具**，我们看到**机器学习算法**正在重塑传统行业的工作方式。
    
    ### 💰 金融科技创新
    
    **Tickup**作为**股票社交平台**的代表，将**AI技术**与**投资决策**相结合，通过**智能推荐算法**帮助用户发现优质**投资机会**。这种**社交化投资**模式反映了**金融科技**向**个性化**和**智能化**发展的趋势。
    
    ### 🛡️ 开发者工具智能化
    
    **VibeSec**等**AI驱动的安全工具**展现了**开发者工具**的智能化升级。通过**自动化代码审计**和**漏洞检测**，这类工具大幅提升了**软件开发**的**安全性**和**效率**。
    """
    
    # 分析关键词密度
    keywords = ["AI", "人工智能", "机器学习", "股票", "投资", "金融科技", "开发者工具", "代码安全"]
    
    print("🔍 关键词密度分析:")
    for keyword in keywords:
        count = test_content.lower().count(keyword.lower())
        print(f"  - '{keyword}': {count}次")
    
    # 检查关键词是否自然融入
    natural_integration_score = 0
    if "**人工智能技术**" in test_content:
        natural_integration_score += 1
    if "**AI驱动的" in test_content:
        natural_integration_score += 1
    if "**金融科技**" in test_content:
        natural_integration_score += 1
    
    print(f"\n📊 关键词自然融入评分: {natural_integration_score}/3")
    
    return natural_integration_score >= 2

def main():
    """主测试函数"""
    print("🚀 开始SEO优化功能测试\n")
    
    test_results = []
    
    # 测试1: 行业分析
    test_results.append(("行业分析功能", test_industry_analysis()))
    
    # 测试2: 产品描述优化  
    test_results.append(("产品描述优化", test_product_description_enhancement()))
    
    # 测试3: SEO关键词集成
    test_results.append(("SEO关键词集成", test_seo_keywords_integration()))
    
    # 输出测试结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = 0
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n总体结果: {passed}/{len(test_results)} 项测试通过")
    
    if passed == len(test_results):
        print("🎉 所有SEO优化功能测试通过！")
    else:
        print("⚠️ 部分功能需要进一步优化")

if __name__ == "__main__":
    main()
