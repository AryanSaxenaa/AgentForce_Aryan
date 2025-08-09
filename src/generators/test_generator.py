"""
Test Generator - Generates unit, integration, and edge test cases
"""
from typing import List, Dict, Any
from dataclasses import dataclass
from analyzers.code_analyzer import AnalysisResult, FunctionInfo

@dataclass
class TestCase:
    name: str
    test_type: str  # 'unit', 'integration', 'edge'
    function_name: str
    description: str
    test_code: str
    setup_code: str = ""
    assertions: List[str] = None

class TestGenerator:
    """Generates comprehensive test cases based on code analysis."""
    
    def __init__(self):
        self.test_templates = {
            'python': {
                'unit': self._python_unit_template,
                'edge': self._python_edge_template,
                'integration': self._python_integration_template
            },
            'javascript': {
                'unit': self._javascript_unit_template,
                'edge': self._javascript_edge_template,
                'integration': self._javascript_integration_template
            },
            'java': {
                'unit': self._java_unit_template,
                'edge': self._java_edge_template,
                'integration': self._java_integration_template
            }
        }
    
    def generate_tests(self, analysis: AnalysisResult) -> List[TestCase]:
        """Generate comprehensive test cases from analysis results."""
        test_cases = []
        
        for function in analysis.functions:
            # Generate unit tests
            test_cases.extend(self._generate_unit_tests(function, analysis))
            
            # Generate edge case tests
            test_cases.extend(self._generate_edge_tests(function, analysis))
            
            # Generate integration tests if applicable
            if self._needs_integration_tests(function, analysis):
                test_cases.extend(self._generate_integration_tests(function, analysis))
        
        return test_cases
    
    def _generate_unit_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> List[TestCase]:
        """Generate unit tests for a function."""
        tests = []
        template_func = self.test_templates[analysis.language]['unit']
        
        # Basic functionality test
        test_code = template_func(function, 'basic', self._generate_basic_inputs(function))
        tests.append(TestCase(
            name=f"test_{function.name}_basic",
            test_type='unit',
            function_name=function.name,
            description=f"Test basic functionality of {function.name}",
            test_code=test_code
        ))
        
        # Test with different input types if function has parameters
        if function.args:
            for i, arg in enumerate(function.args):
                test_code = template_func(function, f'param_{i}', self._generate_param_variations(function, i))
                tests.append(TestCase(
                    name=f"test_{function.name}_param_{arg}",
                    test_type='unit',
                    function_name=function.name,
                    description=f"Test {function.name} with different {arg} values",
                    test_code=test_code
                ))
        
        return tests
    
    def _generate_edge_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> List[TestCase]:
        """Generate edge case tests."""
        tests = []
        template_func = self.test_templates[analysis.language]['edge']
        
        edge_scenarios = self._identify_edge_scenarios(function, analysis)
        
        for scenario in edge_scenarios:
            test_code = template_func(function, scenario['type'], scenario['inputs'])
            tests.append(TestCase(
                name=f"test_{function.name}_edge_{scenario['type']}",
                test_type='edge',
                function_name=function.name,
                description=f"Test {function.name} edge case: {scenario['description']}",
                test_code=test_code
            ))
        
        return tests
    
    def _generate_integration_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> List[TestCase]:
        """Generate integration tests."""
        tests = []
        template_func = self.test_templates[analysis.language]['integration']
        
        # Integration test for functions that interact with external systems
        test_code = template_func(function, 'integration', {})
        tests.append(TestCase(
            name=f"test_{function.name}_integration",
            test_type='integration',
            function_name=function.name,
            description=f"Integration test for {function.name}",
            test_code=test_code
        ))
        
        return tests
    
    def _needs_integration_tests(self, function: FunctionInfo, analysis: AnalysisResult) -> bool:
        """Determine if function needs integration tests."""
        # Check for external dependencies
        external_indicators = ['requests', 'urllib', 'database', 'api', 'file', 'open']
        
        if function.docstring:
            return any(indicator in function.docstring.lower() for indicator in external_indicators)
        
        # Check imports for external libraries
        return any(indicator in ' '.join(analysis.imports).lower() for indicator in external_indicators)
    
    def _identify_edge_scenarios(self, function: FunctionInfo, analysis: AnalysisResult) -> List[Dict[str, Any]]:
        """Identify edge case scenarios for a function."""
        scenarios = []
        
        # Common edge cases based on function signature
        if function.args:
            scenarios.extend([
                {
                    'type': 'null_input',
                    'description': 'null/None input values',
                    'inputs': {arg: None for arg in function.args}
                },
                {
                    'type': 'empty_input',
                    'description': 'empty input values',
                    'inputs': {arg: self._get_empty_value(analysis.language) for arg in function.args}
                }
            ])
        
        # Add scenarios based on detected edge cases
        for edge_case in analysis.edge_cases:
            if 'division' in edge_case.lower():
                scenarios.append({
                    'type': 'division_by_zero',
                    'description': 'division by zero',
                    'inputs': self._generate_division_zero_inputs(function)
                })
            elif 'index' in edge_case.lower():
                scenarios.append({
                    'type': 'index_error',
                    'description': 'index out of bounds',
                    'inputs': self._generate_index_error_inputs(function)
                })
        
        return scenarios
    
    def _generate_basic_inputs(self, function: FunctionInfo) -> Dict[str, Any]:
        """Generate basic test inputs for a function."""
        inputs = {}
        for arg in function.args:
            inputs[arg] = self._get_default_value(arg)
        return inputs
    
    def _generate_param_variations(self, function: FunctionInfo, param_index: int) -> Dict[str, Any]:
        """Generate parameter variations for testing."""
        inputs = self._generate_basic_inputs(function)
        arg_name = function.args[param_index]
        
        # Generate different values based on parameter name
        if 'num' in arg_name.lower() or 'count' in arg_name.lower():
            inputs[arg_name] = [0, 1, -1, 100, -100]
        elif 'str' in arg_name.lower() or 'text' in arg_name.lower():
            inputs[arg_name] = ['', 'test', 'a' * 1000]
        elif 'list' in arg_name.lower() or 'arr' in arg_name.lower():
            inputs[arg_name] = [[], [1], [1, 2, 3]]
        
        return inputs
    
    def _get_default_value(self, param_name: str) -> Any:
        """Get default test value based on parameter name."""
        if 'num' in param_name.lower() or 'count' in param_name.lower():
            return 5
        elif 'str' in param_name.lower() or 'text' in param_name.lower():
            return 'test_string'
        elif 'list' in param_name.lower() or 'arr' in param_name.lower():
            return [1, 2, 3]
        elif 'bool' in param_name.lower():
            return True
        else:
            return 'test_value'
    
    def _get_empty_value(self, language: str) -> Any:
        """Get empty value for the language."""
        if language == 'python':
            return ''
        elif language in ['javascript', 'typescript']:
            return 'null'
        elif language == 'java':
            return 'null'
        return ''
    
    def _generate_division_zero_inputs(self, function: FunctionInfo) -> Dict[str, Any]:
        """Generate inputs that might cause division by zero."""
        inputs = self._generate_basic_inputs(function)
        # Look for parameters that might be divisors
        for arg in function.args:
            if 'divisor' in arg.lower() or 'denom' in arg.lower():
                inputs[arg] = 0
        return inputs
    
    def _generate_index_error_inputs(self, function: FunctionInfo) -> Dict[str, Any]:
        """Generate inputs that might cause index errors."""
        inputs = self._generate_basic_inputs(function)
        for arg in function.args:
            if 'index' in arg.lower() or 'idx' in arg.lower():
                inputs[arg] = -1  # Negative index
        return inputs
    
    # Template functions for different languages
    def _python_unit_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Python unit test template."""
        test_code = f"""def test_{function.name}_{test_type}():
    # Arrange
"""
        
        for arg, value in inputs.items():
            if isinstance(value, str):
                test_code += f"    {arg} = '{value}'\n"
            else:
                test_code += f"    {arg} = {value}\n"
        
        test_code += f"""    
    # Act
    result = {function.name}({', '.join(inputs.keys())})
    
    # Assert
    assert result is not None
    # Add specific assertions based on expected behavior
"""
        return test_code
    
    def _python_edge_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Python edge case test template."""
        test_code = f"""def test_{function.name}_edge_{test_type}():
    # Test edge case: {test_type}
    
    # Arrange
"""
        
        for arg, value in inputs.items():
            if value is None:
                test_code += f"    {arg} = None\n"
            elif isinstance(value, str):
                test_code += f"    {arg} = '{value}'\n"
            else:
                test_code += f"    {arg} = {value}\n"
        
        if test_type == 'division_by_zero':
            test_code += f"""    
    # Act & Assert
    with pytest.raises(ZeroDivisionError):
        {function.name}({', '.join(inputs.keys())})
"""
        elif test_type == 'null_input':
            test_code += f"""    
    # Act & Assert
    with pytest.raises((TypeError, ValueError)):
        {function.name}({', '.join(inputs.keys())})
"""
        else:
            test_code += f"""    
    # Act
    result = {function.name}({', '.join(inputs.keys())})
    
    # Assert
    # Add appropriate assertions for edge case
    assert result is not None or result is None  # Adjust based on expected behavior
"""
        
        return test_code
    
    def _python_integration_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Python integration test template."""
        return f"""def test_{function.name}_integration():
    # Integration test for {function.name}
    # This test should verify the function works with real external dependencies
    
    # Arrange
    # Set up test environment, mock external services if needed
    
    # Act
    result = {function.name}()  # Call with appropriate parameters
    
    # Assert
    assert result is not None
    # Add assertions to verify integration behavior
"""
    
    def _javascript_unit_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate JavaScript unit test template."""
        test_code = f"""describe('{function.name}', () => {{
    test('should handle {test_type} case', () => {{
        // Arrange
"""
        
        for arg, value in inputs.items():
            if isinstance(value, str):
                test_code += f"        const {arg} = '{value}';\n"
            else:
                test_code += f"        const {arg} = {str(value).lower()};\n"
        
        test_code += f"""        
        // Act
        const result = {function.name}({', '.join(inputs.keys())});
        
        // Assert
        expect(result).toBeDefined();
        // Add specific assertions
    }});
}});
"""
        return test_code
    
    def _javascript_edge_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate JavaScript edge case test template."""
        return f"""describe('{function.name} edge cases', () => {{
    test('should handle {test_type}', () => {{
        // Arrange
        // Set up edge case inputs
        
        // Act & Assert
        expect(() => {{
            {function.name}(/* edge case parameters */);
        }}).toThrow(); // or not.toThrow() based on expected behavior
    }});
}});
"""
    
    def _javascript_integration_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate JavaScript integration test template."""
        return f"""describe('{function.name} integration', () => {{
    test('should integrate with external systems', async () => {{
        // Arrange
        // Set up integration test environment
        
        // Act
        const result = await {function.name}();
        
        // Assert
        expect(result).toBeDefined();
        // Add integration-specific assertions
    }});
}});
"""
    
    def _java_unit_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Java unit test template."""
        return f"""@Test
public void test{function.name.capitalize()}{test_type.capitalize()}() {{
    // Arrange
    // Set up test data
    
    // Act
    // Call the method under test
    
    // Assert
    assertNotNull(result);
    // Add specific assertions
}}
"""
    
    def _java_edge_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Java edge case test template."""
        return f"""@Test(expected = Exception.class)
public void test{function.name.capitalize()}Edge{test_type.capitalize()}() {{
    // Arrange
    // Set up edge case scenario
    
    // Act
    // This should throw an exception
    // Call method with edge case parameters
}}
"""
    
    def _java_integration_template(self, function: FunctionInfo, test_type: str, inputs: Dict[str, Any]) -> str:
        """Generate Java integration test template."""
        return f"""@Test
public void test{function.name.capitalize()}Integration() {{
    // Arrange
    // Set up integration test environment
    
    // Act
    // Call method that integrates with external systems
    
    // Assert
    assertNotNull(result);
    // Add integration-specific assertions
}}
"""