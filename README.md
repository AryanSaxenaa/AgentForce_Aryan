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
2. Set up your AI model API key
3. Run: `python src/main.py --file your_code.py`