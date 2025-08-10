#!/usr/bin/env python3
"""
Demo script for Test Case Generator Bot
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from rich.console import Console
from rich.panel import Panel

from analyzers.code_analyzer import CodeAnalyzer
from generators.test_generator import TestGenerator
from agents.test_agent import TestGeneratorAgent

console = Console()

def main():
    """Run a demo of the Test Case Generator Bot."""
    
    console.print(Panel.fit(
        "[bold blue]Test Case Generator Bot Demo[/bold blue]\n"
        "Analyzing sample code and generating test cases...",
        border_style="blue"
    ))
    
    # Initialize components
    analyzer = CodeAnalyzer()
    generator = TestGenerator()
    agent = TestGeneratorAgent(analyzer, generator)
    
    # Process the sample file
    sample_file = "examples/sample_code.py"
    
    try:
        console.print(f"[yellow]Processing {sample_file}...[/yellow]")
        results = agent.process_file(sample_file, output_dir="demo_tests")
        
        console.print(f"\n[green]✅ Demo completed successfully![/green]")
        console.print(f"[green]Generated {results['test_count']} test cases[/green]")
        console.print(f"[green]Estimated coverage: {results['coverage_percentage']:.1f}%[/green]")
        console.print(f"[blue]Check the 'demo_tests' directory for generated tests[/blue]")
        
        # Show some example generated tests
        if results['tests']:
            console.print(f"\n[yellow]Example generated test:[/yellow]")
            example_test = results['tests'][0]
            console.print(Panel(
                f"[bold]{example_test.name}[/bold]\n\n"
                f"{example_test.test_code}",
                title=f"{example_test.test_type.value.title()} Test"
            ))
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())