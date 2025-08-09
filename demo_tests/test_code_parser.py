"""
Unit tests for the tree-sitter based code parser.
"""
import pytest
import tempfile
import os
from pathlib import Path

from src.analyzers.code_parser import CodeParser, ASTNode
from src.interfaces.base_interfaces import (
    CodeAnalysis, FunctionInfo, ClassInfo, Parameter,
    EdgeCase, Dependency, ComplexityMetrics
)


class TestCodeParser:
    """Test cases for CodeParser class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
    
    def test_parser_initialization(self):
        """Test that parser initializes with all supported languages."""
        expected_languages = ['python', 'javascript', 'typescript', 'java']
        
        for lang in expected_languages:
            assert lang in self.parser.languages
            assert lang in self.parser.parsers
    
    def test_language_detection(self):
        """Test automatic language detection from file extensions."""
        test_cases = [
            ('test.py', 'python'),
            ('test.js', 'javascript'),
            ('test.ts', 'typescript'),
            ('test.jsx', 'javascript'),
            ('test.tsx', 'typescript'),
            ('test.java', 'java')
        ]
        
        for filename, expected_lang in test_cases:
            path = Path(filename)
            detected_lang = self.parser._detect_language(path)
            assert detected_lang == expected_lang
    
    def test_unsupported_language_detection(self):
        """Test error handling for unsupported file extensions."""
        with pytest.raises(ValueError, match="Cannot detect language"):
            self.parser._detect_language(Path('test.cpp'))
    
    def test_parse_python_code(self):
        """Test parsing Python code into AST."""
        python_code = '''
def hello_world(name):
    """Say hello to someone."""
    return f"Hello, {name}!"

class Greeter:
    def greet(self, name):
        return hello_world(name)
'''
        
        ast = self.parser.parse_code(python_code, 'python')
        
        assert isinstance(ast, ASTNode)
        assert ast.type == 'module'
        assert not ast.node.has_error
    
    def test_parse_javascript_code(self):
        """Test parsing JavaScript code into AST."""
        js_code = '''
function helloWorld(name) {
    return `Hello, ${name}!`;
}

const greet = (name) => {
    return helloWorld(name);
};

class Greeter {
    greet(name) {
        return helloWorld(name);
    }
}
'''
        
        ast = self.parser.parse_code(js_code, 'javascript')
        
        assert isinstance(ast, ASTNode)
        assert ast.type == 'program'
        assert not ast.node.has_error
    
    def test_parse_java_code(self):
        """Test parsing Java code into AST."""
        java_code = '''
public class Greeter {
    public String helloWorld(String name) {
        return "Hello, " + name + "!";
    }
    
    public void greet(String name) {
        System.out.println(helloWorld(name));
    }
}
'''
        
        ast = self.parser.parse_code(java_code, 'java')
        
        assert isinstance(ast, ASTNode)
        assert ast.type == 'program'
        assert not ast.node.has_error
    
    def test_identify_python_functions(self):
        """Test identification of Python functions."""
        python_code = '''
def simple_function():
    pass

def function_with_params(a, b, c=None):
    """Function with parameters and default value."""
    return a + b

def function_with_type_hints(x: int, y: str) -> str:
    return f"{x}: {y}"
'''
        
        ast = self.parser.parse_code(python_code, 'python')
        functions = self.parser.identify_functions(ast)
        
        assert len(functions) == 3
        
        # Check first function
        func1 = functions[0]
        assert func1.name == 'simple_function'
        assert len(func1.parameters) == 0
        assert func1.complexity >= 1
        
        # Check second function
        func2 = functions[1]
        assert func2.name == 'function_with_params'
        assert len(func2.parameters) == 3
        assert func2.docstring is not None
        
        # Check third function
        func3 = functions[2]
        assert func3.name == 'function_with_type_hints'
        assert len(func3.parameters) == 2
    
    def test_identify_python_classes(self):
        """Test identification of Python classes."""
        python_code = '''
class SimpleClass:
    pass

class ClassWithMethods:
    def __init__(self):
        pass
    
    def method1(self):
        return "method1"
    
    def method2(self, param):
        return f"method2: {param}"

class InheritedClass(ClassWithMethods):
    def method3(self):
        return "method3"
'''
        
        ast = self.parser.parse_code(python_code, 'python')
        classes = self.parser.identify_classes(ast)
        
        assert len(classes) == 3
        
        # Check first class
        class1 = classes[0]
        assert class1.name == 'SimpleClass'
        assert len(class1.methods) == 0
        
        # Check second class
        class2 = classes[1]
        assert class2.name == 'ClassWithMethods'
        assert len(class2.methods) == 3  # __init__, method1, method2
        
        # Check third class
        class3 = classes[2]
        assert class3.name == 'InheritedClass'
        assert len(class3.methods) == 1  # method3
        assert 'ClassWithMethods' in class3.inheritance
    
    def test_identify_javascript_functions(self):
        """Test identification of JavaScript functions."""
        js_code = '''
function regularFunction(a, b) {
    return a + b;
}

const arrowFunction = (x, y) => {
    return x * y;
};

const simpleArrow = () => "hello";

function complexFunction(param1, param2, param3) {
    if (param1 > 0) {
        for (let i = 0; i < param2; i++) {
            console.log(param3);
        }
    }
    return param1 + param2;
}
'''
        
        ast = self.parser.parse_code(js_code, 'javascript')
        functions = self.parser.identify_functions(ast)
        
        assert len(functions) >= 3  # At least the main functions
        
        # Find specific functions
        func_names = [f.name for f in functions]
        assert 'regularFunction' in func_names
        assert 'complexFunction' in func_names
    
    def test_identify_java_functions(self):
        """Test identification of Java methods."""
        java_code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    private String formatResult(int result) {
        return "Result: " + result;
    }
    
    public static void main(String[] args) {
        Calculator calc = new Calculator();
        int sum = calc.add(5, 3);
        System.out.println(calc.formatResult(sum));
    }
}
'''
        
        ast = self.parser.parse_code(java_code, 'java')
        functions = self.parser.identify_functions(ast)
        
        assert len(functions) == 3
        
        func_names = [f.name for f in functions]
        assert 'add' in func_names
        assert 'formatResult' in func_names
        assert 'main' in func_names
    
    def test_detect_python_edge_cases(self):
        """Test detection of Python edge cases."""
        python_code = '''
def risky_function(data, divisor):
    # Division by zero risk
    result = data / divisor
    
    # Index access risk
    first_item = data[0]
    
    # Dictionary access risk
    value = data['key']
    
    return result + first_item + value
'''
        
        ast = self.parser.parse_code(python_code, 'python')
        edge_cases = self.parser.detect_edge_cases(ast)
        
        assert len(edge_cases) > 0
        
        edge_types = [ec.type for ec in edge_cases]
        assert 'division_by_zero' in edge_types or 'index_access' in edge_types
    
    def test_detect_javascript_edge_cases(self):
        """Test detection of JavaScript edge cases."""
        js_code = '''
function processData(obj) {
    if (obj === null) {
        return null;
    }
    
    if (obj.property === undefined) {
        return undefined;
    }
    
    return obj.property.value;
}
'''
        
        ast = self.parser.parse_code(js_code, 'javascript')
        edge_cases = self.parser.detect_edge_cases(ast)
        
        # Should detect null/undefined checks
        assert len(edge_cases) > 0
    
    def test_find_python_dependencies(self):
        """Test finding Python import dependencies."""
        python_code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict
import requests
'''
        
        ast = self.parser.parse_code(python_code, 'python')
        dependencies = self.parser.find_dependencies(ast)
        
        assert len(dependencies) > 0
        
        dep_names = [dep.name for dep in dependencies]
        assert 'os' in dep_names
        assert 'sys' in dep_names
        assert 'pathlib' in dep_names or 'Path' in dep_names
    
    def test_find_javascript_dependencies(self):
        """Test finding JavaScript import dependencies."""
        js_code = '''
import React from 'react';
import { useState, useEffect } from 'react';
import axios from 'axios';
import './styles.css';
'''
        
        ast = self.parser.parse_code(js_code, 'javascript')
        dependencies = self.parser.find_dependencies(ast)
        
        assert len(dependencies) > 0
        
        dep_names = [dep.name for dep in dependencies]
        assert 'react' in dep_names
        assert 'axios' in dep_names
    
    def test_find_java_dependencies(self):
        """Test finding Java import dependencies."""
        java_code = '''
import java.util.List;
import java.util.ArrayList;
import java.io.IOException;
import com.example.MyClass;
'''
        
        ast = self.parser.parse_code(java_code, 'java')
        dependencies = self.parser.find_dependencies(ast)
        
        assert len(dependencies) > 0
        
        dep_names = [dep.name for dep in dependencies]
        assert any('java.util.List' in name for name in dep_names)
        assert any('java.util.ArrayList' in name for name in dep_names)
    
    def test_analyze_complexity_metrics(self):
        """Test complexity analysis."""
        complex_python_code = '''
def complex_function(data):
    result = 0
    
    for item in data:
        if item > 0:
            if item % 2 == 0:
                result += item * 2
            else:
                result += item
        elif item < 0:
            result -= abs(item)
        else:
            continue
    
    try:
        final_result = result / len(data)
    except ZeroDivisionError:
        final_result = 0
    
    return final_result
'''
        
        ast = self.parser.parse_code(complex_python_code, 'python')
        complexity = self.parser.analyze_complexity(ast)
        
        assert isinstance(complexity, ComplexityMetrics)
        assert complexity.cyclomatic_complexity > 1
        assert complexity.lines_of_code > 0
        assert 0 <= complexity.maintainability_index <= 100
    
    def test_analyze_file_with_temp_file(self):
        """Test analyzing a temporary file."""
        python_code = '''
def test_function(x, y):
    """Test function for file analysis."""
    return x + y

class TestClass:
    def test_method(self):
        return "test"
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(python_code)
            temp_file_path = f.name
        
        try:
            analysis = self.parser.analyze_file(temp_file_path)
            
            assert isinstance(analysis, CodeAnalysis)
            assert analysis.language == 'python'
            assert len(analysis.functions) == 2  # test_function and test_method
            assert len(analysis.classes) == 1
            func_names = [f.name for f in analysis.functions]
            assert 'test_function' in func_names
            assert 'test_method' in func_names
            assert analysis.classes[0].name == 'TestClass'
            
        finally:
            os.unlink(temp_file_path)
    
    def test_analyze_nonexistent_file(self):
        """Test error handling for nonexistent files."""
        with pytest.raises(FileNotFoundError):
            self.parser.analyze_file('nonexistent_file.py')
    
    def test_analyze_code_comprehensive(self):
        """Test comprehensive code analysis."""
        python_code = '''
import os
from typing import List

def calculate_average(numbers: List[int]) -> float:
    """Calculate the average of a list of numbers."""
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    total = sum(numbers)
    return total / len(numbers)

class Calculator:
    def __init__(self):
        self.history = []
    
    def add(self, a: int, b: int) -> int:
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def divide(self, a: int, b: int) -> float:
        if b == 0:
            raise ValueError("Cannot divide by zero")
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
'''
        
        analysis = self.parser.analyze_code(python_code, 'python')
        
        # Verify analysis structure
        assert isinstance(analysis, CodeAnalysis)
        assert analysis.language == 'python'
        
        # Check functions
        assert len(analysis.functions) == 4  # calculate_average, __init__, add, divide
        func_names = [f.name for f in analysis.functions]
        assert 'calculate_average' in func_names
        assert '__init__' in func_names
        assert 'add' in func_names
        assert 'divide' in func_names
        
        # Check classes
        assert len(analysis.classes) == 1
        assert analysis.classes[0].name == 'Calculator'
        assert len(analysis.classes[0].methods) == 3  # __init__, add, divide
        
        # Check dependencies
        assert len(analysis.dependencies) > 0
        dep_names = [dep.name for dep in analysis.dependencies]
        assert 'os' in dep_names
        
        # Check edge cases
        assert len(analysis.edge_cases) > 0
        
        # Check complexity metrics
        assert isinstance(analysis.complexity_metrics, ComplexityMetrics)
        assert analysis.complexity_metrics.cyclomatic_complexity > 0
    
    def test_ast_node_properties(self):
        """Test ASTNode wrapper properties."""
        python_code = 'def test(): pass'
        
        ast = self.parser.parse_code(python_code, 'python')
        
        assert ast.text == python_code
        assert ast.type == 'module'
        assert isinstance(ast.start_point, tuple)
        assert isinstance(ast.end_point, tuple)
        assert len(ast.start_point) == 2  # (row, column)
        assert len(ast.end_point) == 2
    
    def test_traverse_ast_functionality(self):
        """Test AST traversal functionality."""
        python_code = '''
def func1():
    pass

def func2():
    pass
'''
        
        ast = self.parser.parse_code(python_code, 'python')
        function_nodes = self.parser._traverse_ast(ast.node, ast.source_code, 'function_definition')
        
        assert len(function_nodes) == 2
        assert all(isinstance(node, ASTNode) for node in function_nodes)
        assert all(node.type == 'function_definition' for node in function_nodes)
    
    def test_error_handling_invalid_syntax(self):
        """Test handling of code with syntax errors."""
        invalid_python = '''
def broken_function(
    # Missing closing parenthesis and colon
    return "this won't parse"
'''
        
        # Should still create AST but with errors
        ast = self.parser.parse_code(invalid_python, 'python')
        assert ast.node.has_error
    
    def test_parameter_extraction_with_defaults(self):
        """Test extraction of function parameters with default values."""
        python_code = '''
def function_with_defaults(a, b=10, c="default", d=None):
    return a + b
'''
        
        ast = self.parser.parse_code(python_code, 'python')
        functions = self.parser.identify_functions(ast)
        
        assert len(functions) == 1
        func = functions[0]
        assert func.name == 'function_with_defaults'
        assert len(func.parameters) == 4
        
        param_names = [p.name for p in func.parameters]
        assert 'a' in param_names
        assert 'b' in param_names
        assert 'c' in param_names
        assert 'd' in param_names


class TestCodeParserIntegration:
    """Integration tests for CodeParser with real code examples."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CodeParser()
    
    def test_analyze_real_python_module(self):
        """Test analysis of a realistic Python module."""
        python_module = '''
"""
A sample calculator module for testing.
"""
import math
from typing import List, Optional

class ScientificCalculator:
    """A calculator with scientific functions."""
    
    def __init__(self):
        self.memory = 0.0
        self.history: List[str] = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self._record_operation(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a: float, b: float) -> float:
        """Multiply two numbers."""
        result = a * b
        self._record_operation(f"{a} * {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Division by zero")
        result = a / b
        self._record_operation(f"{a} / {b} = {result}")
        return result
    
    def power(self, base: float, exponent: float) -> float:
        """Calculate power."""
        result = math.pow(base, exponent)
        self._record_operation(f"{base} ^ {exponent} = {result}")
        return result
    
    def sqrt(self, x: float) -> float:
        """Calculate square root."""
        if x < 0:
            raise ValueError("Cannot calculate square root of negative number")
        result = math.sqrt(x)
        self._record_operation(f"sqrt({x}) = {result}")
        return result
    
    def _record_operation(self, operation: str) -> None:
        """Record operation in history."""
        self.history.append(operation)
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self) -> None:
        """Clear calculation history."""
        self.history.clear()

def calculate_statistics(numbers: List[float]) -> dict:
    """Calculate basic statistics for a list of numbers."""
    if not numbers:
        return {"error": "Empty list"}
    
    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    
    # Calculate variance
    variance = sum((x - mean) ** 2 for x in numbers) / count
    std_dev = math.sqrt(variance)
    
    return {
        "count": count,
        "sum": total,
        "mean": mean,
        "variance": variance,
        "std_dev": std_dev,
        "min": min(numbers),
        "max": max(numbers)
    }
'''
        
        analysis = self.parser.analyze_code(python_module, 'python')
        
        # Verify comprehensive analysis
        assert analysis.language == 'python'
        
        # Check functions (class methods + standalone function)
        assert len(analysis.functions) >= 8  # All methods + calculate_statistics
        
        # Check classes
        assert len(analysis.classes) == 1
        calc_class = analysis.classes[0]
        assert calc_class.name == 'ScientificCalculator'
        assert len(calc_class.methods) >= 7
        
        # Check dependencies
        dep_names = [dep.name for dep in analysis.dependencies]
        assert 'math' in dep_names
        
        # Check edge cases (division by zero, negative sqrt, etc.)
        assert len(analysis.edge_cases) > 0
        
        # Check complexity
        assert analysis.complexity_metrics.cyclomatic_complexity > 1
        assert analysis.complexity_metrics.lines_of_code > 50
    
    def test_analyze_real_javascript_module(self):
        """Test analysis of a realistic JavaScript module."""
        js_module = '''
/**
 * User management utilities
 */

class UserManager {
    constructor() {
        this.users = new Map();
        this.nextId = 1;
    }
    
    addUser(name, email) {
        if (!name || !email) {
            throw new Error('Name and email are required');
        }
        
        const user = {
            id: this.nextId++,
            name: name,
            email: email,
            createdAt: new Date()
        };
        
        this.users.set(user.id, user);
        return user;
    }
    
    getUser(id) {
        const user = this.users.get(id);
        if (!user) {
            return null;
        }
        return { ...user };
    }
    
    updateUser(id, updates) {
        const user = this.users.get(id);
        if (!user) {
            throw new Error('User not found');
        }
        
        Object.assign(user, updates);
        return { ...user };
    }
    
    deleteUser(id) {
        return this.users.delete(id);
    }
    
    getAllUsers() {
        return Array.from(this.users.values());
    }
}

function validateEmail(email) {
    const emailRegex = /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/;
    return emailRegex.test(email);
}

const formatUserName = (firstName, lastName) => {
    if (!firstName && !lastName) {
        return 'Anonymous';
    }
    return `${firstName || ''} ${lastName || ''}`.trim();
};

async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Failed to fetch user data:', error);
        return null;
    }
}
'''
        
        analysis = self.parser.analyze_code(js_module, 'javascript')
        
        # Verify analysis
        assert analysis.language == 'javascript'
        
        # Check functions (methods + standalone functions)
        assert len(analysis.functions) >= 8
        
        # Check classes
        assert len(analysis.classes) == 1
        user_class = analysis.classes[0]
        assert user_class.name == 'UserManager'
        
        # Check edge cases (null checks, error handling)
        assert len(analysis.edge_cases) > 0
    
    def test_analyze_real_java_class(self):
        """Test analysis of a realistic Java class."""
        java_class = '''
package com.example.utils;

import java.util.*;
import java.io.IOException;

/**
 * A utility class for string operations
 */
public class StringUtils {
    
    private static final String DEFAULT_DELIMITER = ",";
    
    public static boolean isEmpty(String str) {
        return str == null || str.trim().isEmpty();
    }
    
    public static boolean isNotEmpty(String str) {
        return !isEmpty(str);
    }
    
    public static String join(List<String> strings, String delimiter) {
        if (strings == null || strings.isEmpty()) {
            return "";
        }
        
        if (delimiter == null) {
            delimiter = DEFAULT_DELIMITER;
        }
        
        StringBuilder result = new StringBuilder();
        for (int i = 0; i < strings.size(); i++) {
            if (i > 0) {
                result.append(delimiter);
            }
            result.append(strings.get(i));
        }
        
        return result.toString();
    }
    
    public static List<String> split(String input, String delimiter) {
        if (isEmpty(input)) {
            return new ArrayList<>();
        }
        
        if (delimiter == null) {
            delimiter = DEFAULT_DELIMITER;
        }
        
        return Arrays.asList(input.split(delimiter));
    }
    
    public static String capitalize(String str) {
        if (isEmpty(str)) {
            return str;
        }
        
        return str.substring(0, 1).toUpperCase() + str.substring(1).toLowerCase();
    }
    
    public static String reverse(String str) {
        if (isEmpty(str)) {
            return str;
        }
        
        return new StringBuilder(str).reverse().toString();
    }
    
    public static int countOccurrences(String text, String substring) {
        if (isEmpty(text) || isEmpty(substring)) {
            return 0;
        }
        
        int count = 0;
        int index = 0;
        
        while ((index = text.indexOf(substring, index)) != -1) {
            count++;
            index += substring.length();
        }
        
        return count;
    }
}
'''
        
        analysis = self.parser.analyze_code(java_class, 'java')
        
        # Verify analysis
        assert analysis.language == 'java'
        
        # Check methods
        assert len(analysis.functions) >= 7
        method_names = [f.name for f in analysis.functions]
        assert 'isEmpty' in method_names
        assert 'join' in method_names
        assert 'split' in method_names
        
        # Check classes
        assert len(analysis.classes) == 1
        string_utils_class = analysis.classes[0]
        assert string_utils_class.name == 'StringUtils'
        
        # Check dependencies
        dep_names = [dep.name for dep in analysis.dependencies]
        assert any('java.util' in name for name in dep_names)
        
        # Check edge cases (null checks, empty string handling)
        assert len(analysis.edge_cases) > 0


if __name__ == '__main__':
    pytest.main([__file__])