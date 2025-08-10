#!/usr/bin/env python3
"""
Demo script for IntegrationTestGenerator
"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.generators.integration_test_generator import IntegrationTestGenerator
from src.interfaces.base_interfaces import FunctionInfo, Parameter, Dependency, EdgeCase


def main():
    """Demonstrate the IntegrationTestGenerator functionality."""
    print("=== Integration Test Generator Demo ===\n")
    
    # Create sample function info
    sample_function = FunctionInfo(
        name="process_user_data",
        parameters=[
            Parameter(name="user_data", type_hint="dict"),
            Parameter(name="config", type_hint="dict", default_value=None)
        ],
        return_type="dict",
        complexity=8,
        line_range=(15, 45),
        docstring="Process user data with external dependencies including database and API calls"
    )
    
    # Create sample dependencies
    sample_dependencies = [
        Dependency(name="sqlite3", type="database", source="import sqlite3"),
        Dependency(name="requests", type="http_client", source="import requests"),
        Dependency(name="open", type="file_operation", source="with open('config.json') as f:"),
        Dependency(name="redis", type="database", source="import redis"),
        Dependency(name="external_api.authenticate", type="external_call", source="external_api.authenticate(token)")
    ]
    
    # Create sample edge cases
    sample_edge_cases = [
        EdgeCase(
            type="database_dependency",
            location="line 25",
            description="Database connection may fail or timeout",
            severity=3
        ),
        EdgeCase(
            type="network_dependency", 
            location="line 35",
            description="HTTP request may timeout or return error status",
            severity=2
        ),
        EdgeCase(
            type="file_dependency",
            location="line 20",
            description="Configuration file may not exist or be corrupted",
            severity=2
        )
    ]
    
    # Initialize the generator
    generator = IntegrationTestGenerator()
    
    # Test different languages
    languages = ["python", "javascript", "java"]
    
    for language in languages:
        print(f"=== {language.upper()} Integration Tests ===")
        
        # Generate comprehensive integration tests
        integration_tests = generator.generate_integration_tests(
            sample_function, sample_dependencies, language, sample_edge_cases
        )
        
        print(f"Generated {len(integration_tests)} integration test cases:")
        for i, test in enumerate(integration_tests, 1):
            print(f"\n{i}. {test.name}")
            print(f"   Description: {test.description}")
            print(f"   Type: {test.test_type.value}")
            print(f"   Requirements: {', '.join(test.requirements_covered)}")
            
            # Show a snippet of the test code
            code_lines = test.test_code.split('\n')
            print(f"   Code snippet (first 5 lines):")
            for line in code_lines[:5]:
                if line.strip():
                    print(f"     {line}")
            if len(code_lines) > 5:
                print(f"     ... ({len(code_lines) - 5} more lines)")
        
        print("\n" + "="*60 + "\n")
    
    # Demonstrate dependency injection tests
    print("=== Dependency Injection Tests ===")
    injection_tests = generator.generate_dependency_injection_tests(
        sample_function, sample_dependencies, "python"
    )
    
    print(f"Generated {len(injection_tests)} dependency injection test cases:")
    for i, test in enumerate(injection_tests, 1):
        print(f"\n{i}. {test.name}")
        print(f"   Description: {test.description}")
        
        # Show test code snippet
        code_lines = test.test_code.split('\n')
        print(f"   Code snippet:")
        for line in code_lines[:8]:
            if line.strip():
                print(f"     {line}")
        if len(code_lines) > 8:
            print(f"     ... ({len(code_lines) - 8} more lines)")
    
    print("\n" + "="*60 + "\n")
    
    # Demonstrate mock object tests
    print("=== Mock Object Tests ===")
    mock_tests = generator.generate_mock_object_tests(
        sample_function, sample_dependencies[:3], "python"  # Just first 3 dependencies
    )
    
    print(f"Generated {len(mock_tests)} mock object test cases:")
    for i, test in enumerate(mock_tests, 1):
        print(f"\n{i}. {test.name}")
        print(f"   Description: {test.description}")
        
        # Show test code snippet
        code_lines = test.test_code.split('\n')
        print(f"   Code snippet:")
        for line in code_lines[:10]:
            if line.strip():
                print(f"     {line}")
        if len(code_lines) > 10:
            print(f"     ... ({len(code_lines) - 10} more lines)")
    
    print("\n=== Demo Complete ===")
    print(f"Total integration tests generated: {len(integration_tests) * len(languages) + len(injection_tests) + len(mock_tests)}")


if __name__ == "__main__":
    main()