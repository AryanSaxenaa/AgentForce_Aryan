#!/usr/bin/env python3
"""
Demo script for CoverageAnalyzer functionality.
"""

from src.analyzers.coverage_analyzer import CoverageAnalyzer
from src.interfaces.base_interfaces import TestSuite, TestCase, TestType, Language


def demo_coverage_analysis():
    """Demonstrate coverage analysis capabilities."""
    print("=" * 60)
    print("Coverage Analyzer Demo")
    print("=" * 60)
    
    # Sample code to analyze
    sample_code = """def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def multiply(x, y):
    \"\"\"Multiply two numbers.\"\"\"
    result = x * y
    return result

def divide(x, y):
    \"\"\"Divide two numbers with error handling.\"\"\"
    if y == 0:
        raise ValueError("Division by zero")
    return x / y

def factorial(n):
    \"\"\"Calculate factorial recursively.\"\"\"
    if n <= 1:
        return 1
    return n * factorial(n - 1)
"""
    
    # Sample test cases (partial coverage)
    test_cases = [
        TestCase(
            name="test_add_positive_numbers",
            test_type=TestType.UNIT,
            function_name="add",
            description="Test adding positive numbers",
            test_code="assert add(2, 3) == 5"
        ),
        TestCase(
            name="test_add_negative_numbers",
            test_type=TestType.UNIT,
            function_name="add",
            description="Test adding negative numbers",
            test_code="assert add(-2, -3) == -5"
        ),
        TestCase(
            name="test_multiply_basic",
            test_type=TestType.UNIT,
            function_name="multiply",
            description="Test basic multiplication",
            test_code="assert multiply(3, 4) == 12"
        )
    ]
    
    test_suite = TestSuite(
        language=Language.PYTHON,
        framework="pytest",
        test_cases=test_cases
    )
    
    # Initialize analyzer
    analyzer = CoverageAnalyzer()
    
    print("Sample Code:")
    print("-" * 40)
    for i, line in enumerate(sample_code.split('\n'), 1):
        print(f"{i:2d}: {line}")
    
    print("\nTest Cases:")
    print("-" * 40)
    for i, test in enumerate(test_cases, 1):
        print(f"{i}. {test.name} -> {test.function_name}")
    
    # Perform coverage analysis
    print("\nPerforming Coverage Analysis...")
    print("-" * 40)
    
    coverage_report = analyzer.estimate_coverage(test_suite, sample_code)
    
    # Display results
    print(f"\nCoverage Results:")
    print(f"Overall Coverage: {coverage_report.overall_percentage:.1f}%")
    
    print(f"\nLine-by-Line Coverage:")
    for line_num, is_covered in coverage_report.line_coverage.items():
        status = "✓" if is_covered else "✗"
        print(f"  Line {line_num:2d}: {status}")
    
    print(f"\nUntested Functions:")
    if coverage_report.untested_functions:
        for func in coverage_report.untested_functions:
            print(f"  - {func}")
    else:
        print("  None - all functions have tests!")
    
    print(f"\nCoverage Gaps:")
    if coverage_report.coverage_gaps:
        for i, gap in enumerate(coverage_report.coverage_gaps, 1):
            print(f"  {i}. Function: {gap.function_name}")
            print(f"     Lines: {gap.line_range[0]}-{gap.line_range[1]}")
            print(f"     Issue: {gap.description}")
            print(f"     Suggestions:")
            for suggestion in gap.suggested_tests:
                print(f"       - {suggestion}")
            print()
    else:
        print("  No coverage gaps detected!")
    
    # Demonstrate gap identification
    print("Identifying Coverage Gaps...")
    print("-" * 40)
    gaps = analyzer.identify_gaps(coverage_report)
    print(f"Found {len(gaps)} coverage gaps")
    
    # Demonstrate test suggestions
    print("\nGenerating Test Suggestions...")
    print("-" * 40)
    suggested_tests = analyzer.suggest_additional_tests(gaps)
    
    if suggested_tests:
        print("Suggested Additional Tests:")
        for i, test in enumerate(suggested_tests, 1):
            print(f"{i}. {test.name}")
            print(f"   Function: {test.function_name}")
            print(f"   Description: {test.description}")
            print(f"   Test Code Preview:")
            print("   " + "\n   ".join(test.test_code.strip().split('\n')[:3]))
            print()
    else:
        print("No additional tests suggested - coverage is complete!")


def demo_language_support():
    """Demonstrate multi-language support."""
    print("\n" + "=" * 60)
    print("Multi-Language Support Demo")
    print("=" * 60)
    
    analyzer = CoverageAnalyzer()
    
    # Test different languages
    languages = {
        'python': """def calculate(x, y):
    if x > y:
        return x + y
    else:
        return x - y""",
        
        'java': """public class Calculator {
    public int calculate(int x, int y) {
        if (x > y) {
            return x + y;
        } else {
            return x - y;
        }
    }
}""",
        
        'javascript': """function calculate(x, y) {
    if (x > y) {
        return x + y;
    } else {
        return x - y;
    }
}"""
    }
    
    for lang, code in languages.items():
        print(f"\n{lang.upper()} Code Analysis:")
        print("-" * 30)
        
        lines = analyzer._parse_code_lines(code, lang)
        executable_lines = [l for l in lines if l.is_executable]
        
        print(f"Total lines: {len(lines)}")
        print(f"Executable lines: {len(executable_lines)}")
        print("Executable line details:")
        
        for line in executable_lines:
            print(f"  Line {line.line_number}: {line.content.strip()}")
            if line.function_name:
                print(f"    -> Function: {line.function_name}")


if __name__ == "__main__":
    demo_coverage_analysis()
    demo_language_support()
    
    print("\n" + "=" * 60)
    print("Coverage Analyzer Demo Complete!")
    print("=" * 60)