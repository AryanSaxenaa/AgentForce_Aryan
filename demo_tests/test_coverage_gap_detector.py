"""
Unit tests for coverage gap detection and reporting functionality.
"""
import pytest
from unittest.mock import Mock, patch
from src.analyzers.coverage_gap_detector import (
    CoverageGapDetector, DetailedCoverageGap, DetailedCoverageReport,
    GapType, GapSeverity, CoverageMetrics
)
from src.interfaces.base_interfaces import (
    FunctionInfo, TestCase, TestType, Language, Parameter
)


class TestCoverageGapDetector:
    """Test cases for CoverageGapDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = CoverageGapDetector()
        
        # Sample function info
        self.sample_functions = [
            FunctionInfo(
                name="add_numbers",
                parameters=[
                    Parameter(name="a", type_hint="int"),
                    Parameter(name="b", type_hint="int")
                ],
                return_type="int",
                complexity=2,
                line_range=(1, 3),
                docstring="Add two numbers"
            ),
            FunctionInfo(
                name="divide_numbers",
                parameters=[
                    Parameter(name="a", type_hint="float"),
                    Parameter(name="b", type_hint="float")
                ],
                return_type="float",
                complexity=5,
                line_range=(5, 12),
                docstring="Divide two numbers with error handling"
            ),
            FunctionInfo(
                name="complex_function",
                parameters=[
                    Parameter(name="data", type_hint="list"),
                    Parameter(name="threshold", type_hint="int", default_value=10)
                ],
                return_type="dict",
                complexity=15,
                line_range=(14, 25),
                docstring="Complex function with high complexity"
            )
        ]
        
        # Sample code
        self.sample_code = '''def add_numbers(a, b):
    return a + b

def divide_numbers(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    if a < 0:
        return None
    try:
        result = a / b
    except Exception as e:
        raise RuntimeError(f"Division failed: {e}")
    return result

def complex_function(data, threshold=10):
    if not data:
        return {}
    if len(data) == 0:
        return {"empty": True}
    result = {}
    for item in data:
        if item > threshold:
            result[item] = "high"
        elif item < 0:
            result[item] = "negative"
        else:
            result[item] = "normal"
    return result'''
        
        # Sample coverage data
        self.covered_functions = {"add_numbers"}  # Only add_numbers is covered
        self.line_coverage = {
            1: True,   # def add_numbers
            2: True,   # return a + b
            3: False,  # empty line
            5: False,  # def divide_numbers
            6: False,  # if b == 0
            7: False,  # raise ValueError
            8: False,  # if a < 0
            9: False,  # return None
            10: False, # try
            11: False, # result = a / b
            12: False, # except
            13: False, # raise RuntimeError
            14: False, # return result
            16: False, # def complex_function
            17: False, # if not data
            18: False, # return {}
            19: False, # if len(data) == 0
            20: False, # return {"empty": True}
            21: False, # result = {}
            22: False, # for item in data
            23: False, # if item > threshold
            24: False, # result[item] = "high"
            25: False, # elif item < 0
        }
    
    def test_detect_untested_functions(self):
        """Test detection of functions with no test coverage."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions, 
            self.line_coverage, self.sample_functions
        )
        
        # Should detect divide_numbers and complex_function as untested
        untested_gaps = [g for g in gaps if g.gap_type == GapType.UNTESTED_FUNCTION]
        assert len(untested_gaps) == 2
        
        # Check that complex_function has critical severity due to high complexity
        complex_gap = next(g for g in untested_gaps if g.function_name == "complex_function")
        assert complex_gap.severity == GapSeverity.CRITICAL
        assert complex_gap.confidence == 1.0
        assert complex_gap.priority == 10
        
        # Check that divide_numbers has medium severity (complexity = 5, which is <= 5)
        divide_gap = next(g for g in untested_gaps if g.function_name == "divide_numbers")
        assert divide_gap.severity == GapSeverity.MEDIUM
        assert divide_gap.priority == 8  # Medium severity gets priority 8
        assert "no test coverage" in divide_gap.description
    
    def test_detect_missing_edge_cases(self):
        """Test detection of missing edge case coverage."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        edge_gaps = [g for g in gaps if g.gap_type == GapType.MISSING_EDGE_CASES]
        
        # Should detect edge cases like "if not data", "if len(data) == 0", etc.
        assert len(edge_gaps) > 0
        
        # Check that edge cases have appropriate metadata
        for gap in edge_gaps:
            assert gap.severity in [GapSeverity.MEDIUM, GapSeverity.LOW]
            assert gap.confidence == 0.7
            assert TestType.EDGE in gap.suggested_test_types
    
    def test_detect_error_handling_gaps(self):
        """Test detection of uncovered error handling code."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        error_gaps = [g for g in gaps if g.gap_type == GapType.ERROR_HANDLING]
        
        # Should detect raise statements and exception handling
        assert len(error_gaps) > 0
        
        # Check error handling gaps have high severity
        for gap in error_gaps:
            assert gap.severity == GapSeverity.HIGH
            assert gap.confidence == 0.9
            assert "error handling" in gap.description.lower()
    
    def test_detect_uncovered_branches(self):
        """Test detection of uncovered conditional branches."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        branch_gaps = [g for g in gaps if g.gap_type == GapType.UNCOVERED_BRANCHES]
        
        # Should detect if statements, for loops, etc.
        assert len(branch_gaps) > 0
        
        # Check branch gaps have appropriate metadata
        for gap in branch_gaps:
            assert gap.severity == GapSeverity.MEDIUM
            assert gap.confidence == 0.8
            assert TestType.UNIT in gap.suggested_test_types or TestType.EDGE in gap.suggested_test_types
    
    def test_generate_detailed_report(self):
        """Test generation of detailed coverage report."""
        report = self.detector.generate_detailed_report(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        # Check report structure
        assert isinstance(report, DetailedCoverageReport)
        assert isinstance(report.metrics, CoverageMetrics)
        assert len(report.coverage_gaps) > 0
        assert len(report.recommendations) > 0
        assert len(report.improvement_suggestions) > 0
        
        # Check metrics calculation
        assert report.metrics.total_lines > 0
        assert report.metrics.executable_lines > 0
        assert report.metrics.function_coverage < 100  # Not all functions covered
        assert report.overall_percentage >= 0
        
        # Check untested functions
        assert "divide_numbers" in report.untested_functions
        assert "complex_function" in report.untested_functions
        assert "add_numbers" not in report.untested_functions
    
    def test_calculate_detailed_metrics(self):
        """Test detailed metrics calculation."""
        metrics = self.detector._calculate_detailed_metrics(
            self.sample_code, self.line_coverage, self.sample_functions, self.covered_functions
        )
        
        assert isinstance(metrics, CoverageMetrics)
        assert metrics.total_lines > 0
        assert metrics.executable_lines > 0
        assert metrics.covered_lines >= 0
        assert metrics.uncovered_lines >= 0
        assert 0 <= metrics.function_coverage <= 100
        assert 0 <= metrics.statement_coverage <= 100
        assert 0 <= metrics.complexity_weighted_coverage <= 100
        
        # Function coverage should be 33.33% (1 out of 3 functions covered)
        assert abs(metrics.function_coverage - 33.33) < 0.1
    
    def test_generate_recommendations(self):
        """Test generation of coverage recommendations."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        metrics = self.detector._calculate_detailed_metrics(
            self.sample_code, self.line_coverage, self.sample_functions, self.covered_functions
        )
        
        recommendations = self.detector._generate_recommendations(gaps, metrics)
        
        assert len(recommendations) > 0
        assert any("coverage" in rec.lower() for rec in recommendations)
        
        # Should recommend improving function coverage
        assert any("function coverage" in rec.lower() for rec in recommendations)
    
    def test_suggest_test_improvements(self):
        """Test generation of test improvement suggestions."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        suggested_tests = self.detector.suggest_test_improvements(gaps)
        
        assert len(suggested_tests) > 0
        
        # Check test case structure
        for test in suggested_tests:
            assert isinstance(test, TestCase)
            assert test.name
            assert test.test_code
            assert test.description
            assert test.test_type in [TestType.UNIT, TestType.EDGE, TestType.INTEGRATION]
    
    def test_generate_improvement_suggestions(self):
        """Test generation of improvement suggestions."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        suggestions = self.detector._generate_improvement_suggestions(gaps)
        
        assert len(suggestions) > 0
        
        # Check suggestion structure
        for suggestion in suggestions:
            assert 'type' in suggestion
            assert 'count' in suggestion
            assert 'priority' in suggestion
            assert 'description' in suggestion
            assert 'action_items' in suggestion
            assert isinstance(suggestion['action_items'], list)
    
    def test_generate_test_template(self):
        """Test generation of test templates for different gap types."""
        # Test untested function template
        untested_gap = DetailedCoverageGap(
            function_name="test_func",
            line_range=(1, 5),
            description="Test description",
            suggested_tests=["Add unit test"],
            gap_type=GapType.UNTESTED_FUNCTION,
            severity=GapSeverity.HIGH,
            confidence=1.0,
            code_snippet="def test_func(): pass",
            suggested_test_types=[TestType.UNIT],
            priority=8
        )
        
        template = self.detector._generate_test_template(untested_gap, "Add unit test")
        assert "def test_test_func()" in template
        assert "TODO" in template
        assert "test_func" in template
        
        # Test edge case template
        edge_gap = DetailedCoverageGap(
            function_name="edge_func",
            line_range=(1, 2),
            description="Edge case",
            suggested_tests=["Test edge case"],
            gap_type=GapType.MISSING_EDGE_CASES,
            severity=GapSeverity.MEDIUM,
            confidence=0.7,
            code_snippet="if not data:",
            suggested_test_types=[TestType.EDGE],
            priority=6
        )
        
        edge_template = self.detector._generate_test_template(edge_gap, "Test edge case")
        assert "edge_case" in edge_template
        assert "if not data:" in edge_template
        
        # Test error handling template
        error_gap = DetailedCoverageGap(
            function_name="error_func",
            line_range=(1, 2),
            description="Error handling",
            suggested_tests=["Test error"],
            gap_type=GapType.ERROR_HANDLING,
            severity=GapSeverity.HIGH,
            confidence=0.9,
            code_snippet="raise ValueError",
            suggested_test_types=[TestType.EDGE],
            priority=8
        )
        
        error_template = self.detector._generate_test_template(error_gap, "Test error")
        assert "error_handling" in error_template
        assert "pytest.raises" in error_template
    
    def test_language_specific_patterns(self):
        """Test language-specific pattern detection."""
        # Test Java patterns
        java_code = '''public class Calculator {
    public int divide(int a, int b) {
        if (b == 0) {
            throw new IllegalArgumentException("Division by zero");
        }
        return a / b;
    }
}'''
        
        java_line_coverage = {i: False for i in range(1, 8)}
        java_functions = [
            FunctionInfo(
                name="divide",
                parameters=[Parameter("a", "int"), Parameter("b", "int")],
                return_type="int",
                complexity=3,
                line_range=(2, 6)
            )
        ]
        
        java_gaps = self.detector.detect_coverage_gaps(
            java_code, "java", set(), java_line_coverage, java_functions
        )
        
        assert len(java_gaps) > 0
        
        # Test JavaScript patterns
        js_code = '''function validateInput(input) {
    if (input === null || input === undefined) {
        throw new Error("Input cannot be null or undefined");
    }
    if (input.length === 0) {
        return false;
    }
    return true;
}'''
        
        js_line_coverage = {i: False for i in range(1, 8)}
        js_functions = [
            FunctionInfo(
                name="validateInput",
                parameters=[Parameter("input", "any")],
                return_type="boolean",
                complexity=4,
                line_range=(1, 7)
            )
        ]
        
        js_gaps = self.detector.detect_coverage_gaps(
            js_code, "javascript", set(), js_line_coverage, js_functions
        )
        
        assert len(js_gaps) > 0
    
    def test_gap_prioritization(self):
        """Test that gaps are properly prioritized by severity and priority."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        # Gaps should be sorted by severity and priority
        assert len(gaps) > 1
        
        # Critical gaps should come first
        critical_gaps = [g for g in gaps if g.severity == GapSeverity.CRITICAL]
        if critical_gaps:
            assert gaps[0].severity == GapSeverity.CRITICAL
        
        # Check that priorities are in descending order within same severity
        for i in range(len(gaps) - 1):
            current_gap = gaps[i]
            next_gap = gaps[i + 1]
            
            # If same severity, priority should be higher or equal
            if current_gap.severity == next_gap.severity:
                assert current_gap.priority >= next_gap.priority
    
    def test_confidence_scoring(self):
        """Test that confidence scores are appropriate for different gap types."""
        gaps = self.detector.detect_coverage_gaps(
            self.sample_code, "python", self.covered_functions,
            self.line_coverage, self.sample_functions
        )
        
        # Check confidence scores for different gap types
        for gap in gaps:
            if gap.gap_type == GapType.UNTESTED_FUNCTION:
                assert gap.confidence == 1.0  # Highest confidence
            elif gap.gap_type == GapType.ERROR_HANDLING:
                assert gap.confidence == 0.9  # High confidence
            elif gap.gap_type == GapType.UNCOVERED_BRANCHES:
                assert gap.confidence == 0.8  # Good confidence
            elif gap.gap_type == GapType.MISSING_EDGE_CASES:
                assert gap.confidence == 0.7  # Medium confidence
            
            # All confidence scores should be between 0 and 1
            assert 0.0 <= gap.confidence <= 1.0


class TestCoverageAnalyzerIntegration:
    """Test integration between CoverageAnalyzer and CoverageGapDetector."""
    
    def setup_method(self):
        """Set up test fixtures."""
        from src.analyzers.coverage_analyzer import CoverageAnalyzer
        from src.interfaces.base_interfaces import TestSuite, Language
        
        self.analyzer = CoverageAnalyzer()
        
        # Sample test suite
        self.test_suite = TestSuite(
            language=Language.PYTHON,
            framework="pytest",
            test_cases=[
                TestCase(
                    name="test_add_numbers",
                    test_type=TestType.UNIT,
                    function_name="add_numbers",
                    description="Test addition",
                    test_code="def test_add_numbers(): assert add_numbers(2, 3) == 5"
                )
            ]
        )
        
        self.sample_code = '''def add_numbers(a, b):
    return a + b

def divide_numbers(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b'''
        
        self.sample_functions = [
            FunctionInfo(
                name="add_numbers",
                parameters=[Parameter("a", "int"), Parameter("b", "int")],
                return_type="int",
                complexity=1,
                line_range=(1, 2)
            ),
            FunctionInfo(
                name="divide_numbers",
                parameters=[Parameter("a", "int"), Parameter("b", "int")],
                return_type="int",
                complexity=3,
                line_range=(4, 7)
            )
        ]
    
    def test_generate_detailed_coverage_report_integration(self):
        """Test integration of detailed coverage report generation."""
        report = self.analyzer.generate_detailed_coverage_report(
            self.test_suite, self.sample_code, self.sample_functions
        )
        
        assert isinstance(report, DetailedCoverageReport)
        assert report.overall_percentage >= 0
        assert len(report.coverage_gaps) > 0
        assert len(report.recommendations) > 0
        assert isinstance(report.metrics, CoverageMetrics)
    
    def test_detect_advanced_gaps_integration(self):
        """Test integration of advanced gap detection."""
        gaps = self.analyzer.detect_advanced_gaps(
            self.test_suite, self.sample_code, self.sample_functions
        )
        
        assert len(gaps) > 0
        assert all(isinstance(gap, DetailedCoverageGap) for gap in gaps)
        
        # Should detect divide_numbers as untested
        untested_gaps = [g for g in gaps if g.gap_type == GapType.UNTESTED_FUNCTION]
        assert any(g.function_name == "divide_numbers" for g in untested_gaps)
    
    def test_suggest_improved_tests_integration(self):
        """Test integration of improved test suggestions."""
        gaps = self.analyzer.detect_advanced_gaps(
            self.test_suite, self.sample_code, self.sample_functions
        )
        
        improved_tests = self.analyzer.suggest_improved_tests(gaps)
        
        assert len(improved_tests) > 0
        assert all(isinstance(test, TestCase) for test in improved_tests)
        
        # Should suggest tests for divide_numbers
        divide_tests = [t for t in improved_tests if "divide_numbers" in t.name]
        assert len(divide_tests) > 0


if __name__ == "__main__":
    pytest.main([__file__])