import os
import sys
import traceback
import argparse
from dotenv import load_dotenv

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables from .env file
load_dotenv()

# Import the LLM providers
from llm_provider import BaseLLMProvider, get_llm_provider
from llm_openai import OpenAILLMProvider
from llm_gemini import GeminiLLMProvider
from llm_deepseek import DeepSeekLLMProvider
from llm_openrouter import OpenRouterLLMProvider

def test_provider(provider_class, provider_name, init_only=False, test_url=None):
    """Test a specific LLM provider"""
    print(f"\n=== Testing {provider_name} Provider ===")
    
    try:
        # Test initialization
        print(f"Initializing {provider_name}...")
        provider = provider_class()
        print(f"✅ {provider_name} initialized successfully")
        
        if init_only:
            return True
            
        # Test generate_keywords method
        print(f"Testing generate_keywords method...")
        name = "Test Product"
        tagline = "A simple test product"
        description = "This is a test product description for testing the LLM provider."
        keywords = provider.generate_keywords(name, tagline, description)
        print(f"✅ generate_keywords returned: {keywords}")
        
        # Test translate_text method
        print(f"Testing translate_text method...")
        text = "Hello, this is a test message for translation."
        translation = provider.translate_text(text)
        print(f"✅ translate_text returned: {translation}")
        
        # Test process_url method if URL is provided
        if test_url:
            print(f"Testing process_url method with URL: {test_url}")
            url_result = provider.process_url(test_url)
            if url_result["status"] == "success":
                print(f"✅ process_url returned title: {url_result['title']}")
                print(f"✅ process_url returned summary: {url_result['summary'][:100]}...")
            else:
                print(f"❌ Error processing URL: {url_result['error']}")
        
        return True
    except Exception as e:
        print(f"❌ Error testing {provider_name}: {str(e)}")
        print(traceback.format_exc())
        return False

def main():
    """Test LLM providers based on command line arguments"""
    parser = argparse.ArgumentParser(description="Test LLM providers")
    parser.add_argument("--provider", choices=["openai", "gemini", "deepseek", "openrouter", "all"], 
                        default="all", help="Specify which provider to test")
    parser.add_argument("--init-only", action="store_true", 
                        help="Test only initialization without making API calls")
    parser.add_argument("--url", type=str, default=None,
                        help="URL to test with process_url method")
    args = parser.parse_args()
    
    print(f"Starting LLM Provider Tests (Provider: {args.provider}, Init Only: {args.init_only}, URL: {args.url})")
    
    # Define all available providers
    all_providers = {
        "openai": (OpenAILLMProvider, "OpenAI"),
        "gemini": (GeminiLLMProvider, "Gemini"),
        "deepseek": (DeepSeekLLMProvider, "DeepSeek"),
        "openrouter": (OpenRouterLLMProvider, "OpenRouter")
    }
    
    # Determine which providers to test
    providers_to_test = []
    if args.provider == "all":
        providers_to_test = list(all_providers.values())
    else:
        if args.provider in all_providers:
            providers_to_test = [all_providers[args.provider]]
        else:
            print(f"Error: Unknown provider '{args.provider}'")
            sys.exit(1)
    
    # Test each selected provider
    results = {}
    for provider_class, provider_name in providers_to_test:
        results[provider_name] = test_provider(provider_class, provider_name, args.init_only, args.url)
    
    # Print summary
    print("\n=== Test Results Summary ===")
    for provider_name, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{provider_name}: {status}")
    
    # Test the get_llm_provider function if testing all providers
    if args.provider == "all":
        print("\n=== Testing get_llm_provider function ===")
        try:
            current_provider = os.getenv("LLM_PROVIDER", "openai")
            print(f"Current LLM_PROVIDER: {current_provider}")
            provider = get_llm_provider()
            print(f"✅ get_llm_provider returned: {provider.__class__.__name__}")
        except Exception as e:
            print(f"❌ Error testing get_llm_provider: {str(e)}")

if __name__ == "__main__":
    main() 