"""
Unit tests for TestGenerator with AI integration
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List, Dict, Any

from src.generators.test_generator import TestGenerator
from src.interfaces.base_interfaces import (
    TestCase, TestSuite, TestType, Language, 
    FunctionInfo, Parameter, EdgeCase, Dependency
)
from src.config.ai_provider_manager import AIProviderManager


class MockAnalysisResult:
    """Mock analysis result for testing."""
    def __init__(self, language='python', functions=None, edge_cases=None, imports=None):
        self.language = language
        self.functions = functions or []
        self.edge_cases = edge_cases or []
        self.imports = imports or []


class MockAIProvider:
    """Mock AI provider for testing."""
    
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
        self.enhance_calls = []
        self.analysis_calls = []
    
    def enhance_test_case(self, test: TestCase, context: Dict[str, Any]) -> Dict[str, Any]:
        self.enhance_calls.append((test, context))
        
        if self.should_fail:
            raise Exception("Mock AI provider failure")
        
        return {
            'code': f"# AI Enhanced\n{test.test_code}",
            'description': f"AI Enhanced: {test.description}",
            'assertions': ['assert result is not None', 'assert isinstance(result, expected_type)']
        }
    
    def analyze_code_patterns(self, code: str, language: str) -> Dict[str, Any]:
        self.analysis_calls.append((code, language))
        
        if self.should_fail:
            raise Exception("Mock AI analysis failure")
        
        return {
            'analysis': f'Mock analysis for {language} code',
            'provider': 'mock'
        }
    
    def suggest_test_improvements(self, test: TestCase, context: Dict[str, Any]) -> str:
        return "Mock improvement suggestions"


@pytest.fixture
def mock_ai_provider():
    """Create a mock AI provider."""
    return MockAIProvider()


@pytest.fixture
def failing_ai_provider():
    """Create a failing mock AI provider."""
    return MockAIProvider(should_fail=True)


@pytest.fixture
def mock_ai_provider_manager(mock_ai_provider):
    """Create a mock AI provider manager."""
    manager = Mock(spec=AIProviderManager)
    manager.get_provider.return_value = mock_ai_provider
    return manager


@pytest.fixture
def sample_function():
    """Create a sample function for testing."""
    return FunctionInfo(
        name="calculate_sum",
        parameters=[
            Parameter(name="a", type_hint="int"),
            Parameter(name="b", type_hint="int")
        ],
        return_type="int",
        complexity=2,
        line_range=(1, 5),
        docstring="Calculate the sum of two numbers"
    )


@pytest.fixture
def sample_analysis(sample_function):
    """Create a sample analysis result."""
    return MockAnalysisResult(
        language='python',
        functions=[sample_function],
        edge_cases=[
            EdgeCase(type="null_check", location="line 2", description="Null input check", severity=3)
        ],
        imports=['import math', 'import os']
    )


class TestTestGenerator:
    """Test cases for TestGenerator class."""
    
    def test_init_with_ai_provider_manager(self, mock_ai_provider_manager):
        """Test TestGenerator initialization with AI provider manager."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        assert generator.ai_provider_manager == mock_ai_provider_manager
        assert generator.ai_provider is not None
        assert 'python' in generator.test_frameworks
        assert 'javascript' in generator.test_frameworks
        assert 'java' in generator.test_frameworks
    
    def test_init_without_ai_provider_manager(self):
        """Test TestGenerator initialization without AI provider manager."""
        with patch('src.generators.test_generator.AIProviderManager') as mock_manager_class:
            mock_manager = Mock()
            mock_provider = Mock()
            mock_manager.get_provider.return_value = mock_provider
            mock_manager_class.return_value = mock_manager
            
            generator = TestGenerator()
            
            assert generator.ai_provider_manager == mock_manager
            assert generator.ai_provider == mock_provider
    
    def test_generate_tests_returns_test_suite(self, mock_ai_provider_manager, sample_analysis):
        """Test that generate_tests returns a TestSuite object."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        result = generator.generate_tests(sample_analysis)
        
        assert isinstance(result, TestSuite)
        assert result.language == Language.PYTHON
        assert result.framework == 'pytest'
        assert len(result.test_cases) > 0
        assert result.setup_code is not None
        assert result.teardown_code is not None
    
    def test_generate_tests_with_ai_enhancement(self, mock_ai_provider_manager, sample_analysis, mock_ai_provider):
        """Test that tests are enhanced with AI."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        result = generator.generate_tests(sample_analysis)
        
        # Verify AI provider was called
        assert len(mock_ai_provider.analysis_calls) > 0
        assert len(mock_ai_provider.enhance_calls) > 0
        
        # Verify enhanced test content
        enhanced_test = result.test_cases[0]
        assert "AI Enhanced" in enhanced_test.test_code
        assert "AI Enhanced" in enhanced_test.description
    
    def test_generate_tests_handles_ai_failure(self, sample_analysis):
        """Test that generator handles AI provider failures gracefully."""
        failing_manager = Mock(spec=AIProviderManager)
        failing_provider = MockAIProvider(should_fail=True)
        failing_manager.get_provider.return_value = failing_provider
        
        generator = TestGenerator(failing_manager)
        
        # Should not raise exception despite AI failure
        result = generator.generate_tests(sample_analysis)
        
        assert isinstance(result, TestSuite)
        assert len(result.test_cases) > 0
    
    def test_generate_unit_tests_interface_method(self, mock_ai_provider_manager, sample_function):
        """Test the generate_unit_tests interface method."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        result = generator.generate_unit_tests([sample_function])
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(test, TestCase) for test in result)
        assert all(test.test_type == TestType.UNIT for test in result)
    
    def test_generate_integration_tests_interface_method(self, mock_ai_provider_manager):
        """Test the generate_integration_tests interface method."""
        from src.interfaces.base_interfaces import Dependency
        
        generator = TestGenerator(mock_ai_provider_manager)
        
        # Create a proper Dependency object instead of a Mock
        test_dependency = Dependency(name="database", type="database", source="import database")
        dependencies = [test_dependency]
        
        result = generator.generate_integration_tests(dependencies)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(test, TestCase) for test in result)
        assert all(test.test_type == TestType.INTEGRATION for test in result)
    
    def test_generate_edge_case_tests_interface_method(self, mock_ai_provider_manager):
        """Test the generate_edge_case_tests interface method."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        edge_case = EdgeCase(
            type="null_check", 
            location="line 5", 
            description="Null input validation", 
            severity=3
        )
        edge_cases = [edge_case]
        
        result = generator.generate_edge_case_tests(edge_cases)
        
        assert isinstance(result, list)
        assert len(result) > 0
        assert all(isinstance(test, TestCase) for test in result)
        assert all(test.test_type == TestType.EDGE for test in result)
    
    def test_format_tests_python(self, mock_ai_provider_manager):
        """Test formatting tests for Python."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        test_case = TestCase(
            name="test_example",
            test_type=TestType.UNIT,
            function_name="example",
            description="Example test",
            test_code="def test_example():\n    assert True",
            requirements_covered=[]
        )
        
        result = generator.format_tests([test_case], Language.PYTHON)
        
        assert "import pytest" in result
        assert "from unittest.mock import Mock, patch" in result
        assert "def test_example():" in result
    
    def test_format_tests_javascript(self, mock_ai_provider_manager):
        """Test formatting tests for JavaScript."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        test_case = TestCase(
            name="test_example",
            test_type=TestType.UNIT,
            function_name="example",
            description="Example test",
            test_code="test('example', () => { expect(true).toBe(true); });",
            requirements_covered=[]
        )
        
        result = generator.format_tests([test_case], Language.JAVASCRIPT)
        
        assert "const { describe, test, expect, jest }" in result
        assert "test('example'" in result
    
    def test_format_tests_java(self, mock_ai_provider_manager):
        """Test formatting tests for Java."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        test_case = TestCase(
            name="testExample",
            test_type=TestType.UNIT,
            function_name="example",
            description="Example test",
            test_code="@Test\npublic void testExample() {\n    assertTrue(true);\n}",
            requirements_covered=[]
        )
        
        result = generator.format_tests([test_case], Language.JAVA)
        
        assert "import org.junit.jupiter.api.Test;" in result
        assert "import static org.junit.jupiter.api.Assertions.*;" in result
        assert "@Test" in result
    
    def test_get_ai_code_analysis(self, mock_ai_provider_manager, sample_analysis, mock_ai_provider):
        """Test AI code analysis functionality."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        result = generator._get_ai_code_analysis(sample_analysis)
        
        assert isinstance(result, dict)
        assert 'analysis' in result
        assert 'provider' in result
        assert len(mock_ai_provider.analysis_calls) == 1
    
    def test_get_ai_code_analysis_handles_failure(self, sample_analysis):
        """Test AI code analysis handles failures gracefully."""
        failing_manager = Mock(spec=AIProviderManager)
        failing_provider = MockAIProvider(should_fail=True)
        failing_manager.get_provider.return_value = failing_provider
        
        generator = TestGenerator(failing_manager)
        
        result = generator._get_ai_code_analysis(sample_analysis)
        
        assert isinstance(result, dict)
        assert result['analysis'] == 'AI analysis unavailable'
        assert result['provider'] == 'none'
    
    def test_enhance_tests_with_ai(self, mock_ai_provider_manager, sample_analysis, mock_ai_provider):
        """Test AI enhancement of test cases."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        original_test = TestCase(
            name="test_original",
            test_type=TestType.UNIT,
            function_name="original",
            description="Original test",
            test_code="def test_original():\n    assert True",
            requirements_covered=[]
        )
        
        ai_analysis = {'analysis': 'Mock analysis'}
        
        result = generator._enhance_tests_with_ai([original_test], sample_analysis, ai_analysis)
        
        assert len(result) == 1
        enhanced_test = result[0]
        assert "AI Enhanced" in enhanced_test.test_code
        assert "AI Enhanced" in enhanced_test.description
        assert len(mock_ai_provider.enhance_calls) == 1
    
    def test_enhance_tests_with_ai_handles_failure(self, sample_analysis):
        """Test AI enhancement handles failures gracefully."""
        failing_manager = Mock(spec=AIProviderManager)
        failing_provider = MockAIProvider(should_fail=True)
        failing_manager.get_provider.return_value = failing_provider
        
        generator = TestGenerator(failing_manager)
        
        original_test = TestCase(
            name="test_original",
            test_type=TestType.UNIT,
            function_name="original",
            description="Original test",
            test_code="def test_original():\n    assert True",
            requirements_covered=[]
        )
        
        ai_analysis = {'analysis': 'Mock analysis'}
        
        result = generator._enhance_tests_with_ai([original_test], sample_analysis, ai_analysis)
        
        assert len(result) == 1
        # Should return original test when AI fails
        assert result[0].test_code == original_test.test_code
    
    def test_reconstruct_code_from_analysis(self, mock_ai_provider_manager, sample_analysis):
        """Test code reconstruction from analysis."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        result = generator._reconstruct_code_from_analysis(sample_analysis)
        
        assert isinstance(result, str)
        assert "import math" in result
        assert "def calculate_sum" in result
        assert "Calculate the sum of two numbers" in result
    
    def test_identify_performance_risks(self, mock_ai_provider_manager, sample_analysis):
        """Test performance risk identification."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        # Add a high complexity function
        high_complexity_func = FunctionInfo(
            name="complex_loop_function",
            parameters=[],
            return_type="int",
            complexity=15,
            line_range=(10, 20)
        )
        sample_analysis.functions.append(high_complexity_func)
        
        result = generator._identify_performance_risks(sample_analysis)
        
        assert isinstance(result, list)
        assert any("High complexity" in risk for risk in result)
        assert any("complex_loop_function" in risk for risk in result)
    
    def test_generate_setup_code_for_language(self, mock_ai_provider_manager):
        """Test setup code generation for different languages."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        python_setup = generator._generate_setup_code_for_language('python')
        assert "import sys" in python_setup
        assert "import os" in python_setup
        
        js_setup = generator._generate_setup_code_for_language('javascript')
        assert "beforeEach" in js_setup
        
        java_setup = generator._generate_setup_code_for_language('java')
        assert "@BeforeEach" in java_setup
        
        unknown_setup = generator._generate_setup_code_for_language('unknown')
        assert unknown_setup is None
    
    def test_generate_teardown_code_for_language(self, mock_ai_provider_manager):
        """Test teardown code generation for different languages."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        python_teardown = generator._generate_teardown_code_for_language('python')
        assert "# Test teardown" in python_teardown
        
        js_teardown = generator._generate_teardown_code_for_language('javascript')
        assert "afterEach" in js_teardown
        
        java_teardown = generator._generate_teardown_code_for_language('java')
        assert "@AfterEach" in java_teardown
        
        unknown_teardown = generator._generate_teardown_code_for_language('unknown')
        assert unknown_teardown is None
    
    def test_generate_basic_integration_test(self, mock_ai_provider_manager):
        """Test basic integration test generation."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        result = generator._generate_basic_integration_test("Database Connection")
        
        assert "def test_integration_database_connection" in result
        assert "Integration test for Database Connection" in result
        assert "assert True" in result
    
    def test_generate_basic_edge_test(self, mock_ai_provider_manager):
        """Test basic edge case test generation."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        result = generator._generate_basic_edge_test("Null Input Validation")
        
        assert "def test_edge_null_input_validation" in result
        assert "Edge case test for Null Input Validation" in result
        assert "assert True" in result


class TestTestGeneratorIntegration:
    """Integration tests for TestGenerator with real AI provider manager."""
    
    @patch('src.generators.test_generator.AIProviderManager')
    def test_integration_with_real_ai_provider_manager(self, mock_manager_class, sample_analysis):
        """Test integration with real AI provider manager."""
        # Setup mock manager
        mock_manager = Mock()
        mock_provider = MockAIProvider()
        mock_manager.get_provider.return_value = mock_provider
        mock_manager_class.return_value = mock_manager
        
        generator = TestGenerator()
        result = generator.generate_tests(sample_analysis)
        
        assert isinstance(result, TestSuite)
        assert len(result.test_cases) > 0
        assert mock_manager_class.called
        assert mock_manager.get_provider.called
    
    def test_prompt_engineering_context(self, mock_ai_provider_manager, sample_analysis, mock_ai_provider):
        """Test that proper context is passed to AI provider for prompt engineering."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        generator.generate_tests(sample_analysis)
        
        # Verify AI provider received proper context
        assert len(mock_ai_provider.enhance_calls) > 0
        
        for test, context in mock_ai_provider.enhance_calls:
            assert 'language' in context
            assert 'edge_cases' in context
            assert 'performance_risks' in context
            assert 'ai_insights' in context
            assert context['language'] == 'python'
    
    def test_language_specific_framework_selection(self, mock_ai_provider_manager):
        """Test that correct frameworks are selected for different languages."""
        generator = TestGenerator(mock_ai_provider_manager)
        
        # Test Python
        python_analysis = MockAnalysisResult(language='python')
        python_result = generator.generate_tests(python_analysis)
        assert python_result.framework == 'pytest'
        
        # Test JavaScript
        js_analysis = MockAnalysisResult(language='javascript')
        js_result = generator.generate_tests(js_analysis)
        assert js_result.framework == 'jest'
        
        # Test Java
        java_analysis = MockAnalysisResult(language='java')
        java_result = generator.generate_tests(java_analysis)
        assert java_result.framework == 'junit'


if __name__ == '__main__':
    pytest.main([__file__])