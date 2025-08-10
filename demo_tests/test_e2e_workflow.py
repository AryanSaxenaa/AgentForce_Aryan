"""End-to-end integration tests for Task 9.1.

Covers:
- Complete CLI workflow on real example code (Python)
- Multi-language path (JavaScript auto-detect)
- AI provider behavior without API keys (falls back to mock/disabled)

Notes:
- Real API calls are intentionally avoided here. See test_real_api_integration_optional for a gated test.
"""
from __future__ import annotations

import os
from pathlib import Path
import time
from click.testing import CliRunner

from src.main import main as cli_main


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_e2e_python_example_full_workflow(tmp_path: Path):
    """Run CLI on the repo's example Python file and verify outputs."""
    example = _repo_root() / "examples" / "sample_code.py"
    assert example.exists(), "examples/sample_code.py must exist for E2E test"

    out_dir = tmp_path / "generated_tests"
    runner = CliRunner()
    result = runner.invoke(
        cli_main,
        ["--file", str(example), "--language", "python", "--output", str(out_dir)],
    )

    assert result.exit_code == 0, result.output
    # Visible workflow signals
    assert "Analyzing" in result.output
    assert "Generated" in result.output
    assert "Coverage:" in result.output

    # Files should be created in the output directory
    assert out_dir.exists(), "Output directory should be created"
    files = list(out_dir.glob("test_*.py"))
    assert files, f"Expected generated test files in {out_dir}"


def test_e2e_autodetect_language_javascript(tmp_path: Path):
    """Ensure JS is auto-detected and processed without specifying --language."""
    code = """
    function add(a, b) { return a + b; }
    """
    js_file = tmp_path / "sample.js"
    js_file.write_text(code.strip() + "\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli_main, ["-f", str(js_file)])

    assert result.exit_code == 0, result.output
    assert "Analyzing" in result.output


def test_e2e_ai_provider_mock_when_no_keys(monkeypatch, tmp_path: Path):
    """When no API keys are present, CLI should show AI enhancement disabled."""
    # Ensure keys are absent
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    code = """
    def add(a, b):
        return a + b
    """
    py_file = tmp_path / "simple.py"
    py_file.write_text(code.strip() + "\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli_main, ["-f", str(py_file), "-l", "python"])

    assert result.exit_code == 0, result.output
    # Expect the disabled message when provider resolves to mock
    assert "AI Enhancement" in result.output
    assert "Disabled" in result.output


def test_real_api_integration_optional(monkeypatch, tmp_path: Path):
    """Optional real API smoke test; skipped unless REAL_API_TESTS=1 and keys set.

    This verifies that the factory chooses a real provider when a key is available.
    It does not force a network call to avoid flakiness.
    """
    import pytest
    from src.config.configuration_manager import ConfigurationManager
    from src.factories.ai_provider_factory import AIProviderFactory, MockAIProvider

    if os.getenv("REAL_API_TESTS") != "1":
        pytest.skip("Set REAL_API_TESTS=1 to enable real API smoke test")

    # Prefer OpenAI key if present; otherwise Anthropic; else skip
    has_openai = bool(os.getenv("OPENAI_API_KEY"))
    has_anthropic = bool(os.getenv("ANTHROPIC_API_KEY"))
    if not (has_openai or has_anthropic):
        pytest.skip("No API keys available for real API test")

    cfg = ConfigurationManager()
    preferred = cfg.get_preferred_ai_provider()
    factory = AIProviderFactory()

    provider = factory.create_provider(preferred, cfg.get_ai_provider_config())

    # If keys/modules are available, provider should not be MockAIProvider
    assert not isinstance(provider, MockAIProvider)


def test_e2e_autodetect_language_java(tmp_path: Path):
    """Ensure Java is auto-detected and processed without specifying --language."""
    code = """
    public class Sample {
        public static int add(int a, int b) { return a + b; }
    }
    """
    java_file = tmp_path / "Sample.java"
    java_file.write_text(code.strip() + "\n", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(cli_main, ["-f", str(java_file)])

    assert result.exit_code == 0, result.output
    assert "Analyzing" in result.output


def test_performance_smoke_optional(tmp_path: Path):
    """Optional performance smoke: run on a larger file and capture runtime.

    Skips assertion unless PERF_TESTS=1 to avoid flakiness.
    """
    import pytest

    # Build a larger Python file with many small functions
    lines = ["""
def f0(x):
    return x + 1
""".strip()]
    for i in range(1, 200):
        lines.append(f"def f{i}(x, y):\n    return x * y + {i}\n")
    code = "\n\n".join(lines)
    big_file = tmp_path / "big.py"
    big_file.write_text(code, encoding="utf-8")

    runner = CliRunner()
    start = time.perf_counter()
    result = runner.invoke(cli_main, ["-f", str(big_file), "-l", "python"])
    elapsed = time.perf_counter() - start

    assert result.exit_code == 0, result.output

    if os.getenv("PERF_TESTS") == "1":
        # Generous threshold to account for environments; adjust as needed.
        assert elapsed < 5.0, f"E2E generation took too long: {elapsed:.2f}s"
