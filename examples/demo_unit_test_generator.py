#!/usr/bin/env python3
"""
Demo script for UnitTestGenerator - Shows unit test generation capabilities
"""

from src.generators.unit_test_generator import UnitTestGenerator
from src.interfaces.base_interfaces import FunctionInfo, Parameter

def main():
    """Demonstrate the UnitTestGenerator functionality."""
    print("=== Unit Test Generator Demo ===\n")
    
    # Initialize the generator
    generator = UnitTestGenerator()
    
    # Example 1: Simple mathematical function
    print("1. Testing a simple mathematical function:")
    math_function = FunctionInfo(
        name="calculate_area",
        parameters=[
            Parameter(name="width", type_hint="float", default_value=None),
            Parameter(name="height", type_hint="float", default_value=None)
        ],
        return_type="float",
        complexity=1,
        line_range=(1, 3),
        docstring="Calculate the area of a rectangle"
    )
    
    # Generate unit tests for Python
    python_tests = generator.generate_unit_tests(math_function, "python")
    print(f"Generated {len(python_tests)} Python test cases:")
    for i, test in enumerate(python_tests[:2], 1):  # Show first 2 tests
        print(f"\nTest {i}: {test.name}")
        print(f"Description: {test.description}")
        print("Code:")
        print(test.test_code)
        print("-" * 50)
    
    # Example 2: Function with edge cases
    print("\n2. Testing a function prone to edge cases:")
    edge_function = FunctionInfo(
        name="divide_numbers",
        parameters=[
            Parameter(name="numerator", type_hint="float"),
            Parameter(name="denominator", type_hint="float")
        ],
        return_type="float",
        complexity=2,
        line_range=(1, 5),
        docstring="Divide two numbers with error handling"
    )
    
    # Generate edge case tests
    edge_tests = generator.generate_edge_case_tests(edge_function, "python")
    print(f"Generated {len(edge_tests)} edge case tests:")
    for i, test in enumerate(edge_tests[:2], 1):  # Show first 2 edge tests
        print(f"\nEdge Test {i}: {test.name}")
        print(f"Description: {test.description}")
        print("Code:")
        print(test.test_code)
        print("-" * 50)
    
    # Example 3: JavaScript function
    print("\n3. Testing JavaScript function generation:")
    js_function = FunctionInfo(
        name="validateEmail",
        parameters=[
            Parameter(name="email", type_hint="string")
        ],
        return_type="boolean",
        complexity=3,
        line_range=(1, 10),
        docstring="Validate email address format"
    )
    
    js_tests = generator.generate_unit_tests(js_function, "javascript")
    print(f"Generated {len(js_tests)} JavaScript test cases:")
    for i, test in enumerate(js_tests[:1], 1):  # Show first test
        print(f"\nJS Test {i}: {test.name}")
        print(f"Description: {test.description}")
        print("Code:")
        print(test.test_code)
        print("-" * 50)
    
    # Example 4: Parameter variations
    print("\n4. Testing parameter variations:")
    param_function = FunctionInfo(
        name="process_data",
        parameters=[
            Parameter(name="data", type_hint="list"),
            Parameter(name="filter_empty", type_hint="bool", default_value=True),
            Parameter(name="sort_order", type_hint="str", default_value="asc")
        ],
        return_type="list",
        complexity=4,
        line_range=(1, 15)
    )
    
    param_tests = generator.generate_parameter_variations(param_function, "python")
    print(f"Generated {len(param_tests)} parameter variation tests:")
    for i, test in enumerate(param_tests[:2], 1):  # Show first 2 tests
        print(f"\nParam Test {i}: {test.name}")
        print(f"Description: {test.description}")
        print("Code snippet:")
        print(test.test_code[:200] + "..." if len(test.test_code) > 200 else test.test_code)
        print("-" * 50)
    
    print("\n=== Demo Complete ===")
    print(f"Total tests generated across all examples: {len(python_tests) + len(edge_tests) + len(js_tests) + len(param_tests)}")

if __name__ == "__main__":
    main()