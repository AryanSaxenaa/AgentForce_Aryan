#!/usr/bin/env python3
"""
Interactive AI Setup Wizard - Configure API keys for test enhancement
"""
import os
import sys
from pathlib import Path
from typing import Dict, Optional, Tuple
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.ai_config import AIConfigManager

console = Console()

def main():
    """Interactive AI setup wizard."""
    
    console.print(Panel.fit(
        "[bold blue]Test Case Generator Bot - AI Setup Wizard[/bold blue]\n"
        "Configure your AI API keys for enhanced test generation",
        border_style="blue"
    ))
    
    # Check current setup
    config_manager = AIConfigManager()
    setup_info = config_manager.validate_setup()
    
    # Display current status
    display_current_status(setup_info)
    
    # Determine if setup is needed
    if setup_info['has_ai_capability']:
        if not Confirm.ask("\nWould you like to reconfigure your AI settings?"):
            console.print("[green]✓ AI is already configured and ready to use![/green]")
            return
    else:
        console.print("\n[yellow]No AI API keys detected. Let's set one up![/yellow]")
    
    # Run setup wizard
    env_vars = run_setup_wizard()
    
    if env_vars:
        # Create .env file
        create_env_file(env_vars)
        
        # Verify setup
        verify_setup()
    else:
        console.print("[yellow]Setup cancelled. You can run this script again later.[/yellow]")

def display_current_status(setup_info: Dict):
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

def run_setup_wizard() -> Optional[Dict[str, str]]:
    """Run the interactive setup wizard."""
    console.print("\n[bold cyan]Setup Wizard[/bold cyan]")
    
    # Choose provider
    provider_choice = Prompt.ask(
        "\nWhich AI provider would you like to use?",
        choices=["openai", "anthropic", "both", "skip"],
        default="openai"
    )
    
    if provider_choice == "skip":
        return None
    
    env_vars = {}
    
    # Setup OpenAI
    if provider_choice in ["openai", "both"]:
        openai_key = setup_openai_interactive()
        if openai_key:
            env_vars["OPENAI_API_KEY"] = openai_key
            
            # Ask for model preference
            model = Prompt.ask(
                "Which OpenAI model would you like to use?",
                choices=["gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"],
                default="gpt-4"
            )
            env_vars["OPENAI_MODEL"] = model
    
    # Setup Anthropic
    if provider_choice in ["anthropic", "both"]:
        anthropic_key = setup_anthropic_interactive()
        if anthropic_key:
            env_vars["ANTHROPIC_API_KEY"] = anthropic_key
            
            # Ask for model preference
            model = Prompt.ask(
                "Which Anthropic model would you like to use?",
                choices=["claude-3-sonnet-20240229", "claude-3-haiku-20240307", "claude-3-opus-20240229"],
                default="claude-3-sonnet-20240229"
            )
            env_vars["ANTHROPIC_MODEL"] = model
    
    # Set provider preference
    if len([k for k in env_vars.keys() if "API_KEY" in k]) > 1:
        provider_pref = Prompt.ask(
            "Which provider should be preferred when both are available?",
            choices=["openai", "anthropic", "auto"],
            default="auto"
        )
        env_vars["AI_PROVIDER"] = provider_pref
    elif "OPENAI_API_KEY" in env_vars:
        env_vars["AI_PROVIDER"] = "openai"
    elif "ANTHROPIC_API_KEY" in env_vars:
        env_vars["AI_PROVIDER"] = "anthropic"
    
    # Configure advanced settings
    if Confirm.ask("\nWould you like to configure advanced AI settings?", default=False):
        env_vars.update(configure_advanced_settings())
    
    return env_vars if env_vars else None

def setup_openai_interactive() -> Optional[str]:
    """Interactive OpenAI setup."""
    console.print("\n[blue]Setting up OpenAI API[/blue]")
    console.print("1. Go to https://platform.openai.com/api-keys")
    console.print("2. Create a new API key")
    console.print("3. Copy the key and paste it below")
    
    while True:
        api_key = Prompt.ask("\nEnter your OpenAI API key (or 'skip' to skip)", password=True)
        
        if api_key.lower() == 'skip':
            console.print("[yellow]Skipping OpenAI setup.[/yellow]")
            return None
        
        if not api_key:
            console.print("[red]API key cannot be empty. Please try again.[/red]")
            continue
        
        # Validate API key
        if validate_openai_key(api_key):
            console.print("[green]✅ OpenAI API key validated successfully![/green]")
            return api_key
        else:
            console.print("[red]❌ Invalid API key. Please check and try again.[/red]")
            if not Confirm.ask("Would you like to try again?"):
                return None

def setup_anthropic_interactive() -> Optional[str]:
    """Interactive Anthropic setup."""
    console.print("\n[blue]Setting up Anthropic API[/blue]")
    console.print("1. Go to https://console.anthropic.com/")
    console.print("2. Create a new API key")
    console.print("3. Copy the key and paste it below")
    
    while True:
        api_key = Prompt.ask("\nEnter your Anthropic API key (or 'skip' to skip)", password=True)
        
        if api_key.lower() == 'skip':
            console.print("[yellow]Skipping Anthropic setup.[/yellow]")
            return None
        
        if not api_key:
            console.print("[red]API key cannot be empty. Please try again.[/red]")
            continue
        
        # Validate API key
        if validate_anthropic_key(api_key):
            console.print("[green]✅ Anthropic API key validated successfully![/green]")
            return api_key
        else:
            console.print("[red]❌ Invalid API key. Please check and try again.[/red]")
            if not Confirm.ask("Would you like to try again?"):
                return None

def configure_advanced_settings() -> Dict[str, str]:
    """Configure advanced AI settings."""
    settings = {}
    
    console.print("\n[cyan]Advanced Settings[/cyan]")
    
    # Max tokens
    max_tokens = Prompt.ask(
        "Maximum tokens per AI request",
        default="1000"
    )
    try:
        int(max_tokens)
        settings["AI_MAX_TOKENS"] = max_tokens
    except ValueError:
        console.print("[yellow]Invalid number, using default (1000)[/yellow]")
    
    # Temperature
    temperature = Prompt.ask(
        "AI temperature (0.0-2.0, lower = more focused)",
        default="0.3"
    )
    try:
        temp_val = float(temperature)
        if 0.0 <= temp_val <= 2.0:
            settings["AI_TEMPERATURE"] = temperature
        else:
            console.print("[yellow]Temperature out of range, using default (0.3)[/yellow]")
    except ValueError:
        console.print("[yellow]Invalid temperature, using default (0.3)[/yellow]")
    
    # Timeout
    timeout = Prompt.ask(
        "AI request timeout (seconds)",
        default="30"
    )
    try:
        int(timeout)
        settings["AI_TIMEOUT"] = timeout
    except ValueError:
        console.print("[yellow]Invalid timeout, using default (30)[/yellow]")
    
    return settings

def validate_openai_key(api_key: str) -> bool:
    """Validate OpenAI API key."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing OpenAI API key...", total=None)
        
        try:
            # Try importing openai
            import openai
            client = openai.OpenAI(api_key=api_key)
            
            # Make a minimal test request
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            progress.update(task, completed=True)
            return True
        except ImportError:
            progress.update(task, completed=True)
            console.print("[yellow]Warning: OpenAI library not installed. Key format appears valid.[/yellow]")
            return api_key.startswith("sk-") and len(api_key) > 20
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]OpenAI API test failed: {str(e)[:100]}...[/red]")
            return False

def validate_anthropic_key(api_key: str) -> bool:
    """Validate Anthropic API key."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Testing Anthropic API key...", total=None)
        
        try:
            # Try importing anthropic
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            
            # Make a minimal test request
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1,
                messages=[{"role": "user", "content": "Test"}]
            )
            progress.update(task, completed=True)
            return True
        except ImportError:
            progress.update(task, completed=True)
            console.print("[yellow]Warning: Anthropic library not installed. Key format appears valid.[/yellow]")
            return api_key.startswith("sk-ant-") and len(api_key) > 20
        except Exception as e:
            progress.update(task, completed=True)
            console.print(f"[red]Anthropic API test failed: {str(e)[:100]}...[/red]")
            return False

def create_env_file(env_vars: Dict[str, str]) -> bool:
    """Create .env file with proper formatting."""
    env_path = Path(".env")
    
    try:
        # Read existing .env if it exists
        existing_vars = {}
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_vars[key] = value
        
        # Merge with new variables
        existing_vars.update(env_vars)
        
        # Write .env file with proper formatting
        with open(env_path, 'w') as f:
            f.write("# Test Case Generator Bot - Environment Variables\n")
            f.write("# Generated by setup wizard\n\n")
            
            # AI Provider Configuration
            f.write("# AI Provider Configuration\n")
            if "AI_PROVIDER" in existing_vars:
                f.write(f"AI_PROVIDER={existing_vars['AI_PROVIDER']}\n")
            f.write("\n")
            
            # OpenAI Configuration
            if any(k.startswith("OPENAI_") for k in existing_vars):
                f.write("# OpenAI Configuration\n")
                for key in ["OPENAI_API_KEY", "OPENAI_MODEL"]:
                    if key in existing_vars:
                        f.write(f"{key}={existing_vars[key]}\n")
                f.write("\n")
            
            # Anthropic Configuration
            if any(k.startswith("ANTHROPIC_") for k in existing_vars):
                f.write("# Anthropic Configuration\n")
                for key in ["ANTHROPIC_API_KEY", "ANTHROPIC_MODEL"]:
                    if key in existing_vars:
                        f.write(f"{key}={existing_vars[key]}\n")
                f.write("\n")
            
            # AI Request Settings
            if any(k.startswith("AI_") and not k == "AI_PROVIDER" for k in existing_vars):
                f.write("# AI Request Settings\n")
                for key in ["AI_MAX_TOKENS", "AI_TEMPERATURE", "AI_TIMEOUT"]:
                    if key in existing_vars:
                        f.write(f"{key}={existing_vars[key]}\n")
                f.write("\n")
            
            # Other settings
            other_keys = [k for k in existing_vars.keys() 
                         if not k.startswith(("AI_", "OPENAI_", "ANTHROPIC_"))]
            if other_keys:
                f.write("# Other Settings\n")
                for key in other_keys:
                    f.write(f"{key}={existing_vars[key]}\n")
        
        console.print(f"[green]✅ Environment file created: {env_path.absolute()}[/green]")
        return True
        
    except Exception as e:
        console.print(f"[red]❌ Failed to create .env file: {e}[/red]")
        return False

def verify_setup():
    """Verify the setup was successful."""
    console.print("\n[blue]Verifying setup...[/blue]")
    
    # Reload environment variables
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
    
    # Check configuration
    config_manager = AIConfigManager()
    setup_info = config_manager.validate_setup()
    
    if setup_info['has_ai_capability']:
        console.print("[green]✅ AI setup completed successfully![/green]")
        console.print(f"[green]Active provider: {setup_info['preferred_provider'].title()}[/green]")
        
        # Show next steps
        console.print("\n[cyan]Next Steps:[/cyan]")
        console.print("1. Run: python src/main.py --file your_code.py")
        console.print("2. Or try the demo: python demo.py")
        console.print("3. For help: python src/main.py --help")
    else:
        console.print("[red]❌ Setup verification failed. Please check your configuration.[/red]")

if __name__ == "__main__":
    main()