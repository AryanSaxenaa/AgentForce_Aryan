"""
Unit tests for EdgeTestGenerator
"""
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from generators.edge_test_generator import EdgeTestGenerator, EdgeCaseAnalyzer, EdgeTestScenario
from interfaces.base_interfaces import FunctionInfo, Parameter, EdgeCase, TestType


class TestEdgeCaseAnalyzer:
    """Test cases for EdgeCaseAnalyzer."""
    
    def test_analyze_function_edge_cases_basic(self):
        """Test basic edge case analysis."""
        # Arrange
        function_info = FunctionInfo(
            name="test_function",
            parameters=[
                Parameter(name="value", type_hint="int"),
                Parameter(name="text", type_hint="str")
            ],
            return_type="str",
            complexity=1,
            line_range=(1, 10)
        )
        detected_edge_cases = []
        
        # Act
        scenarios = EdgeCaseAnalyzer.analyze_function_edge_cases(function_info, detected_edge_cases)
        
        # Assert
        assert len(scenarios) > 0
        assert any(scenario.edge_case_type == "null_input" for scenario in scenarios)
        assert any(scenario.edge_case_type == "boundary_value" for scenario in scenarios)
    
    def test_analyze_parameter_edge_cases_numeric(self):
        """Test edge case analysis for numeric parameters."""
        # Arrange
        param = Parameter(name="count", type_hint="int")
        function_info = FunctionInfo(
            name="test_function",
            parameters=[param],
            return_type="int",
            complexity=1,
            line_range=(1, 5)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_parameter_edge_cases(param, function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "null_input" in scenario_types
        assert "boundary_value" in scenario_types
        
        # Check for specific numeric edge cases
        zero_scenario = next((s for s in scenarios if s.name == "zero_count"), None)
        assert zero_scenario is not None
        assert zero_scenario.test_inputs["count"] == 0
    
    def test_analyze_parameter_edge_cases_string(self):
        """Test edge case analysis for string parameters."""
        # Arrange
        param = Parameter(name="text", type_hint="str")
        function_info = FunctionInfo(
            name="test_function",
            parameters=[param],
            return_type="str",
            complexity=1,
            line_range=(1, 5)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_parameter_edge_cases(param, function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "null_input" in scenario_types
        assert "empty_input" in scenario_types
        
        # Check for specific string edge cases
        empty_scenario = next((s for s in scenarios if s.name == "empty_string_text"), None)
        assert empty_scenario is not None
        assert empty_scenario.test_inputs["text"] == ""
    
    def test_analyze_parameter_edge_cases_collection(self):
        """Test edge case analysis for collection parameters."""
        # Arrange
        param = Parameter(name="items", type_hint="list")
        function_info = FunctionInfo(
            name="test_function",
            parameters=[param],
            return_type="int",
            complexity=1,
            line_range=(1, 5)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_parameter_edge_cases(param, function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "null_input" in scenario_types
        assert "empty_collection" in scenario_types
        
        # Check for specific collection edge cases
        empty_scenario = next((s for s in scenarios if s.name == "empty_list_items"), None)
        assert empty_scenario is not None
        assert empty_scenario.test_inputs["items"] == []
    
    def test_analyze_parameter_edge_cases_index(self):
        """Test edge case analysis for index parameters."""
        # Arrange
        param = Parameter(name="index", type_hint="int")
        function_info = FunctionInfo(
            name="test_function",
            parameters=[param],
            return_type="str",
            complexity=1,
            line_range=(1, 5)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_parameter_edge_cases(param, function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "index_bounds" in scenario_types
        
        # Check for specific index edge cases
        negative_scenario = next((s for s in scenarios if s.name == "negative_index_index"), None)
        assert negative_scenario is not None
        assert negative_scenario.test_inputs["index"] == -1
        assert negative_scenario.expected_behavior == "throws_exception"
        assert negative_scenario.exception_type == "IndexError"
    
    def test_analyze_parameter_edge_cases_divisor(self):
        """Test edge case analysis for divisor parameters."""
        # Arrange
        param = Parameter(name="divisor", type_hint="int")
        function_info = FunctionInfo(
            name="divide",
            parameters=[param],
            return_type="float",
            complexity=1,
            line_range=(1, 5)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_parameter_edge_cases(param, function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "division_by_zero" in scenario_types
        
        # Check for division by zero edge case
        zero_div_scenario = next((s for s in scenarios if s.name == "zero_divisor_divisor"), None)
        assert zero_div_scenario is not None
        assert zero_div_scenario.test_inputs["divisor"] == 0
        assert zero_div_scenario.expected_behavior == "throws_exception"
        assert zero_div_scenario.exception_type == "ZeroDivisionError"
    
    def test_convert_detected_edge_case_to_scenario(self):
        """Test conversion of detected edge cases to scenarios."""
        # Arrange
        edge_case = EdgeCase(
            type="division_by_zero",
            location="line 5",
            description="Potential division by zero",
            severity=2
        )
        function_info = FunctionInfo(
            name="calculate",
            parameters=[Parameter(name="divisor", type_hint="int")],
            return_type="float",
            complexity=1,
            line_range=(1, 10)
        )
        
        # Act
        scenario = EdgeCaseAnalyzer._convert_detected_edge_case_to_scenario(edge_case, function_info)
        
        # Assert
        assert scenario is not None
        assert scenario.edge_case_type == "division_by_zero"
        assert scenario.expected_behavior == "throws_exception"
        assert scenario.exception_type == "ZeroDivisionError"
    
    def test_analyze_context_edge_cases_mathematical(self):
        """Test context-aware edge case analysis for mathematical functions."""
        # Arrange
        function_info = FunctionInfo(
            name="calculate_average",
            parameters=[Parameter(name="numbers", type_hint="list")],
            return_type="float",
            complexity=1,
            line_range=(1, 10)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_context_edge_cases(function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "numeric_overflow" in scenario_types
    
    def test_analyze_context_edge_cases_string_processing(self):
        """Test context-aware edge case analysis for string processing functions."""
        # Arrange
        function_info = FunctionInfo(
            name="parse_json",
            parameters=[Parameter(name="json_string", type_hint="str")],
            return_type="dict",
            complexity=1,
            line_range=(1, 10)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_context_edge_cases(function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "malformed_input" in scenario_types
    
    def test_analyze_context_edge_cases_file_io(self):
        """Test context-aware edge case analysis for file I/O functions."""
        # Arrange
        function_info = FunctionInfo(
            name="read_file",
            parameters=[Parameter(name="filename", type_hint="str")],
            return_type="str",
            complexity=1,
            line_range=(1, 10)
        )
        
        # Act
        scenarios = EdgeCaseAnalyzer._analyze_context_edge_cases(function_info)
        
        # Assert
        assert len(scenarios) > 0
        scenario_types = [s.edge_case_type for s in scenarios]
        assert "file_not_found" in scenario_types


class TestEdgeTestGenerator:
    """Test cases for EdgeTestGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = EdgeTestGenerator()
        self.sample_function = FunctionInfo(
            name="test_function",
            parameters=[
                Parameter(name="value", type_hint="int"),
                Parameter(name="text", type_hint="str")
            ],
            return_type="str",
            complexity=1,
            line_range=(1, 10)
        )
    
    def test_init(self):
        """Test EdgeTestGenerator initialization."""
        # Assert
        assert self.generator.edge_case_analyzer is not None
        assert "python" in self.generator.templates
        assert "javascript" in self.generator.templates
        assert "java" in self.generator.templates
    
    def test_generate_edge_case_tests(self):
        """Test edge case test generation."""
        # Arrange
        detected_edge_cases = [
            EdgeCase(
                type="division_by_zero",
                location="line 5",
                description="Potential division by zero",
                severity=2
            )
        ]
        
        # Act
        test_cases = self.generator.generate_edge_case_tests(
            self.sample_function, detected_edge_cases, "python"
        )
        
        # Assert
        assert len(test_cases) > 0
        assert all(test_case.test_type == TestType.EDGE for test_case in test_cases)
        assert all(test_case.function_name == "test_function" for test_case in test_cases)
        assert all("edge" in test_case.name for test_case in test_cases)
    
    def test_generate_boundary_value_tests(self):
        """Test boundary value test generation."""
        # Act
        test_cases = self.generator.generate_boundary_value_tests(self.sample_function, "python")
        
        # Assert
        assert len(test_cases) > 0
        assert all(test_case.test_type == TestType.EDGE for test_case in test_cases)
        assert any("boundary" in test_case.name for test_case in test_cases)
    
    def test_generate_exception_tests(self):
        """Test exception test generation."""
        # Act
        test_cases = self.generator.generate_exception_tests(self.sample_function, "python")
        
        # Assert
        assert len(test_cases) > 0
        assert all(test_case.test_type == TestType.EDGE for test_case in test_cases)
        assert any("pytest.raises" in test_case.test_code for test_case in test_cases)
    
    def test_generate_negative_tests(self):
        """Test negative test generation."""
        # Act
        test_cases = self.generator.generate_negative_tests(self.sample_function, "python")
        
        # Assert
        assert len(test_cases) > 0
        assert all(test_case.test_type == TestType.EDGE for test_case in test_cases)
    
    def test_generate_negative_tests_validation_function(self):
        """Test negative test generation for validation functions."""
        # Arrange
        validation_function = FunctionInfo(
            name="validate_email",
            parameters=[Parameter(name="email", type_hint="str")],
            return_type="bool",
            complexity=1,
            line_range=(1, 10)
        )
        
        # Act
        test_cases = self.generator.generate_negative_tests(validation_function, "python")
        
        # Assert
        assert len(test_cases) > 0
        assert all(test_case.test_type == TestType.EDGE for test_case in test_cases)
    
    def test_generate_negative_tests_calculation_function(self):
        """Test negative test generation for calculation functions."""
        # Arrange
        calc_function = FunctionInfo(
            name="calculate_result",
            parameters=[Parameter(name="divisor", type_hint="int")],
            return_type="float",
            complexity=1,
            line_range=(1, 10)
        )
        
        # Act
        test_cases = self.generator.generate_negative_tests(calc_function, "python")
        
        # Assert
        assert len(test_cases) > 0
        assert all(test_case.test_type == TestType.EDGE for test_case in test_cases)
    
    def test_generate_test_case_for_scenario_exception(self):
        """Test test case generation for exception scenarios."""
        # Arrange
        scenario = EdgeTestScenario(
            name="test_scenario",
            description="Test scenario description",
            edge_case_type="null_input",
            test_inputs={"value": None},
            expected_behavior="throws_exception",
            exception_type="TypeError"
        )
        
        # Act
        test_case = self.generator._generate_test_case_for_scenario(
            self.sample_function, scenario, "python"
        )
        
        # Assert
        assert test_case is not None
        assert test_case.test_type == TestType.EDGE
        assert "pytest.raises(TypeError)" in test_case.test_code
        assert "test_function(value=None)" in test_case.test_code
    
    def test_generate_test_case_for_scenario_return_value(self):
        """Test test case generation for return value scenarios."""
        # Arrange
        scenario = EdgeTestScenario(
            name="test_scenario",
            description="Test scenario description",
            edge_case_type="boundary_value",
            test_inputs={"value": 0},
            expected_behavior="returns_value"
        )
        
        # Act
        test_case = self.generator._generate_test_case_for_scenario(
            self.sample_function, scenario, "python"
        )
        
        # Assert
        assert test_case is not None
        assert test_case.test_type == TestType.EDGE
        assert "result = test_function(value=0)" in test_case.test_code
        assert "assert result is not None" in test_case.test_code
    
    def test_generate_test_case_for_scenario_graceful_handling(self):
        """Test test case generation for graceful handling scenarios."""
        # Arrange
        scenario = EdgeTestScenario(
            name="test_scenario",
            description="Test scenario description",
            edge_case_type="empty_input",
            test_inputs={"text": ""},
            expected_behavior="handles_gracefully"
        )
        
        # Act
        test_case = self.generator._generate_test_case_for_scenario(
            self.sample_function, scenario, "python"
        )
        
        # Assert
        assert test_case is not None
        assert test_case.test_type == TestType.EDGE
        assert "test_function(text='')" in test_case.test_code
        assert "assert True" in test_case.test_code
    
    def test_is_numeric_parameter(self):
        """Test numeric parameter detection."""
        # Test with type hint
        numeric_param = Parameter(name="value", type_hint="int")
        assert self.generator._is_numeric_parameter(numeric_param)
        
        # Test with parameter name
        numeric_param_name = Parameter(name="count", type_hint=None)
        assert self.generator._is_numeric_parameter(numeric_param_name)
        
        # Test non-numeric
        string_param = Parameter(name="text", type_hint="str")
        assert not self.generator._is_numeric_parameter(string_param)
    
    def test_is_string_parameter(self):
        """Test string parameter detection."""
        # Test with type hint
        string_param = Parameter(name="value", type_hint="str")
        assert self.generator._is_string_parameter(string_param)
        
        # Test with parameter name
        string_param_name = Parameter(name="text", type_hint=None)
        assert self.generator._is_string_parameter(string_param_name)
        
        # Test non-string
        numeric_param = Parameter(name="count", type_hint="int")
        assert not self.generator._is_string_parameter(numeric_param)
    
    def test_is_collection_parameter(self):
        """Test collection parameter detection."""
        # Test with type hint
        list_param = Parameter(name="value", type_hint="list")
        assert self.generator._is_collection_parameter(list_param)
        
        # Test with parameter name
        list_param_name = Parameter(name="items", type_hint=None)
        assert self.generator._is_collection_parameter(list_param_name)
        
        # Test non-collection
        string_param = Parameter(name="text", type_hint="str")
        assert not self.generator._is_collection_parameter(string_param)
    
    def test_js_repr(self):
        """Test JavaScript representation of values."""
        assert self.generator._js_repr(None) == "null"
        assert self.generator._js_repr(True) == "true"
        assert self.generator._js_repr(False) == "false"
        assert self.generator._js_repr("test") == '"test"'
        assert self.generator._js_repr([1, 2, 3]) == "[1, 2, 3]"
        assert self.generator._js_repr({"key": "value"}) == '{"key": "value"}'
    
    def test_java_repr(self):
        """Test Java representation of values."""
        assert self.generator._java_repr(None) == "null"
        assert self.generator._java_repr(True) == "true"
        assert self.generator._java_repr(False) == "false"
        assert self.generator._java_repr("test") == '"test"'
        assert "Arrays.asList" in self.generator._java_repr([1, 2, 3])
        assert "HashMap" in self.generator._java_repr({"key": "value"})
    
    def test_templates_exist(self):
        """Test that all language templates exist and are properly formatted."""
        for language in ["python", "javascript", "typescript", "java"]:
            template = self.generator.templates[language]
            assert template is not None
            assert "{test_name}" in template
            assert "{description}" in template
            assert "{setup_code}" in template
            assert "{test_execution}" in template
            assert "{assertions}" in template
            assert "{teardown_code}" in template


if __name__ == "__main__":
    pytest.main([__file__])