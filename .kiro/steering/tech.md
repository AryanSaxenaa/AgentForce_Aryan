# Technology Stack

## Core Technologies

- **Python 3.8+**: Primary development language
- **Rich**: Terminal UI and formatting
- **Click**: Command-line interface framework
- **Tree-sitter**: Multi-language code parsing
- **PyYAML**: Configuration management

## AI Integration

- **OpenAI API**: GPT-4 for enhanced test generation
- **Anthropic API**: Claude as fallback AI provider
- **Auto-detection**: Automatic provider selection based on available API keys

## Testing & Quality

- **pytest**: Test framework and runner
- **coverage**: Code coverage analysis
- **black**: Code formatting
- **flake8**: Linting and style checking

## Language Support

- **Python**: tree-sitter-python parser
- **JavaScript/TypeScript**: tree-sitter-javascript parser  
- **Java**: tree-sitter-java parser

## Common Commands

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Configure AI providers (interactive setup)
python setup_ai.py

# Manual environment setup
cp .env.example .env
# Edit .env with your API keys
```

### Development
```bash
# Run the main application
python src/main.py --file your_code.py

# Run demo
python demo.py

# Format code
black src/ demo.py

# Lint code
flake8 src/ demo.py

# Run tests
pytest demo_tests/

# Generate coverage report
coverage run -m pytest demo_tests/
coverage report
```

### Configuration

- **Main config**: `config/config.yaml`
- **Environment variables**: `.env` (copy from `.env.example`)
- **AI provider priority**: auto > openai > anthropic > mock