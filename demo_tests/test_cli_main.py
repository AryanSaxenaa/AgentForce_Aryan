"""CLI integration tests for Task 7.1 (Click + Rich)."""
from click.testing import CliRunner
from pathlib import Path
import textwrap

from src.main import main as cli_main


def write_tmp(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return p


def test_cli_python_basic(tmp_path):
    code = """
    def add(a, b):
        # simple add
        return a + b
    """
    f = write_tmp(tmp_path, "sample.py", code)
    runner = CliRunner()
    result = runner.invoke(cli_main, ["--file", str(f), "--language", "python"])
    assert result.exit_code == 0, result.output
    assert "Analyzing" in result.output
    assert "Generated" in result.output


def test_cli_autodetect_language_js(tmp_path):
    code = """
    function add(a, b) { return a + b; }
    """
    f = write_tmp(tmp_path, "sample.js", code)
    runner = CliRunner()
    result = runner.invoke(cli_main, ["-f", str(f)])
    assert result.exit_code == 0, result.output
    assert "Analyzing" in result.output


def test_cli_missing_file(tmp_path):
    runner = CliRunner()
    result = runner.invoke(cli_main, ["-f", str(tmp_path / "nope.py"), "-l", "python"]) 
    assert result.exit_code != 0
    assert "Error: File" in result.output
