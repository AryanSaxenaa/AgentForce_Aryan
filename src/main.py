#!/usr/bin/env python3
"""
Test Case Generator Bot - Main Entry Point
"""
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

from agents.test_agent import TestGeneratorAgent
from analyzers.code_analyzer import CodeAnalyzer
from generators.test_generator import TestGenerator

console = Console()

@click.command()
@click.option('--file', '-f', required=True, help='Path to the code file to analyze')
@click.option('--language', '-l', help='Programming language (auto-detected if not specified)')
@click.option('--output', '-o', help='Output directory for generated tests')
@click.option('--interactive', '-i', is_flag=True, help='Enable interactive mode for test refinement')
@click.option('--coverage', '-c', is_flag=True, help='Generate coverage report')
def main(file, language, output, interactive, coverage):
    """Test Case Generator Bot - Analyze code and generate comprehensive test cases."""
    
    console.print(Panel.fit(
        "[bold blue]Test Case Generator Bot[/bold blue]\n"
        "Analyzing code and generating intelligent test cases...",
        border_style="blue"
    ))
    
    # Validate input file
    code_file = Path(file)
    if not code_file.exists():
        console.print(f"[red]Error: File {file} not found[/red]")
        sys.exit(1)
    
    # Initialize components
    analyzer = CodeAnalyzer()
    generator = TestGenerator()
    agent = TestGeneratorAgent(analyzer, generator)
    
    try:
        # Analyze and generate tests
        console.print(f"[yellow]Analyzing {code_file.name}...[/yellow]")
        results = agent.process_file(str(code_file), language, output)
        
        # Display results
        console.print(f"[green]✓ Generated {results['test_count']} test cases[/green]")
        console.print(f"[green]✓ Coverage: {results['coverage_percentage']:.1f}%[/green]")
        
        if interactive:
            agent.interactive_refinement()
            
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()