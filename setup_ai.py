#!/usr/bin/env python3
"""
AI Setup Script - Help users configure API keys for test enhancement
"""
import os
import sys
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.ai_config import AIConfigManager

console = Console()

def main():
    """Interactive AI setup script."""
    
    console.print(Panel.fit(
        "[bold blue]Test Case Generator Bot - AI Setup[/bold blue]\n"
        "Configure your AI API keys for enhanced test generation",
        border_style="blue"
    ))
    
    config_manager = AIConfigManager()
    setup_info = config_manager.validate_setup()
    
    # Display current status
    display_current_status(setup_info)
    
    # Check if user wants to configure
    if setup_info['has_ai_capability']:
        if not Confirm.ask("Would you like to reconfigure your AI settings?"):
            console.print("[green]✓ AI is already configured and ready to use![/green]")
            return
    else:
        console.print("\n[yellow]No AI API keys detected. Let's set one up![/yellow]")
    
    # Guide user through setup
    setup_api_keys()
    
    # Verify setup
    console.print("\n[blue]Verifying setup...[/blue]")
    new_config = AIConfigManager()
    new_setup_info = new_config.validate_setup()
    
    if new_setup_info['has_ai_capability']:
        console.print("[green]✅ AI setup completed successfully![/green]")
        console.print(f"[green]Using: {new_setup_info['preferred_provider'].title()}[/green]")
    else:
        console.print("[red]❌ Setup incomplete. Please check your API keys.[/red]")

def display_current_status(setup_info):
    """Display current AI configuration status."""
    table = Table(title="Current AI Configuration")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Model", style="yellow")
    
    available = setup_info['available_providers']
    config = setup_info['config']
    
    # OpenAI status
    openai_status = "✅ Available" if available['openai'] else "❌ No API Key"
    table.add_row("OpenAI", openai_status, config.openai_model)
    
    # Anthropic status
    anthropic_status = "✅ Available" if available['anthropic'] else "❌ No API Key"
    table.add_row("Anthropic", anthropic_status, config.anthropic_model)
    
    # Current selection
    preferred = setup_info['preferred_provider']
    if preferred != 'mock':
        table.add_row("", "", "")
        table.add_row("Active Provider", f"🎯 {preferred.title()}", "")
    
    console.print(table)
    
    # Show recommendations
    if setup_info['recommendations']:
        console.print("\n[yellow]💡 Recommendations:[/yellow]")
        for rec in setup_info['recommendations']:
            console.print(f"   • {rec}")

def setup_api_keys():
    """Guide user through API key setup."""
    
    provider_choice = Prompt.ask(
        "\nWhich AI provider would you like to use?",
        choices=["openai", "anthropic", "both", "skip"],
        default="openai"
    )
    
    if provider_choice == "skip":
        console.print("[yellow]Skipping AI setup. You can run this script again later.[/yellow]")
        return
    
    if provider_choice in ["openai", "both"]:
        setup_openai()
    
    if provider_choice in ["anthropic", "both"]:
        setup_anthropic()

def setup_openai():
    """Setup OpenAI API key."""
    console.print("\n[blue]Setting up OpenAI API[/blue]")
    console.print("1. Go to https://platform.openai.com/api-keys")
    console.print("2. Create a new API key")
    console.print("3. Copy the key and paste it below")
    
    api_key = Prompt.ask("\nEnter your OpenAI API key", password=True)
    
    if api_key:
        # Test the API key
        if test_openai_key(api_key):
            set_env_var("OPENAI_API_KEY", api_key)
            console.print("[green]✅ OpenAI API key configured successfully![/green]")
        else:
            console.print("[red]❌ Invalid API key. Please check and try again.[/red]")
    else:
        console.print("[yellow]Skipping OpenAI setup.[/yellow]")

def setup_anthropic():
    """Setup Anthropic API key."""
    console.print("\n[blue]Setting up Anthropic API[/blue]")
    console.print("1. Go to https://console.anthropic.com/")
    console.print("2. Create a new API key")
    console.print("3. Copy the key and paste it below")
    
    api_key = Prompt.ask("\nEnter your Anthropic API key", password=True)
    
    if api_key:
        # Test the API key
        if test_anthropic_key(api_key):
            set_env_var("ANTHROPIC_API_KEY", api_key)
            console.print("[green]✅ Anthropic API key configured successfully![/green]")
        else:
            console.print("[red]❌ Invalid API key. Please check and try again.[/red]")
    else:
        console.print("[yellow]Skipping Anthropic setup.[/yellow]")

def test_openai_key(api_key: str) -> bool:
    """Test OpenAI API key validity."""
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Make a minimal test request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        return True
    except Exception as e:
        console.print(f"[red]OpenAI API test failed: {e}[/red]")
        return False

def test_anthropic_key(api_key: str) -> bool:
    """Test Anthropic API key validity."""
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        
        # Make a minimal test request
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=5,
            messages=[{"role": "user", "content": "Hello"}]
        )
        return True
    except Exception as e:
        console.print(f"[red]Anthropic API test failed: {e}[/red]")
        return False

def set_env_var(name: str, value: str):
    """Set environment variable for current session and provide instructions for persistence."""
    os.environ[name] = value
    
    console.print(f"\n[yellow]To make this permanent, add this to your shell profile:[/yellow]")
    console.print(f"[cyan]export {name}='{value}'[/cyan]")
    
    # Try to detect shell and provide specific instructions
    shell = os.environ.get('SHELL', '').split('/')[-1]
    if shell == 'bash':
        console.print("[yellow]Add to ~/.bashrc or ~/.bash_profile[/yellow]")
    elif shell == 'zsh':
        console.print("[yellow]Add to ~/.zshrc[/yellow]")
    elif shell == 'fish':
        console.print(f"[yellow]Or use: set -Ux {name} '{value}'[/yellow]")
    
    console.print("[yellow]Then restart your terminal or run: source ~/.bashrc[/yellow]")

if __name__ == "__main__":
    main()