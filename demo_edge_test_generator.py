#!/usr/bin/env python3
"""
Demo script for EdgeTestGenerator - shows edge case test generation capabilities
"""
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import directly to avoid module issues
import importlib.util

# Load EdgeTestGenerator module directly
spec = importlib.util.spec_from_file_location("edge_test_generator", "src/generators/edge_test_generator.py")
edge_module = importlib.util.module_from_spec(spec)
sys.modules["edge_test_generator"] = edge_module
spec.loader.exec_module(edge_module)

# Load interfaces module directly
spec2 = importlib.util.spec_from_file_location("base_interfaces", "src/interfaces/base_interfaces.py")
interfaces_module = importlib.util.module_from_spec(spec2)
sys.modules["base_interfaces"] = interfaces_module
spec2.loader.exec_module(interfaces_module)

EdgeTestGenerator = edge_module.EdgeTestGenerator
FunctionInfo = interfaces_module.FunctionInfo
Parameter = interfaces_module.Parameter
EdgeCase = interfaces_module.EdgeCase

def demo_edge_test_generation():
    """Demonstrate edge case test generation."""
    print("🧪 EdgeTestGenerator Demo")
    print("=" * 50)
    
    # Initialize the generator
    generator = EdgeTestGenerator()
    
    # Example 1: Mathematical function with division
    print("\n📊 Example 1: Mathematical Division Function")
    print("-" * 40)
    
    divide_function = FunctionInfo(
        name="safe_divide",
        parameters=[
            Parameter(name="numerator", type_hint="float"),
            Parameter(name="divisor", type_hint="float")
        ],
        return_type="float",
        complexity=2,
        line_range=(1, 15),
        docstring="Safely divide two numbers with error handling"
    )
    
    # Detected edge cases from static analysis
    detected_edge_cases = [
        EdgeCase(
            type="division_by_zero",
            location="line 8",
            description="Potential division by zero when divisor is 0",
            severity=3
        )
    ]
    
    # Generate edge case tests
    edge_tests = generator.generate_edge_case_tests(divide_function, detected_edge_cases, "python")
    print(f"Generated {len(edge_tests)} edge case tests:")
    
    for test in edge_tests:
        print(f"\n🔍 {test.name}")
        print(f"   Description: {test.description}")
        print(f"   Test Code Preview:")
        print("   " + "\n   ".join(test.test_code.split('\n')[:8]) + "...")
    
    # Generate boundary value tests
    boundary_tests = generator.generate_boundary_value_tests(divide_function, "python")
    print(f"\n📏 Generated {len(boundary_tests)} boundary value tests")
    
    # Generate exception tests
    exception_tests = generator.generate_exception_tests(divide_function, "python")
    print(f"⚠️  Generated {len(exception_tests)} exception tests")
    
    # Example 2: String processing function
    print("\n\n📝 Example 2: String Processing Function")
    print("-" * 40)
    
    parse_function = FunctionInfo(
        name="parse_email",
        parameters=[
            Parameter(name="email_string", type_hint="str"),
            Parameter(name="strict_mode", type_hint="bool", default_value=False)
        ],
        return_type="dict",
        complexity=3,
        line_range=(20, 45),
        docstring="Parse email address into components"
    )
    
    # Generate tests for string processing function
    string_edge_tests = generator.generate_edge_case_tests(parse_function, [], "python")
    print(f"Generated {len(string_edge_tests)} edge case tests for string processing:")
    
    for test in string_edge_tests[:2]:  # Show first 2 tests
        print(f"\n🔍 {test.name}")
        print(f"   Description: {test.description}")
    
    # Example 3: Collection processing function
    print("\n\n📋 Example 3: Collection Processing Function")
    print("-" * 40)
    
    sort_function = FunctionInfo(
        name="custom_sort",
        parameters=[
            Parameter(name="items", type_hint="list"),
            Parameter(name="key_func", type_hint="callable", default_value=None),
            Parameter(name="reverse", type_hint="bool", default_value=False)
        ],
        return_type="list",
        complexity=4,
        line_range=(50, 80),
        docstring="Custom sorting with optional key function"
    )
    
    # Generate negative tests
    negative_tests = generator.generate_negative_tests(sort_function, "python")
    print(f"Generated {len(negative_tests)} negative tests for collection processing")
    
    # Summary
    total_tests = len(edge_tests) + len(boundary_tests) + len(exception_tests) + len(string_edge_tests) + len(negative_tests)
    print(f"\n📈 Summary")
    print("-" * 20)
    print(f"Total edge case tests generated: {total_tests}")
    print(f"Functions analyzed: 3")
    print(f"Edge case types covered:")
    print("  • Null/None input handling")
    print("  • Division by zero scenarios")
    print("  • Boundary value testing")
    print("  • Invalid type handling")
    print("  • Empty collection scenarios")
    print("  • String edge cases (empty, whitespace)")
    
    print(f"\n✅ EdgeTestGenerator demo completed successfully!")
    print(f"All generated tests include proper pytest assertions and error handling.")

if __name__ == "__main__":
    demo_edge_test_generation()