#!/usr/bin/env python3
"""
Test Case Generator Bot - Main Entry Point
"""
import click
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables early
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from src.agents.test_agent import TestGeneratorAgent
from src.config.configuration_manager import ConfigurationManager
from src.factories.analyzer_factory import AnalyzerFactory
from src.factories.generator_factory import GeneratorFactory
from src.factories.ai_provider_factory import AIProviderFactory
from src.interfaces.base_interfaces import Language

console = Console()

def check_ai_providers():
    """Check which AI providers are available and return the best one."""
    # Ensure .env file is loaded before checking environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv(override=True)
    except ImportError:
        pass

    def get_clean(key):
        """Get environment variable and strip any whitespace/newlines."""
        val = os.getenv(key)
        return val.strip() if val else None
    
    gemini_key = get_clean('GEMINI_API_KEY')
    openai_key = get_clean('OPENAI_API_KEY')
    anthropic_key = get_clean('ANTHROPIC_API_KEY')
    
    if gemini_key:
        return True, "gemini"
    elif openai_key:
        return True, "openai"
    elif anthropic_key:
        return True, "anthropic"
    else:
        return False, "mock"

@click.command()
@click.option('--file', '-f', required=True, help='Path to the code file to analyze')
@click.option('--language', '-l', help='Programming language (auto-detected if not specified)')
@click.option('--output', '-o', help='Output directory for generated tests')
@click.option('--interactive', '-i', is_flag=True, help='Enable interactive mode for test refinement')
@click.option('--coverage', '-c', is_flag=True, help='Generate coverage report')
@click.version_option(version='0.2.1', prog_name='voylla')
def main(file, language, output, interactive, coverage):
    """Test Case Generator Bot - Analyze code and generate comprehensive test cases."""
    
    console.print(Panel.fit(
        "[bold blue]Test Case Generator Bot[/bold blue]\n"
        "Analyzing code and generating intelligent test cases...",
        border_style="blue"
    ))
    
    # Initialize configuration manager
    config_manager = ConfigurationManager()
    
    # Use improved AI provider detection
    has_ai, preferred_provider = check_ai_providers()
    
    if has_ai and preferred_provider != 'mock':
        console.print(f"[green]🤖 AI Enhancement: {preferred_provider.title()}[/green]")
    else:
        console.print("[yellow]🤖 AI Enhancement: Disabled (set OPENAI_API_KEY, ANTHROPIC_API_KEY, or GEMINI_API_KEY in environment or .env file)[/yellow]")
        console.print("[dim]Available providers: OpenAI, Anthropic, Google Gemini[/dim]")
    
    # Validate input file
    code_file = Path(file)
    if not code_file.exists():
        console.print(f"[red]Error: File {file} not found[/red]")
        sys.exit(1)
    
    # Detect language if not specified
    if not language:
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java'
        }
        language = language_map.get(code_file.suffix.lower())
        if not language:
            console.print(f"[red]Error: Unable to detect language for {code_file.suffix}[/red]")
            sys.exit(1)
    
    # Initialize factories
    analyzer_factory = AnalyzerFactory()
    generator_factory = GeneratorFactory()
    ai_provider_factory = AIProviderFactory()
    
    # Create language-specific components
    try:
        lang_enum = Language(language)
        analyzer = analyzer_factory.create_analyzer(lang_enum)
        generator = generator_factory.create_generator(lang_enum)
        
        # Create AI provider
        ai_config = config_manager.get_ai_provider_config()
        ai_provider = ai_provider_factory.create_provider(preferred_provider, ai_config)
        
        # Initialize agent with configuration
        agent = TestGeneratorAgent(analyzer, generator, config_manager, ai_provider)
        
    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        sys.exit(1)
    
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