from click.testing import CliRunner
from pathlib import Path
import textwrap

from src.main import main as cli_main


def write_tmp(tmp_path: Path, name: str, content: str) -> Path:
    p = tmp_path / name
    p.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return p


def test_cli_interactive_quit(tmp_path):
    code = """
    def add(a, b):
        return a + b
    """
    f = write_tmp(tmp_path, "sample.py", code)
    runner = CliRunner()
    # Provide just 'quit' to exit interactive mode
    result = runner.invoke(cli_main, ["-f", str(f), "-l", "python", "-i"], input="quit\n")
    assert result.exit_code == 0, result.output
    assert "Interactive Test Refinement" in result.output


def test_cli_interactive_view_then_quit(tmp_path):
    code = """
    def mul(x, y):
        return x * y
    """
    f = write_tmp(tmp_path, "sample.py", code)
    runner = CliRunner()
    # View first test, then quit
    result = runner.invoke(
        cli_main,
        ["-f", str(f), "-l", "python", "-i"],
        input="view\n1\nquit\n",
    )
    assert result.exit_code == 0, result.output
    assert "Generated Test Cases" in result.output


def test_cli_interactive_remove_then_quit(tmp_path):
    code = """
    def sub(a, b):
        return a - b
    """
    f = write_tmp(tmp_path, "sample.py", code)
    runner = CliRunner()
    # Remove test 1, then quit
    result = runner.invoke(
        cli_main,
        ["-f", str(f), "-l", "python", "-i"],
        input="remove\n1\nquit\n",
    )
    assert result.exit_code == 0, result.output
    assert "Removed test" in result.output
