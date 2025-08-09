# Project Structure

## Directory Organization

```
test-generator-bot/
├── src/                    # Main source code
│   ├── agents/            # AI agent orchestration logic
│   ├── analyzers/         # Code analysis modules
│   ├── generators/        # Test case generation engines
│   ├── integrations/      # CI/CD and external integrations
│   ├── config/           # Configuration management
│   └── main.py           # CLI entry point
├── config/               # Configuration files
│   └── config.yaml       # Main application config
├── examples/             # Sample code for testing
├── demo_tests/           # Generated test examples
├── .kiro/               # Kiro IDE configuration
└── .env.example         # Environment template
```

## Architecture Patterns

### Modular Design
- **Separation of Concerns**: Each module has a single responsibility
- **Agent Pattern**: `TestGeneratorAgent` orchestrates the workflow
- **Strategy Pattern**: Multiple AI providers with fallback logic
- **Factory Pattern**: Language-specific analyzers and generators

### Component Responsibilities

- **agents/**: High-level workflow orchestration and user interaction
- **analyzers/**: Code parsing, AST analysis, complexity detection
- **generators/**: Test case creation, formatting, output generation  
- **integrations/**: GitHub Actions, CI/CD pipeline integration
- **config/**: Environment setup, AI provider configuration

### File Naming Conventions

- **Classes**: PascalCase (e.g., `TestGeneratorAgent`)
- **Files**: snake_case (e.g., `test_agent.py`)
- **Constants**: UPPER_SNAKE_CASE
- **Private methods**: Leading underscore (`_private_method`)

### Import Structure

- Standard library imports first
- Third-party imports second  
- Local imports last
- Relative imports within modules preferred

### Configuration Hierarchy

1. Environment variables (`.env`)
2. YAML configuration (`config/config.yaml`)
3. Command-line arguments
4. Default values in code