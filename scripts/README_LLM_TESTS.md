# LLM Provider Tests

This script allows testing the various LLM providers used in the Product Hunt Daily Hot application.

## Prerequisites

Make sure you have the required API keys set in your environment variables or in a `.env` file:

- **全局配置**:
  - `LLM_PROVIDER`: 指定使用哪个LLM提供商 (可选，默认为 "openai")，可选值: "openai", "gemini", "deepseek", "openrouter"

- **OpenAI**: 
  - `OPENAI_API_KEY`: API密钥
  - `OPENAI_MODEL`: 模型名称 (可选，默认为 "gpt-4o-mini")
  - `OPENAI_API_BASE`: 自定义API基础URL (可选)

- **Gemini**: 
  - `GEMINI_API_KEY`: API密钥
  - `GEMINI_MODEL`: 模型名称 (可选，默认为 "gemini-2.0-flash")
  - `GEMINI_API_BASE`: 自定义API基础URL (可选)

- **DeepSeek**: 
  - `DEEPSEEK_API_KEY`: API密钥
  - `DEEPSEEK_MODEL`: 模型名称 (可选)
  - `DEEPSEEK_API_BASE`: 自定义API基础URL (可选)

- **OpenRouter**: 
  - `OPENROUTER_API_KEY`: API密钥
  - `OPENROUTER_MODEL`: 模型名称 (可选)
  - `OPENROUTER_API_BASE`: 自定义API基础URL (可选)

Additionally, make sure you have the required Python packages installed:
```bash
pip install requests beautifulsoup4 python-dotenv
```

## Usage

```bash
# Test all providers
python test_llm_providers.py

# Test a specific provider
python test_llm_providers.py --provider openai
python test_llm_providers.py --provider gemini
python test_llm_providers.py --provider deepseek
python test_llm_providers.py --provider openrouter

# Test only initialization without making API calls
python test_llm_providers.py --init-only

# Test initialization of a specific provider
python test_llm_providers.py --provider openai --init-only

# Test URL processing functionality
python test_llm_providers.py --url https://example.com
python test_llm_providers.py --provider openai --url https://example.com
```

## What the test does

1. **Initialization Test**: Verifies that the provider can be initialized with the provided API keys
2. **generate_keywords Test**: Tests the provider's ability to generate keywords from product information
3. **translate_text Test**: Tests the provider's ability to translate text
4. **process_url Test**: Tests the provider's ability to process and summarize content from a URL (if URL is provided)

## Supported Features

Each LLM provider implements the following methods:

1. **generate_keywords**: Generates keywords based on product information
2. **translate_text**: Translates text between languages
3. **process_url**: Fetches content from a URL, extracts text, and generates a summary using the LLM

## 配置说明

### 选择LLM提供商

您可以通过设置`LLM_PROVIDER`环境变量来选择默认的LLM提供商：

```bash
# 在.env文件中
LLM_PROVIDER=gemini

# 或在环境变量中
export LLM_PROVIDER=gemini
```

可选值: "openai", "gemini", "deepseek", "openrouter"。如果未设置，默认使用"openai"。

### 自定义API URL

每个LLM提供商都支持通过环境变量配置自定义API URL：

- OpenAI: `OPENAI_API_BASE`
- Gemini: `GEMINI_API_BASE`
- DeepSeek: `DEEPSEEK_API_BASE`
- OpenRouter: `OPENROUTER_API_BASE`

这对于使用自托管模型、代理服务或区域特定端点非常有用。如果未设置这些变量，将使用各服务的默认URL。

## Troubleshooting

If a test fails, check:

1. Your API keys are correctly set in the environment or `.env` file
2. You have network connectivity to the API endpoints
3. Your API account has sufficient credits/quota
4. The requested model is available for your account
5. For URL processing, ensure the URL is accessible and contains readable content 