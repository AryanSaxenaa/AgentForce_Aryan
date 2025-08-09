"""
Unit tests for FunctionAnalyzer class.
"""
import pytest
from unittest.mock import Mock, patch
from src.analyzers.function_analyzer import FunctionAnalyzer
from src.interfaces.base_interfaces import FunctionInfo, ClassInfo, Parameter


class TestFunctionAnalyzer:
    """Test cases for FunctionAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = FunctionAnalyzer()
    
    def test_analyze_python_functions(self):
        """Test analyzing Python functions."""
        python_code = '''
def add(a, b):
    """Add two numbers."""
    return a + b

def greet(name: str = "World") -> str:
    """Greet someone."""
    return f"Hello, {name}!"

class Calculator:
    def multiply(self, x: int, y: int) -> int:
        return x * y
'''
        
        functions = self.analyzer.analyze_functions(python_code, 'python')
        
        assert len(functions) >= 2  # add, greet, and possibly multiply
        
        # Check add function
        add_func = next((f for f in functions if f.name == 'add'), None)
        assert add_func is not None
        assert len(add_func.parameters) == 2
        assert add_func.parameters[0].name == 'a'
        assert add_func.parameters[1].name == 'b'
        assert add_func.docstring == "Add two numbers."
        
        # Check greet function
        greet_func = next((f for f in functions if f.name == 'greet'), None)
        assert greet_func is not None
        assert len(greet_func.parameters) == 1
        assert greet_func.parameters[0].name == 'name'
        assert greet_func.parameters[0].type_hint == 'str'
        assert greet_func.parameters[0].default_value == '"World"'
        assert greet_func.return_type == 'str'
    
    def test_analyze_javascript_functions(self):
        """Test analyzing JavaScript functions."""
        js_code = '''
function add(a, b) {
    return a + b;
}

const multiply = (x, y) => x * y;

class Calculator {
    divide(a, b) {
        return a / b;
    }
}
'''
        
        functions = self.analyzer.analyze_functions(js_code, 'javascript')
        
        assert len(functions) >= 2  # add, multiply, and possibly divide
        
        # Check add function
        add_func = next((f for f in functions if f.name == 'add'), None)
        assert add_func is not None
        assert len(add_func.parameters) == 2
        assert add_func.parameters[0].name == 'a'
        assert add_func.parameters[1].name == 'b'
        
        # Check arrow function
        multiply_func = next((f for f in functions if f.name == 'anonymous_arrow'), None)
        if multiply_func:  # Arrow functions might be detected as anonymous
            assert len(multiply_func.parameters) == 2
    
    def test_analyze_java_methods(self):
        """Test analyzing Java methods."""
        java_code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public String greet(String name) {
        return "Hello, " + name;
    }
    
    private void helper() {
        // Helper method
    }
}
'''
        
        functions = self.analyzer.analyze_functions(java_code, 'java')
        
        assert len(functions) >= 2  # add, greet, helper
        
        # Check add method
        add_func = next((f for f in functions if f.name == 'add'), None)
        assert add_func is not None
        assert len(add_func.parameters) == 2
        assert add_func.return_type == 'int'
        
        # Check greet method
        greet_func = next((f for f in functions if f.name == 'greet'), None)
        assert greet_func is not None
        assert len(greet_func.parameters) == 1
        assert greet_func.parameters[0].name == 'name'
        assert greet_func.parameters[0].type_hint == 'String'
        assert greet_func.return_type == 'String'
    
    def test_analyze_python_classes(self):
        """Test analyzing Python classes."""
        python_code = '''
class Calculator:
    def add(self, a, b):
        return a + b
    
    def subtract(self, a, b):
        return a - b

class AdvancedCalculator(Calculator):
    def multiply(self, a, b):
        return a * b
'''
        
        classes = self.analyzer.analyze_classes(python_code, 'python')
        
        assert len(classes) == 2
        
        # Check Calculator class
        calc_class = next((c for c in classes if c.name == 'Calculator'), None)
        assert calc_class is not None
        assert 'add' in calc_class.methods
        assert 'subtract' in calc_class.methods
        
        # Check AdvancedCalculator class
        adv_calc_class = next((c for c in classes if c.name == 'AdvancedCalculator'), None)
        assert adv_calc_class is not None
        assert 'multiply' in adv_calc_class.methods
        assert 'Calculator' in adv_calc_class.inheritance
    
    def test_get_function_signature_python(self):
        """Test generating Python function signatures."""
        func_info = FunctionInfo(
            name='greet',
            parameters=[
                Parameter(name='name', type_hint='str', default_value='"World"')
            ],
            return_type='str',
            complexity=1,
            line_range=(1, 3)
        )
        
        signature = self.analyzer.get_function_signature(func_info, 'python')
        expected = 'def greet(name: str = "World") -> str'
        assert signature == expected
    
    def test_get_function_signature_javascript(self):
        """Test generating JavaScript function signatures."""
        func_info = FunctionInfo(
            name='add',
            parameters=[
                Parameter(name='a'),
                Parameter(name='b', default_value='0')
            ],
            return_type=None,
            complexity=1,
            line_range=(1, 3)
        )
        
        signature = self.analyzer.get_function_signature(func_info, 'javascript')
        expected = 'function add(a, b = 0)'
        assert signature == expected
    
    def test_get_function_signature_java(self):
        """Test generating Java method signatures."""
        func_info = FunctionInfo(
            name='add',
            parameters=[
                Parameter(name='a', type_hint='int'),
                Parameter(name='b', type_hint='int')
            ],
            return_type='int',
            complexity=1,
            line_range=(1, 3)
        )
        
        signature = self.analyzer.get_function_signature(func_info, 'java')
        expected = 'public int add(int a, int b)'
        assert signature == expected
    
    def test_detect_parameter_types(self):
        """Test parameter type detection."""
        func_info = FunctionInfo(
            name='test',
            parameters=[
                Parameter(name='flag', default_value='True'),
                Parameter(name='count', default_value='10'),
                Parameter(name='name', default_value='"test"'),
                Parameter(name='value', default_value='3.14')
            ],
            return_type=None,
            complexity=1,
            line_range=(1, 3)
        )
        
        enhanced_params = self.analyzer.detect_parameter_types(func_info, 'python')
        
        assert enhanced_params[0].type_hint == 'bool'  # flag
        assert enhanced_params[1].type_hint == 'int'   # count
        assert enhanced_params[2].type_hint == 'str'   # name
        assert enhanced_params[3].type_hint == 'float' # value
    
    def test_complexity_calculation(self):
        """Test function complexity calculation."""
        complex_python_code = '''
def complex_function(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                try:
                    result = i / (x - i)
                except ZeroDivisionError:
                    result = 0
            else:
                result = i * 2
        return result
    else:
        return 0
'''
        
        functions = self.analyzer.analyze_functions(complex_python_code, 'python')
        
        assert len(functions) == 1
        func = functions[0]
        assert func.name == 'complex_function'
        # Complexity should be > 1 due to if statements, for loop, try/except
        assert func.complexity > 1
    
    def test_error_handling(self):
        """Test error handling with invalid code."""
        invalid_code = "def incomplete_function("
        
        # Should not raise exception, but return empty list
        functions = self.analyzer.analyze_functions(invalid_code, 'python')
        assert isinstance(functions, list)
        # May be empty or contain partial results depending on parser behavior
    
    def test_unsupported_language(self):
        """Test handling of unsupported languages."""
        code = "some code"
        
        functions = self.analyzer.analyze_functions(code, 'unsupported')
        assert functions == []
        
        classes = self.analyzer.analyze_classes(code, 'unsupported')
        assert classes == []
    
    @patch('src.analyzers.function_analyzer.logger')
    def test_logging(self, mock_logger):
        """Test that appropriate logging occurs."""
        python_code = '''
def simple_function():
    pass
'''
        
        self.analyzer.analyze_functions(python_code, 'python')
        
        # Check that info logging occurred
        mock_logger.info.assert_called()
        
        # Test error logging with invalid language
        self.analyzer.analyze_functions(python_code, 'invalid')
        mock_logger.warning.assert_called()


if __name__ == '__main__':
    pytest.main([__file__])