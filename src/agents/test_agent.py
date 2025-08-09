"""
Test Generator Agent - AI-powered test case generation and refinement
"""
import os
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.panel import Panel

from analyzers.code_analyzer import CodeAnalyzer, AnalysisResult
from generators.test_generator import TestGenerator, TestCase
from config.ai_config import AIConfigManager

console = Console()

class TestGeneratorAgent:
    """AI agent that orchestrates code analysis and test generation."""
    
    def __init__(self, analyzer: CodeAnalyzer, generator: TestGenerator):
        self.analyzer = analyzer
        self.generator = generator
        self.current_analysis: Optional[AnalysisResult] = None
        self.current_tests: List[TestCase] = []
        self.ai_config = AIConfigManager()
        self.ai_client = self._initialize_ai_client()
    
    def _initialize_ai_client(self):
        """Initialize AI client based on configuration and available API keys."""
        setup_info = self.ai_config.validate_setup()
        provider = setup_info['preferred_provider']
        
        if provider == 'openai':
            api_key = self.ai_config.get_api_key('openai')
            console.print(f"[blue]Using OpenAI {self.ai_config.config.openai_model} for test enhancement[/blue]")
            return OpenAIClient(api_key, self.ai_config.config)
        elif provider == 'anthropic':
            api_key = self.ai_config.get_api_key('anthropic')
            console.print(f"[blue]Using Anthropic {self.ai_config.config.anthropic_model} for test enhancement[/blue]")
            return AnthropicClient(api_key, self.ai_config.config)
        else:
            console.print("[yellow]No AI API key found. Using mock client for demonstration.[/yellow]")
            for recommendation in setup_info['recommendations']:
                console.print(f"[yellow]💡 {recommendation}[/yellow]")
            return MockAIClient()
    
    def process_file(self, file_path: str, language: Optional[str] = None, output_dir: Optional[str] = None) -> Dict[str, Any]:
        """Process a code file and generate comprehensive test cases."""
        
        # Step 1: Analyze the code
        console.print("[yellow]🔍 Analyzing code structure and flow...[/yellow]")
        self.current_analysis = self.analyzer.analyze_file(file_path, language)
        
        # Step 2: Display analysis results
        self._display_analysis_summary()
        
        # Step 3: Generate initial test cases
        console.print("[yellow]🧪 Generating test cases...[/yellow]")
        self.current_tests = self.generator.generate_tests(self.current_analysis)
        
        # Step 4: Enhance tests with AI insights
        console.print("[yellow]🤖 Enhancing tests with AI insights...[/yellow]")
        self._enhance_tests_with_ai()
        
        # Step 5: Generate coverage report
        coverage_percentage = self._calculate_coverage()
        
        # Step 6: Save generated tests
        if output_dir:
            self._save_tests(output_dir)
        
        return {
            'test_count': len(self.current_tests),
            'coverage_percentage': coverage_percentage,
            'analysis': self.current_analysis,
            'tests': self.current_tests
        }
    
    def _display_analysis_summary(self):
        """Display code analysis summary."""
        if not self.current_analysis:
            return
        
        # Create analysis summary table
        table = Table(title="Code Analysis Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Language", self.current_analysis.language)
        table.add_row("Functions Found", str(len(self.current_analysis.functions)))
        table.add_row("Classes Found", str(len(self.current_analysis.classes)))
        table.add_row("Complexity Score", str(self.current_analysis.complexity_score))
        table.add_row("Edge Cases Detected", str(len(self.current_analysis.edge_cases)))
        table.add_row("Performance Risks", str(len(self.current_analysis.performance_risks)))
        
        console.print(table)
        
        # Display detected issues
        if self.current_analysis.edge_cases:
            console.print("\n[yellow]⚠️  Detected Edge Cases:[/yellow]")
            for edge_case in self.current_analysis.edge_cases:
                console.print(f"  • {edge_case}")
        
        if self.current_analysis.performance_risks:
            console.print("\n[red]🚨 Performance Risks:[/red]")
            for risk in self.current_analysis.performance_risks:
                console.print(f"  • {risk}")
    
    def _enhance_tests_with_ai(self):
        """Use AI to enhance generated test cases."""
        if not self.current_analysis or not self.current_tests:
            return
        
        # Prepare context for AI
        context = self._prepare_ai_context()
        
        # Get AI suggestions for each test
        for test in self.current_tests:
            enhanced_test = self.ai_client.enhance_test_case(test, context)
            if enhanced_test:
                test.test_code = enhanced_test.get('code', test.test_code)
                test.description = enhanced_test.get('description', test.description)
                if enhanced_test.get('assertions'):
                    test.assertions = enhanced_test['assertions']
    
    def _prepare_ai_context(self) -> Dict[str, Any]:
        """Prepare context for AI enhancement."""
        return {
            'language': self.current_analysis.language,
            'functions': [
                {
                    'name': f.name,
                    'args': f.args,
                    'complexity': f.complexity,
                    'docstring': f.docstring
                }
                for f in self.current_analysis.functions
            ],
            'edge_cases': self.current_analysis.edge_cases,
            'performance_risks': self.current_analysis.performance_risks,
            'imports': self.current_analysis.imports
        }
    
    def _calculate_coverage(self) -> float:
        """Calculate estimated test coverage."""
        if not self.current_analysis or not self.current_tests:
            return 0.0
        
        total_functions = len(self.current_analysis.functions)
        if total_functions == 0:
            return 100.0
        
        covered_functions = set()
        for test in self.current_tests:
            covered_functions.add(test.function_name)
        
        return (len(covered_functions) / total_functions) * 100
    
    def _save_tests(self, output_dir: str):
        """Save generated tests to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Group tests by function
        tests_by_function = {}
        for test in self.current_tests:
            if test.function_name not in tests_by_function:
                tests_by_function[test.function_name] = []
            tests_by_function[test.function_name].append(test)
        
        # Generate test files
        for function_name, tests in tests_by_function.items():
            filename = f"test_{function_name}.{self._get_test_file_extension()}"
            filepath = output_path / filename
            
            with open(filepath, 'w') as f:
                f.write(self._generate_test_file_header())
                for test in tests:
                    f.write(f"\n{test.test_code}\n")
            
            console.print(f"[green]✓ Generated {filepath}[/green]")
    
    def _get_test_file_extension(self) -> str:
        """Get appropriate test file extension."""
        extensions = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'java': 'java'
        }
        return extensions.get(self.current_analysis.language, 'txt')
    
    def _generate_test_file_header(self) -> str:
        """Generate test file header."""
        if self.current_analysis.language == 'python':
            return """import pytest
import unittest
from unittest.mock import Mock, patch

# Generated test cases
"""
        elif self.current_analysis.language in ['javascript', 'typescript']:
            return """const { describe, test, expect, beforeEach, afterEach } = require('@jest/globals');

// Generated test cases
"""
        elif self.current_analysis.language == 'java':
            return """import org.junit.Test;
import org.junit.Before;
import org.junit.After;
import static org.junit.Assert.*;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;

// Generated test cases
"""
        return "// Generated test cases\n"
    
    def interactive_refinement(self):
        """Interactive mode for test case refinement."""
        if not self.current_tests:
            console.print("[red]No tests available for refinement[/red]")
            return
        
        console.print(Panel.fit(
            "[bold blue]Interactive Test Refinement[/bold blue]\n"
            "Review and refine your generated test cases",
            border_style="blue"
        ))
        
        while True:
            # Display current tests
            self._display_test_summary()
            
            # Get user choice
            choice = Prompt.ask(
                "\nWhat would you like to do?",
                choices=["view", "edit", "add", "remove", "enhance", "save", "quit"],
                default="quit"
            )
            
            if choice == "view":
                self._view_test_details()
            elif choice == "edit":
                self._edit_test()
            elif choice == "add":
                self._add_custom_test()
            elif choice == "remove":
                self._remove_test()
            elif choice == "enhance":
                self._enhance_specific_test()
            elif choice == "save":
                output_dir = Prompt.ask("Output directory", default="./tests")
                self._save_tests(output_dir)
            elif choice == "quit":
                break
    
    def _display_test_summary(self):
        """Display summary of current tests."""
        table = Table(title="Generated Test Cases")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Function", style="blue")
        
        for i, test in enumerate(self.current_tests):
            table.add_row(
                str(i + 1),
                test.name,
                test.test_type,
                test.function_name
            )
        
        console.print(table)
    
    def _view_test_details(self):
        """View details of a specific test."""
        test_id = Prompt.ask("Enter test ID to view")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                test = self.current_tests[test_index]
                console.print(Panel(
                    f"[bold]{test.name}[/bold]\n\n"
                    f"Type: {test.test_type}\n"
                    f"Function: {test.function_name}\n"
                    f"Description: {test.description}\n\n"
                    f"[yellow]Code:[/yellow]\n{test.test_code}",
                    title="Test Details"
                ))
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    def _edit_test(self):
        """Edit a specific test case."""
        test_id = Prompt.ask("Enter test ID to edit")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                test = self.current_tests[test_index]
                
                # Show current test
                console.print(f"[yellow]Current test:[/yellow]\n{test.test_code}")
                
                # Get AI suggestions for improvement
                suggestions = self.ai_client.suggest_test_improvements(test, self._prepare_ai_context())
                if suggestions:
                    console.print(f"[blue]AI Suggestions:[/blue]\n{suggestions}")
                
                # Allow manual editing
                if Confirm.ask("Would you like to manually edit this test?"):
                    console.print("[yellow]Enter new test code (press Ctrl+D when done):[/yellow]")
                    new_code = ""
                    try:
                        while True:
                            line = input()
                            new_code += line + "\n"
                    except EOFError:
                        pass
                    
                    if new_code.strip():
                        test.test_code = new_code.strip()
                        console.print("[green]✓ Test updated[/green]")
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    def _add_custom_test(self):
        """Add a custom test case."""
        console.print("[yellow]Adding custom test case...[/yellow]")
        
        name = Prompt.ask("Test name")
        test_type = Prompt.ask("Test type", choices=["unit", "integration", "edge"], default="unit")
        function_name = Prompt.ask("Function name")
        description = Prompt.ask("Description")
        
        console.print("[yellow]Enter test code (press Ctrl+D when done):[/yellow]")
        test_code = ""
        try:
            while True:
                line = input()
                test_code += line + "\n"
        except EOFError:
            pass
        
        if test_code.strip():
            custom_test = TestCase(
                name=name,
                test_type=test_type,
                function_name=function_name,
                description=description,
                test_code=test_code.strip()
            )
            self.current_tests.append(custom_test)
            console.print("[green]✓ Custom test added[/green]")
    
    def _remove_test(self):
        """Remove a test case."""
        test_id = Prompt.ask("Enter test ID to remove")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                removed_test = self.current_tests.pop(test_index)
                console.print(f"[green]✓ Removed test: {removed_test.name}[/green]")
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")
    
    def _enhance_specific_test(self):
        """Enhance a specific test with AI."""
        test_id = Prompt.ask("Enter test ID to enhance")
        try:
            test_index = int(test_id) - 1
            if 0 <= test_index < len(self.current_tests):
                test = self.current_tests[test_index]
                console.print(f"[yellow]Enhancing test: {test.name}...[/yellow]")
                
                enhanced = self.ai_client.enhance_test_case(test, self._prepare_ai_context())
                if enhanced:
                    test.test_code = enhanced.get('code', test.test_code)
                    test.description = enhanced.get('description', test.description)
                    console.print("[green]✓ Test enhanced[/green]")
                else:
                    console.print("[yellow]No enhancements suggested[/yellow]")
            else:
                console.print("[red]Invalid test ID[/red]")
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


class OpenAIClient:
    """OpenAI API client for test enhancement."""
    
    def __init__(self, api_key: str, config):
        try:
            import openai
            self.client = openai.OpenAI(
                api_key=api_key,
                timeout=config.timeout
            )
            self.model = config.openai_model
            self.max_tokens = config.max_tokens
            self.temperature = config.temperature
        except ImportError:
            console.print("[red]Error: openai package not installed. Run: pip install openai[/red]")
            raise
    
    def enhance_test_case(self, test: TestCase, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enhance test case using OpenAI API."""
        try:
            prompt = self._create_enhancement_prompt(test, context)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software testing engineer. Enhance the provided test case to make it more comprehensive, realistic, and maintainable."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            enhanced_content = response.choices[0].message.content
            return self._parse_enhancement_response(enhanced_content, test)
            
        except Exception as e:
            console.print(f"[yellow]Warning: OpenAI API error: {e}[/yellow]")
            return None
    
    def suggest_test_improvements(self, test: TestCase, context: Dict[str, Any]) -> str:
        """Get test improvement suggestions from OpenAI."""
        try:
            prompt = f"""
Analyze this test case and provide specific improvement suggestions:

Test Name: {test.name}
Test Type: {test.test_type}
Function: {test.function_name}
Language: {context['language']}

Current Test Code:
{test.test_code}

Context:
- Domain: {context.get('functions', [{}])[0].get('complexity', 'unknown')}
- Edge Cases: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Provide 3-5 specific, actionable improvement suggestions.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert software testing engineer. Provide specific, actionable suggestions for improving test cases."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=min(500, self.max_tokens),
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            console.print(f"[yellow]Warning: OpenAI API error: {e}[/yellow]")
            return "Unable to get AI suggestions at this time."
    
    def _create_enhancement_prompt(self, test: TestCase, context: Dict[str, Any]) -> str:
        """Create prompt for test enhancement."""
        return f"""
Enhance this {context['language']} test case to make it more comprehensive and realistic:

Test Name: {test.name}
Test Type: {test.test_type}
Function: {test.function_name}
Description: {test.description}

Current Test Code:
{test.test_code}

Context Information:
- Language: {context['language']}
- Function Domain: {context.get('functions', [{}])[0].get('name', 'unknown')}
- Detected Edge Cases: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Please enhance this test by:
1. Adding more specific and meaningful assertions
2. Using realistic test data
3. Adding proper error handling expectations
4. Including setup/teardown if needed
5. Adding clear comments explaining the test logic

Return the enhanced test code and a brief description of improvements made.
Format your response as:
ENHANCED_CODE:
[enhanced test code here]

DESCRIPTION:
[brief description of improvements]

ASSERTIONS:
[list of key assertions to verify]
"""
    
    def _parse_enhancement_response(self, response: str, original_test: TestCase) -> Dict[str, Any]:
        """Parse OpenAI response into structured enhancement data."""
        try:
            parts = response.split('ENHANCED_CODE:')
            if len(parts) < 2:
                return None
            
            code_and_rest = parts[1].split('DESCRIPTION:')
            enhanced_code = code_and_rest[0].strip()
            
            description = original_test.description
            assertions = []
            
            if len(code_and_rest) > 1:
                desc_and_rest = code_and_rest[1].split('ASSERTIONS:')
                description = desc_and_rest[0].strip()
                
                if len(desc_and_rest) > 1:
                    assertions_text = desc_and_rest[1].strip()
                    assertions = [line.strip('- ').strip() for line in assertions_text.split('\n') if line.strip()]
            
            return {
                'code': enhanced_code,
                'description': description,
                'assertions': assertions
            }
            
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to parse OpenAI response: {e}[/yellow]")
            return None


class AnthropicClient:
    """Anthropic Claude API client for test enhancement."""
    
    def __init__(self, api_key: str, config):
        try:
            import anthropic
            self.client = anthropic.Anthropic(
                api_key=api_key,
                timeout=config.timeout
            )
            self.model = config.anthropic_model
            self.max_tokens = config.max_tokens
            self.temperature = config.temperature
        except ImportError:
            console.print("[red]Error: anthropic package not installed. Run: pip install anthropic[/red]")
            raise
    
    def enhance_test_case(self, test: TestCase, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Enhance test case using Anthropic Claude API."""
        try:
            prompt = self._create_enhancement_prompt(test, context)
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            enhanced_content = response.content[0].text
            return self._parse_enhancement_response(enhanced_content, test)
            
        except Exception as e:
            console.print(f"[yellow]Warning: Anthropic API error: {e}[/yellow]")
            return None
    
    def suggest_test_improvements(self, test: TestCase, context: Dict[str, Any]) -> str:
        """Get test improvement suggestions from Anthropic Claude."""
        try:
            prompt = f"""
As an expert software testing engineer, analyze this test case and provide specific improvement suggestions:

Test Details:
- Name: {test.name}
- Type: {test.test_type}
- Function: {test.function_name}
- Language: {context['language']}

Current Test Code:
{test.test_code}

Context Information:
- Edge Cases Detected: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Please provide 3-5 specific, actionable suggestions to improve this test case. Focus on:
- Test completeness and coverage
- Assertion quality and specificity
- Edge case handling
- Code maintainability
- Best practices for the language/framework
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=min(500, self.max_tokens),
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            console.print(f"[yellow]Warning: Anthropic API error: {e}[/yellow]")
            return "Unable to get AI suggestions at this time."
    
    def _create_enhancement_prompt(self, test: TestCase, context: Dict[str, Any]) -> str:
        """Create prompt for test enhancement."""
        return f"""
As an expert software testing engineer, please enhance this {context['language']} test case:

Current Test:
Name: {test.name}
Type: {test.test_type}
Function: {test.function_name}
Description: {test.description}

Code:
{test.test_code}

Context:
- Language: {context['language']}
- Detected Edge Cases: {context.get('edge_cases', [])}
- Performance Risks: {context.get('performance_risks', [])}

Please enhance this test by:
1. Adding more specific and meaningful assertions
2. Using realistic, domain-appropriate test data
3. Adding proper error handling expectations
4. Including necessary setup/teardown
5. Adding clear, helpful comments

Please format your response as:

ENHANCED_CODE:
[Your enhanced test code here]

DESCRIPTION:
[Brief description of the improvements you made]

ASSERTIONS:
[List the key assertions that should be verified]
"""
    
    def _parse_enhancement_response(self, response: str, original_test: TestCase) -> Dict[str, Any]:
        """Parse Anthropic response into structured enhancement data."""
        try:
            parts = response.split('ENHANCED_CODE:')
            if len(parts) < 2:
                return None
            
            code_and_rest = parts[1].split('DESCRIPTION:')
            enhanced_code = code_and_rest[0].strip()
            
            description = original_test.description
            assertions = []
            
            if len(code_and_rest) > 1:
                desc_and_rest = code_and_rest[1].split('ASSERTIONS:')
                description = desc_and_rest[0].strip()
                
                if len(desc_and_rest) > 1:
                    assertions_text = desc_and_rest[1].strip()
                    assertions = [line.strip('- ').strip() for line in assertions_text.split('\n') if line.strip()]
            
            return {
                'code': enhanced_code,
                'description': description,
                'assertions': assertions
            }
            
        except Exception as e:
            console.print(f"[yellow]Warning: Failed to parse Anthropic response: {e}[/yellow]")
            return None


class MockAIClient:
    """Mock AI client for demonstration when no API key is available."""
    
    def enhance_test_case(self, test: TestCase, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Mock enhancement of test cases."""
        enhancements = {
            'code': test.test_code,
            'description': f"Enhanced: {test.description}",
            'assertions': [
                "assert result is not None",
                "assert isinstance(result, expected_type)",
                "assert result meets expected criteria"
            ]
        }
        
        # Add language-specific improvements
        if context['language'] == 'python':
            if 'pytest.raises' not in test.test_code and test.test_type == 'edge':
                enhancements['code'] = test.test_code.replace(
                    '# Assert',
                    '# Assert\n    # Consider using pytest.raises for exception testing'
                )
        
        return enhancements
    
    def suggest_test_improvements(self, test: TestCase, context: Dict[str, Any]) -> str:
        """Mock test improvement suggestions."""
        suggestions = [
            "Consider adding more specific assertions",
            "Add setup and teardown if needed", 
            "Test boundary conditions",
            "Add documentation for test purpose",
            "Consider parameterized tests for multiple inputs",
            "Set OPENAI_API_KEY or ANTHROPIC_API_KEY for AI-powered suggestions"
        ]
        
        return "\n".join(f"• {suggestion}" for suggestion in suggestions)