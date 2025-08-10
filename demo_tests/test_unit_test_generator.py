"""
Unit tests for UnitTestGenerator - Tests unit test generation across languages
"""
import pytest
from unittest.mock import Mock, patch
from src.generators.unit_test_generator import UnitTestGenerator, TestDataGenerator, AssertionGenerator
from src.interfaces.base_interfaces import FunctionInfo, Parameter, TestCase, TestType


class TestUnitTestGenerator:
    """Test the UnitTestGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = UnitTestGenerator()
    
    def test_init(self):
        """Test UnitTestGenerator initialization."""
        assert self.generator is not None
        assert isinstance(self.generator.test_data_generator, TestDataGenerator)
        assert isinstance(self.generator.assertion_generator, AssertionGenerator)
        assert "python" in self.generator.templates
        assert "javascript" in self.generator.templates
        assert "java" in self.generator.templates
    
    def test_generate_unit_tests_simple_function(self):
        """Test generating unit tests for a simple function."""
        # Create a simple function info
        function_info = FunctionInfo(
            name="add_numbers",
            parameters=[
                Parameter(name="a", type_hint="int"),
                Parameter(name="b", type_hint="int")
            ],
            return_type="int",
            complexity=1,
            line_range=(1, 3)
        )
        
        # Generate tests
        test_cases = self.generator.generate_unit_tests(function_info, "python")
        
        # Verify results
        assert len(test_cases) > 0
        assert all(isinstance(test, TestCase) for test in test_cases)
        assert all(test.test_type == TestType.UNIT for test in test_cases)
        assert all(test.function_name == "add_numbers" for test in test_cases)
    
    def test_generate_unit_tests_no_parameters(self):
        """Test generating unit tests for a function with no parameters."""
        function_info = FunctionInfo(
            name="get_current_time",
            parameters=[],
            return_type="str",
            complexity=1,
            line_range=(1, 2)
        )
        
        test_cases = self.generator.generate_unit_tests(function_info, "python")
        
        assert len(test_cases) > 0
        assert "basic" in test_cases[0].name
    
    def test_generate_parameter_variations(self):
        """Test generating parameter variation tests."""
        function_info = FunctionInfo(
            name="calculate_area",
            parameters=[
                Parameter(name="width", type_hint="float"),
                Parameter(name="height", type_hint="float")
            ],
            return_type="float",
            complexity=1,
            line_range=(1, 3)
        )
        
        test_cases = self.generator.generate_parameter_variations(function_info, "python")
        
        assert len(test_cases) > 0
        assert any("param_width" in test.name for test in test_cases)
        assert any("param_height" in test.name for test in test_cases)
    
    def test_generate_edge_case_tests(self):
        """Test generating edge case tests."""
        function_info = FunctionInfo(
            name="divide_numbers",
            parameters=[
                Parameter(name="numerator", type_hint="float"),
                Parameter(name="denominator", type_hint="float")
            ],
            return_type="float",
            complexity=2,
            line_range=(1, 5)
        )
        
        test_cases = self.generator.generate_edge_case_tests(function_info, "python")
        
        assert len(test_cases) > 0
        assert any("edge" in test.name for test in test_cases)
    
    def test_different_languages(self):
        """Test generating tests for different languages."""
        function_info = FunctionInfo(
            name="test_function",
            parameters=[Parameter(name="param", type_hint="str")],
            return_type="str",
            complexity=1,
            line_range=(1, 2)
        )
        
        languages = ["python", "javascript", "java"]
        
        for language in languages:
            test_cases = self.generator.generate_unit_tests(function_info, language)
            assert len(test_cases) > 0
            # Check that the test code contains language-specific syntax
            test_code = test_cases[0].test_code
            if language == "python":
                assert "def " in test_code
            elif language == "javascript":
                assert "test(" in test_code
            elif language == "java":
                assert "@Test" in test_code


class TestTestDataGenerator:
    """Test the TestDataGenerator class."""
    
    def test_generate_for_type_integer(self):
        """Test generating test data for integer types."""
        values = TestDataGenerator.generate_for_type("count", "int", "python", "basic")
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(v, int) for v in values)
    
    def test_generate_for_type_string(self):
        """Test generating test data for string types."""
        values = TestDataGenerator.generate_for_type("name", "str", "python", "basic")
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(v, str) for v in values)
    
    def test_generate_for_type_edge_context(self):
        """Test generating edge case test data."""
        values = TestDataGenerator.generate_for_type("value", "int", "python", "edge")
        assert isinstance(values, list)
        assert len(values) > 0
        # Should include edge values like min/max integers
        assert any(v < 0 for v in values)
    
    def test_generate_for_type_list(self):
        """Test generating test data for list types."""
        values = TestDataGenerator.generate_for_type("items", "list", "python", "basic")
        assert isinstance(values, list)
        assert len(values) > 0
        assert all(isinstance(v, list) for v in values)


class TestAssertionGenerator:
    """Test the AssertionGenerator class."""
    
    def test_generate_assertions_python(self):
        """Test generating Python assertions."""
        function_info = FunctionInfo(
            name="add",
            parameters=[Parameter(name="a"), Parameter(name="b")],
            return_type="int",
            complexity=1,
            line_range=(1, 2)
        )
        
        test_inputs = {"a": 1, "b": 2}
        assertions = AssertionGenerator.generate_assertions(
            function_info, test_inputs, "returns_value", "python"
        )
        
        assert isinstance(assertions, list)
        assert len(assertions) > 0
        assert any("assert" in assertion for assertion in assertions)
    
    def test_generate_assertions_javascript(self):
        """Test generating JavaScript assertions."""
        function_info = FunctionInfo(
            name="add",
            parameters=[Parameter(name="a"), Parameter(name="b")],
            return_type="number",
            complexity=1,
            line_range=(1, 2)
        )
        
        test_inputs = {"a": 1, "b": 2}
        assertions = AssertionGenerator.generate_assertions(
            function_info, test_inputs, "returns_value", "javascript"
        )
        
        assert isinstance(assertions, list)
        assert len(assertions) > 0
        assert any("expect" in assertion for assertion in assertions)
    
    def test_generate_assertions_exception(self):
        """Test generating exception assertions."""
        function_info = FunctionInfo(
            name="divide",
            parameters=[Parameter(name="a"), Parameter(name="b")],
            return_type="float",
            complexity=1,
            line_range=(1, 2)
        )
        
        test_inputs = {"a": 1, "b": 0}
        assertions = AssertionGenerator.generate_assertions(
            function_info, test_inputs, "throws_exception", "python"
        )
        
        assert isinstance(assertions, list)
        assert len(assertions) > 0
        assert any("pytest.raises" in assertion for assertion in assertions)