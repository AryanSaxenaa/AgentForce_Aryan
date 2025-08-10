# API Reference (High-level)

## CLI (src/main.py)
- Command: `voylla --file <path> [--language <lang>] [--output <dir>] [--interactive]`
- Prints analysis progress, generates tests, and shows estimated coverage.

## Key Classes
- `CodeAnalyzer` — parses code, detects functions/classes, edge/perf risks.
- `TestGenerator` — generates tests and integrates AI provider enhancements.
- `TestGeneratorAgent` — orchestration for analyze → generate → (interactive) refine → save.
- `AIProviderFactory` — selects OpenAI/Anthropic/Mock provider based on env.
- `ConfigurationManager` — loads YAML/env and resolves provider, model, and limits.

## Configuration
Use `.env` or YAML (`config/config.yaml`). Important keys:
- `AI_PROVIDER`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- `OPENAI_MODEL`, `ANTHROPIC_MODEL`
- `AI_MAX_TOKENS`, `AI_TEMPERATURE`, `AI_TIMEOUT`
