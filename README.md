# Test Case Generator Bot

An AI-powered agent that analyzes code and generates comprehensive test cases for Python, Java, and JavaScript.

## Features

- **Multi-language Support**: Python, Java, JavaScript
- **Comprehensive Test Generation**: Unit, integration, and edge cases
- **Code Analysis**: Detects edge conditions and performance risks
- **Coverage Reports**: Analyzes test coverage gaps
- **Interactive Refinement**: Conversational test case improvement
- **CI Integration**: GitHub Actions support for PR test suggestions

## Project Structure

```
test-generator-bot/
├── src/
│   ├── analyzers/          # Code analysis modules
│   ├── generators/         # Test case generators
│   ├── agents/            # AI agent logic
│   └── integrations/      # CI/CD integrations
├── tests/                 # Project tests
├── examples/              # Example code and generated tests
└── config/               # Configuration files
```

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up AI API key (optional but recommended):
   ```bash
   python setup_ai.py
   ```
   Or manually set environment variables:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   # OR
   export ANTHROPIC_API_KEY="your-api-key-here"
   ```
3. Run: `python src/main.py --file your_code.py`

## AI Enhancement

The bot supports multiple AI providers for enhanced test generation:

- **OpenAI GPT-4**: Set `OPENAI_API_KEY` environment variable
- **Anthropic Claude**: Set `ANTHROPIC_API_KEY` environment variable  
- **Auto-detection**: Will use available provider automatically
- **Mock Mode**: Works without API keys (basic enhancement only)

### Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
# Choose provider: "openai", "anthropic", "auto", or "mock"
AI_PROVIDER=auto
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```