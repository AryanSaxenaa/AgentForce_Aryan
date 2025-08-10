# User Guide

## Install

```bash
pip install -r requirements.txt
```

Optionally create a `.env` file (auto-loaded) with:

```properties
AI_PROVIDER=auto
OPENAI_API_KEY=...
# ANTHROPIC_API_KEY=...
AI_MAX_TOKENS=1000
AI_TEMPERATURE=0.3
AI_TIMEOUT=30
```

## Run CLI

```bash
voylla --file examples/sample_code.py --language python --output test_output
```

- Omit `--language` to auto-detect JS/Java/Python.
- Use `--interactive` to enter conversational refinement.

## Demo

```bash
voylla -f examples/sample_code.py -l python -o test_output
```

## Tips
- Keep temperature low (0.2–0.5) for consistent tests.
- Increase timeout for very large files.
- Without API keys, the tool falls back to a mock AI provider.
