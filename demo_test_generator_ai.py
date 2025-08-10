#!/usr/bin/env python3
"""
Demo script for AI-integrated Test Generator
"""
import os
import sys
from typing import List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.test_generator import TestGenerator
from src.interfaces.base_interfaces import (
    FunctionInfo, Parameter, EdgeCase, Language, TestType
)
from src.config.ai_provider_manager import AIProviderManager


class MockAnalysisResult:
    """Mock analysis result for demo."""
    def __init__(self, language='python', functions=None, edge_cases=None, imports=None):
        self.language = language
        self.functions = functions or []
        self.edge_cases = edge_cases or []
        self.imports = imports or []


def create_sample_functions() -> List[FunctionInfo]:
    """Create sample functions for demonstration."""
    functions = [
        FunctionInfo(
            name="calculate_average",
            parameters=[
                Parameter(name="numbers", type_hint="List[float]"),
                Parameter(name="exclude_zeros", type_hint="bool", default_value=False)
            ],
            return_type="float",
            complexity=3,
            line_range=(1, 10),
            docstring="Calculate the average of a list of numbers with optional zero exclusion"
        ),
        FunctionInfo(
            name="validate_email",
            parameters=[
                Parameter(name="email", type_hint="str"),
                Parameter(name="strict_mode", type_hint="bool", default_value=True)
            ],
            return_type="bool",
            complexity=5,
            line_range=(12, 25),
            docstring="Validate email address format with optional strict mode"
        ),
        FunctionInfo(
            name="fibonacci",
            parameters=[
                Parameter(name="n", type_hint="int")
            ],
            return_type="int",
            complexity=8,
            line_range=(27, 35),
            docstring="Calculate the nth Fibonacci number using recursion"
        )
    ]
    return functions


def create_sample_edge_cases() -> List[EdgeCase]:
    """Create sample edge cases for demonstration."""
    edge_cases = [
        EdgeCase(
            type="null_check",
            location="line 5",
            description="Division by zero when calculating average",
            severity=4
        ),
        EdgeCase(
            type="boundary_condition",
            location="line 15",
            description="Empty email string validation",
            severity=3
        ),
        EdgeCase(
            type="performance_risk",
            location="line 30",
            description="Large fibonacci numbers causing stack overflow",
            severity=5
        )
    ]
    return edge_cases


def demo_basic_test_generation():
    """Demonstrate basic test generation without AI."""
    print("=" * 60)
    print("DEMO: Basic Test Generation (No AI Enhancement)")
    print("=" * 60)
    
    # Create test generator with mock AI provider
    generator = TestGenerator()
    
    # Create sample analysis
    functions = create_sample_functions()
    edge_cases = create_sample_edge_cases()
    analysis = MockAnalysisResult(
        language='python',
        functions=functions[:1],  # Just one function for demo
        edge_cases=edge_cases[:1],
        imports=['import math', 'from typing import List']
    )
    
    # Generate tests
    test_suite = generator.generate_tests(analysis)
    
    print(f"Generated {len(test_suite.test_cases)} test cases")
    print(f"Framework: {test_suite.framework}")
    print(f"Language: {test_suite.language.value}")
    print("\nSample Test Case:")
    print("-" * 40)
    if test_suite.test_cases:
        sample_test = test_suite.test_cases[0]
        print(f"Name: {sample_test.name}")
        print(f"Type: {sample_test.test_type.value}")
        print(f"Description: {sample_test.description}")
        print("\nTest Code:")
        print(sample_test.test_code[:300] + "..." if len(sample_test.test_code) > 300 else sample_test.test_code)


def demo_ai_enhanced_generation():
    """Demonstrate AI-enhanced test generation."""
    print("\n" + "=" * 60)
    print("DEMO: AI-Enhanced Test Generation")
    print("=" * 60)
    
    # Check if AI providers are available
    ai_manager = AIProviderManager()
    provider_info = ai_manager.get_provider_info()
    
    print(f"Current AI Provider: {provider_info['current_provider']}")
    print(f"Has AI Capability: {provider_info['has_ai_capability']}")
    
    if not provider_info['has_ai_capability']:
        print("\nNote: No AI API keys detected. Using mock provider for demonstration.")
        print("Set OPENAI_API_KEY or ANTHROPIC_API_KEY environment variables for full AI features.")
    
    # Create test generator
    generator = TestGenerator(ai_manager)
    
    # Create more complex analysis
    functions = create_sample_functions()
    edge_cases = create_sample_edge_cases()
    analysis = MockAnalysisResult(
        language='python',
        functions=functions,
        edge_cases=edge_cases,
        imports=['import math', 'import re', 'from typing import List, Optional']
    )
    
    # Generate AI-enhanced tests
    print("\nGenerating AI-enhanced test suite...")
    test_suite = generator.generate_tests(analysis)
    
    print(f"\nGenerated {len(test_suite.test_cases)} test cases with AI enhancement")
    
    # Show test breakdown by type
    unit_tests = [t for t in test_suite.test_cases if t.test_type == TestType.UNIT]
    edge_tests = [t for t in test_suite.test_cases if t.test_type == TestType.EDGE]
    integration_tests = [t for t in test_suite.test_cases if t.test_type == TestType.INTEGRATION]
    
    print(f"- Unit tests: {len(unit_tests)}")
    print(f"- Edge case tests: {len(edge_tests)}")
    print(f"- Integration tests: {len(integration_tests)}")
    
    # Show sample enhanced test
    if test_suite.test_cases:
        print("\nSample AI-Enhanced Test:")
        print("-" * 40)
        sample_test = test_suite.test_cases[0]
        print(f"Name: {sample_test.name}")
        print(f"Description: {sample_test.description}")
        print("\nEnhanced Test Code:")
        print(sample_test.test_code[:400] + "..." if len(sample_test.test_code) > 400 else sample_test.test_code)


def demo_language_specific_formatting():
    """Demonstrate language-specific test formatting."""
    print("\n" + "=" * 60)
    print("DEMO: Language-Specific Test Formatting")
    print("=" * 60)
    
    generator = TestGenerator()
    
    # Create a simple test case
    from src.interfaces.base_interfaces import TestCase
    sample_test = TestCase(
        name="test_example_function",
        test_type=TestType.UNIT,
        function_name="example_function",
        description="Test example function with various inputs",
        test_code="def test_example_function():\n    assert example_function(5) == 10",
        requirements_covered=[]
    )
    
    # Format for different languages
    languages = [Language.PYTHON, Language.JAVASCRIPT, Language.JAVA]
    
    for language in languages:
        print(f"\n{language.value.upper()} Test Format:")
        print("-" * 30)
        formatted = generator.format_tests([sample_test], language)
        print(formatted[:300] + "..." if len(formatted) > 300 else formatted)


def demo_ai_provider_capabilities():
    """Demonstrate AI provider capabilities."""
    print("\n" + "=" * 60)
    print("DEMO: AI Provider Capabilities")
    print("=" * 60)
    
    ai_manager = AIProviderManager()
    
    # Test all providers
    print("Testing AI provider connections...")
    health_status = ai_manager.test_all_providers()
    
    for provider, is_healthy in health_status.items():
        status = "✓ Working" if is_healthy else "✗ Not available"
        print(f"- {provider.capitalize()}: {status}")
    
    # Get recommendations
    recommendations = ai_manager.get_fallback_recommendations()
    if recommendations:
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"- {rec}")
    
    # Show current provider info
    provider_info = ai_manager.get_provider_info()
    print(f"\nCurrent Configuration:")
    print(f"- Active Provider: {provider_info['current_provider']}")
    print(f"- Available Providers: {list(provider_info['available_providers'].keys())}")
    print(f"- Fallback Order: {provider_info['fallback_order']}")


def main():
    """Run all demonstrations."""
    print("AI-Integrated Test Generator Demo")
    print("=" * 60)
    
    try:
        # Run demonstrations
        demo_basic_test_generation()
        demo_ai_enhanced_generation()
        demo_language_specific_formatting()
        demo_ai_provider_capabilities()
        
        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())