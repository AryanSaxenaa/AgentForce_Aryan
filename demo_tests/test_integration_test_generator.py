"""
Unit tests for IntegrationTestGenerator
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.generators.integration_test_generator import (
    IntegrationTestGenerator, MockStrategyGenerator, MockStrategy, IntegrationScenario
)
from src.interfaces.base_interfaces import (
    FunctionInfo, Parameter, TestCase, TestType, Language, Dependency, EdgeCase
)


class TestMockStrategyGenerator:
    """Test cases for MockStrategyGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = MockStrategyGenerator()
    
    def test_generate_database_mock_python(self):
        """Test database mock generation for Python."""
        dependency = Dependency(name="sqlite3", type="database", source="import sqlite3")
        
        strategy = self.generator.generate_mock_strategy(dependency, "python")
        
        assert strategy.dependency_name == "sqlite3"
        assert strategy.mock_type == "patch"
        assert "mock_db" in strategy.mock_setup
        assert "mock_cursor" in strategy.mock_setup
        assert "fetchall" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 2
        assert "mock_db.cursor.assert_called()" in strategy.mock_assertions
    
    def test_generate_database_mock_javascript(self):
        """Test database mock generation for JavaScript."""
        dependency = Dependency(name="mysql", type="database", source="const mysql = require('mysql')")
        
        strategy = self.generator.generate_mock_strategy(dependency, "javascript")
        
        assert strategy.dependency_name == "mysql"
        assert strategy.mock_type == "mock_object"
        assert "mockDb" in strategy.mock_setup
        assert "jest.fn()" in strategy.mock_setup
        assert "query" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 2
        assert "expect(mockDb.connect).toHaveBeenCalled();" in strategy.mock_assertions
    
    def test_generate_database_mock_java(self):
        """Test database mock generation for Java."""
        dependency = Dependency(name="java.sql.Connection", type="database", source="import java.sql.Connection")
        
        strategy = self.generator.generate_mock_strategy(dependency, "java")
        
        assert strategy.dependency_name == "java.sql.Connection"
        assert strategy.mock_type == "mock_object"
        assert "Mockito.mock" in strategy.mock_setup
        assert "Connection" in strategy.mock_setup
        assert "PreparedStatement" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 2
        assert any("verify(mockConnection)" in assertion for assertion in strategy.mock_assertions)
    
    def test_generate_http_mock_python(self):
        """Test HTTP mock generation for Python."""
        dependency = Dependency(name="requests", type="http_client", source="import requests")
        
        strategy = self.generator.generate_mock_strategy(dependency, "python")
        
        assert strategy.dependency_name == "requests"
        assert strategy.mock_type == "patch"
        assert "mock_response" in strategy.mock_setup
        assert "status_code" in strategy.mock_setup
        assert "json" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 2
        assert "mock_response.raise_for_status.assert_called()" in strategy.mock_assertions
    
    def test_generate_http_mock_javascript(self):
        """Test HTTP mock generation for JavaScript."""
        dependency = Dependency(name="axios", type="http_client", source="const axios = require('axios')")
        
        strategy = self.generator.generate_mock_strategy(dependency, "javascript")
        
        assert strategy.dependency_name == "axios"
        assert strategy.mock_type == "mock_object"
        assert "mockHttpClient" in strategy.mock_setup
        assert "get:" in strategy.mock_setup
        assert "post:" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 2
        assert "expect(mockHttpClient.get).toHaveBeenCalled();" in strategy.mock_assertions
    
    def test_generate_file_mock_python(self):
        """Test file system mock generation for Python."""
        dependency = Dependency(name="open", type="file_operation", source="with open('file.txt') as f:")
        
        strategy = self.generator.generate_mock_strategy(dependency, "python")
        
        assert strategy.dependency_name == "open"
        assert strategy.mock_type == "patch"
        assert "mock_file" in strategy.mock_setup
        assert "read" in strategy.mock_setup
        assert "write" in strategy.mock_setup
        assert "__enter__" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 2
        assert "mock_file.read.assert_called()" in strategy.mock_assertions
    
    def test_generate_external_call_mock_python(self):
        """Test external call mock generation for Python."""
        dependency = Dependency(name="external_api", type="external_call", source="external_api.call()")
        
        strategy = self.generator.generate_mock_strategy(dependency, "python")
        
        assert strategy.dependency_name == "external_api"
        assert strategy.mock_type == "patch"
        assert "mock_service" in strategy.mock_setup
        assert "return_value" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 2
        assert "mock_service.assert_called()" in strategy.mock_assertions
    
    def test_generate_generic_mock_python(self):
        """Test generic mock generation for Python."""
        dependency = Dependency(name="unknown.module", type="unknown", source="import unknown.module")
        
        strategy = self.generator.generate_mock_strategy(dependency, "python")
        
        assert strategy.dependency_name == "unknown.module"
        assert strategy.mock_type == "patch"
        assert "mock_unknown_module" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 1
        assert "mock_unknown_module.assert_called()" in strategy.mock_assertions
    
    def test_generate_generic_mock_unsupported_language(self):
        """Test generic mock generation for unsupported language."""
        dependency = Dependency(name="test.module", type="unknown", source="import test.module")
        
        strategy = self.generator.generate_mock_strategy(dependency, "unsupported")
        
        assert strategy.dependency_name == "test.module"
        assert strategy.mock_type == "generic"
        assert "Mock setup for test.module" in strategy.mock_setup
        assert len(strategy.mock_assertions) >= 1
        assert "// Verify test.module interactions" in strategy.mock_assertions


class TestIntegrationTestGenerator:
    """Test cases for IntegrationTestGenerator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = IntegrationTestGenerator()
        
        # Create sample function info
        self.sample_function = FunctionInfo(
            name="process_data",
            parameters=[
                Parameter(name="data", type_hint="dict"),
                Parameter(name="config", type_hint="dict")
            ],
            return_type="dict",
            complexity=5,
            line_range=(10, 25),
            docstring="Process data with external dependencies"
        )
        
        # Create sample dependencies
        self.sample_dependencies = [
            Dependency(name="sqlite3", type="database", source="import sqlite3"),
            Dependency(name="requests", type="http_client", source="import requests"),
            Dependency(name="open", type="file_operation", source="with open('file.txt') as f:")
        ]
        
        # Create sample edge cases
        self.sample_edge_cases = [
            EdgeCase(
                type="database_dependency",
                location="line 15",
                description="Database connection may fail",
                severity=3
            ),
            EdgeCase(
                type="network_dependency",
                location="line 20",
                description="HTTP request may timeout",
                severity=2
            )
        ]
    
    def test_generate_integration_tests_with_dependencies(self):
        """Test integration test generation with dependencies."""
        test_cases = self.generator.generate_integration_tests(
            self.sample_function, self.sample_dependencies, "python", self.sample_edge_cases
        )
        
        assert len(test_cases) > 0
        assert all(isinstance(tc, TestCase) for tc in test_cases)
        assert all(tc.test_type == TestType.INTEGRATION for tc in test_cases)
        assert all(tc.function_name == "process_data" for tc in test_cases)
        
        # Check that we have different scenarios
        test_names = [tc.name for tc in test_cases]
        assert any("happy_path" in name for name in test_names)
        assert any("database_failure" in name for name in test_names)
        assert any("network_failure" in name for name in test_names)
    
    def test_generate_integration_tests_no_dependencies(self):
        """Test integration test generation with no dependencies."""
        test_cases = self.generator.generate_integration_tests(
            self.sample_function, [], "python"
        )
        
        assert len(test_cases) == 0
    
    def test_generate_dependency_injection_tests(self):
        """Test dependency injection test generation."""
        test_cases = self.generator.generate_dependency_injection_tests(
            self.sample_function, self.sample_dependencies, "python"
        )
        
        assert len(test_cases) == 3  # successful, missing, invalid
        assert all(isinstance(tc, TestCase) for tc in test_cases)
        assert all(tc.test_type == TestType.INTEGRATION for tc in test_cases)
        
        test_names = [tc.name for tc in test_cases]
        assert any("successful_injection" in name for name in test_names)
        assert any("missing_dependency" in name for name in test_names)
        assert any("invalid_dependency" in name for name in test_names)
    
    def test_generate_mock_object_tests(self):
        """Test mock object test generation."""
        test_cases = self.generator.generate_mock_object_tests(
            self.sample_function, self.sample_dependencies, "python"
        )
        
        assert len(test_cases) == len(self.sample_dependencies)
        assert all(isinstance(tc, TestCase) for tc in test_cases)
        assert all(tc.test_type == TestType.INTEGRATION for tc in test_cases)
        
        # Check that each dependency has a corresponding test
        test_names = [tc.name for tc in test_cases]
        assert any("mock_sqlite3" in name for name in test_names)
        assert any("mock_requests" in name for name in test_names)
        assert any("mock_open" in name for name in test_names)
    
    def test_group_dependencies_by_type(self):
        """Test dependency grouping by type."""
        groups = self.generator._group_dependencies_by_type(self.sample_dependencies)
        
        assert "database" in groups
        assert "http_client" in groups
        assert "file_operation" in groups
        assert len(groups["database"]) == 1
        assert len(groups["http_client"]) == 1
        assert len(groups["file_operation"]) == 1
    
    def test_generate_integration_scenarios(self):
        """Test integration scenario generation."""
        dependency_groups = self.generator._group_dependencies_by_type(self.sample_dependencies)
        scenarios = self.generator._generate_integration_scenarios(
            self.sample_function, dependency_groups, self.sample_edge_cases
        )
        
        assert len(scenarios) > 0
        assert all(isinstance(s, IntegrationScenario) for s in scenarios)
        
        scenario_names = [s.name for s in scenarios]
        assert "happy_path_integration" in scenario_names
        assert "database_failure_integration" in scenario_names
        assert "network_failure_integration" in scenario_names
        assert "partial_dependency_failure" in scenario_names
    
    def test_flatten_dependency_groups(self):
        """Test dependency group flattening."""
        dependency_groups = {
            "database": [self.sample_dependencies[0]],
            "http_client": [self.sample_dependencies[1]],
            "file_operation": [self.sample_dependencies[2]]
        }
        
        flattened = self.generator._flatten_dependency_groups(dependency_groups)
        
        assert len(flattened) == 3
        assert all(isinstance(d, Dependency) for d in flattened)
        assert flattened == self.sample_dependencies
    
    def test_generate_test_case_for_scenario_python(self):
        """Test test case generation for a specific scenario in Python."""
        scenario = IntegrationScenario(
            name="test_scenario",
            description="Test scenario description",
            dependencies=self.sample_dependencies[:1],  # Just one dependency
            mock_strategies=[],
            setup_requirements=["Test setup"],
            expected_interactions=["Test interaction"]
        )
        
        test_case = self.generator._generate_test_case_for_scenario(
            self.sample_function, scenario, "python"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert test_case.function_name == "process_data"
        assert "test_process_data_test_scenario" in test_case.name
        assert "def test_process_data_test_scenario" in test_case.test_code
        assert "# Arrange" in test_case.test_code
        assert "# Act" in test_case.test_code
        assert "# Assert" in test_case.test_code
    
    def test_generate_test_case_for_scenario_javascript(self):
        """Test test case generation for a specific scenario in JavaScript."""
        scenario = IntegrationScenario(
            name="test_scenario",
            description="Test scenario description",
            dependencies=self.sample_dependencies[:1],
            mock_strategies=[],
            setup_requirements=["Test setup"],
            expected_interactions=["Test interaction"]
        )
        
        test_case = self.generator._generate_test_case_for_scenario(
            self.sample_function, scenario, "javascript"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert "describe(" in test_case.test_code
        assert "test(" in test_case.test_code
        assert "// Arrange" in test_case.test_code
        assert "// Act" in test_case.test_code
        assert "// Assert" in test_case.test_code
    
    def test_generate_test_case_for_scenario_java(self):
        """Test test case generation for a specific scenario in Java."""
        scenario = IntegrationScenario(
            name="test_scenario",
            description="Test scenario description",
            dependencies=self.sample_dependencies[:1],
            mock_strategies=[],
            setup_requirements=["Test setup"],
            expected_interactions=["Test interaction"]
        )
        
        test_case = self.generator._generate_test_case_for_scenario(
            self.sample_function, scenario, "java"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert "@Test" in test_case.test_code
        assert "public void" in test_case.test_code
        assert "// Arrange" in test_case.test_code
        assert "// Act" in test_case.test_code
        assert "// Assert" in test_case.test_code
    
    def test_generate_successful_injection_test_python(self):
        """Test successful injection test generation for Python."""
        test_case = self.generator._generate_successful_injection_test(
            self.sample_function, self.sample_dependencies, "python"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert "successful_injection" in test_case.name
        assert "def test_process_data_successful_injection" in test_case.test_code
        assert "assert result is not None" in test_case.test_code
    
    def test_generate_missing_dependency_test_python(self):
        """Test missing dependency test generation for Python."""
        test_case = self.generator._generate_missing_dependency_test(
            self.sample_function, self.sample_dependencies, "python"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert "missing_dependency" in test_case.name
        assert "with pytest.raises" in test_case.test_code
        assert "None" in test_case.test_code
    
    def test_generate_missing_dependency_test_javascript(self):
        """Test missing dependency test generation for JavaScript."""
        test_case = self.generator._generate_missing_dependency_test(
            self.sample_function, self.sample_dependencies, "javascript"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert "missing_dependency" in test_case.name
        assert "expect(() =>" in test_case.test_code
        assert "toThrow()" in test_case.test_code
        assert "null" in test_case.test_code
    
    def test_generate_invalid_dependency_test_java(self):
        """Test invalid dependency test generation for Java."""
        test_case = self.generator._generate_invalid_dependency_test(
            self.sample_function, self.sample_dependencies, "java"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert "invalid_dependency" in test_case.name
        assert "assertThrows" in test_case.test_code
        assert "ClassCastException" in test_case.test_code
    
    def test_generate_mock_verification_test(self):
        """Test mock verification test generation."""
        dependency = self.sample_dependencies[0]  # sqlite3
        mock_strategy = MockStrategy(
            dependency_name="sqlite3",
            mock_type="patch",
            mock_setup="mock_setup_code",
            mock_assertions=["assertion1", "assertion2"],
            teardown_code="cleanup_code"
        )
        
        test_case = self.generator._generate_mock_verification_test(
            self.sample_function, dependency, mock_strategy, "python"
        )
        
        assert isinstance(test_case, TestCase)
        assert test_case.test_type == TestType.INTEGRATION
        assert "mock_sqlite3" in test_case.name
        assert "mock_setup_code" in test_case.test_code
        assert "assertion1" in test_case.test_code
        assert "assertion2" in test_case.test_code
        assert "cleanup_code" in test_case.test_code
    
    def test_generate_mock_setups(self):
        """Test mock setup code generation."""
        mock_strategies = [
            MockStrategy("dep1", "patch", "setup1", ["assert1"], "cleanup1"),
            MockStrategy("dep2", "mock", "setup2", ["assert2"], "cleanup2")
        ]
        
        setups = self.generator._generate_mock_setups(mock_strategies, "python")
        
        assert "setup1" in setups
        assert "setup2" in setups
    
    def test_generate_mock_assertions(self):
        """Test mock assertion code generation."""
        mock_strategies = [
            MockStrategy("dep1", "patch", "setup1", ["assert1", "assert2"], "cleanup1"),
            MockStrategy("dep2", "mock", "setup2", ["assert3"], "cleanup2")
        ]
        
        assertions = self.generator._generate_mock_assertions(mock_strategies, "python")
        
        assert "assert1" in assertions
        assert "assert2" in assertions
        assert "assert3" in assertions
    
    def test_generate_teardown_code(self):
        """Test teardown code generation."""
        mock_strategies = [
            MockStrategy("dep1", "patch", "setup1", ["assert1"], "cleanup1"),
            MockStrategy("dep2", "mock", "setup2", ["assert2"], "cleanup2")
        ]
        
        teardown = self.generator._generate_teardown_code(mock_strategies, "python")
        
        assert "cleanup1" in teardown
        assert "cleanup2" in teardown
    
    def test_generate_successful_execution_python(self):
        """Test successful execution code generation for Python."""
        execution = self.generator._generate_successful_execution(self.sample_function, "python")
        
        assert "result = process_data()" in execution
        assert "assert result is not None" in execution
    
    def test_generate_successful_execution_javascript(self):
        """Test successful execution code generation for JavaScript."""
        execution = self.generator._generate_successful_execution(self.sample_function, "javascript")
        
        assert "const result = process_data()" in execution
        assert "expect(result).toBeDefined()" in execution
    
    def test_generate_failure_execution_python(self):
        """Test failure execution code generation for Python."""
        execution = self.generator._generate_failure_execution(self.sample_function, "python")
        
        assert "with pytest.raises(Exception)" in execution
        assert "process_data()" in execution
    
    def test_generate_failure_execution_javascript(self):
        """Test failure execution code generation for JavaScript."""
        execution = self.generator._generate_failure_execution(self.sample_function, "javascript")
        
        assert "expect(() =>" in execution
        assert "process_data()" in execution
        assert "toThrow()" in execution
    
    def test_generate_mock_test_execution_python(self):
        """Test mock test execution code generation for Python."""
        dependency = self.sample_dependencies[0]
        execution = self.generator._generate_mock_test_execution(
            self.sample_function, dependency, "python"
        )
        
        assert "with patch('sqlite3')" in execution
        assert "process_data()" in execution
        assert "assert result is not None" in execution
    
    def test_get_python_template(self):
        """Test Python template retrieval."""
        template = self.generator._get_python_template()
        
        assert "def {test_name}():" in template
        assert "{description}" in template
        assert "# Arrange" in template
        assert "# Act" in template
        assert "# Assert" in template
        assert "# Cleanup" in template
    
    def test_get_javascript_template(self):
        """Test JavaScript template retrieval."""
        template = self.generator._get_javascript_template()
        
        assert "describe(" in template
        assert "test(" in template
        assert "// Arrange" in template
        assert "// Act" in template
        assert "// Assert" in template
        assert "// Cleanup" in template
    
    def test_get_java_template(self):
        """Test Java template retrieval."""
        template = self.generator._get_java_template()
        
        assert "@Test" in template
        assert "public void {test_name}()" in template
        assert "// Arrange" in template
        assert "// Act" in template
        assert "// Assert" in template
        assert "// Cleanup" in template
    
    def test_integration_test_requirements_coverage(self):
        """Test that generated integration tests cover the required requirements."""
        test_cases = self.generator.generate_integration_tests(
            self.sample_function, self.sample_dependencies, "python"
        )
        
        for test_case in test_cases:
            assert test_case.requirements_covered is not None
            assert "3.1" in test_case.requirements_covered
            assert "3.2" in test_case.requirements_covered
            assert "3.3" in test_case.requirements_covered
            assert "3.4" in test_case.requirements_covered
            assert "8.1" in test_case.requirements_covered
            assert "8.2" in test_case.requirements_covered
            assert "8.3" in test_case.requirements_covered
            assert "8.4" in test_case.requirements_covered


class TestIntegrationScenario:
    """Test cases for IntegrationScenario dataclass."""
    
    def test_integration_scenario_creation(self):
        """Test IntegrationScenario creation."""
        dependencies = [
            Dependency(name="test_dep", type="test", source="test source")
        ]
        mock_strategies = [
            MockStrategy("test_dep", "patch", "setup", ["assert"], "cleanup")
        ]
        
        scenario = IntegrationScenario(
            name="test_scenario",
            description="Test description",
            dependencies=dependencies,
            mock_strategies=mock_strategies,
            setup_requirements=["req1", "req2"],
            expected_interactions=["interaction1", "interaction2"]
        )
        
        assert scenario.name == "test_scenario"
        assert scenario.description == "Test description"
        assert len(scenario.dependencies) == 1
        assert len(scenario.mock_strategies) == 1
        assert len(scenario.setup_requirements) == 2
        assert len(scenario.expected_interactions) == 2


class TestMockStrategy:
    """Test cases for MockStrategy dataclass."""
    
    def test_mock_strategy_creation(self):
        """Test MockStrategy creation."""
        strategy = MockStrategy(
            dependency_name="test_dep",
            mock_type="patch",
            mock_setup="setup code",
            mock_assertions=["assert1", "assert2"],
            teardown_code="cleanup code"
        )
        
        assert strategy.dependency_name == "test_dep"
        assert strategy.mock_type == "patch"
        assert strategy.mock_setup == "setup code"
        assert len(strategy.mock_assertions) == 2
        assert strategy.teardown_code == "cleanup code"
    
    def test_mock_strategy_default_teardown(self):
        """Test MockStrategy with default teardown code."""
        strategy = MockStrategy(
            dependency_name="test_dep",
            mock_type="patch",
            mock_setup="setup code",
            mock_assertions=["assert1"]
        )
        
        assert strategy.teardown_code == ""


if __name__ == "__main__":
    pytest.main([__file__])