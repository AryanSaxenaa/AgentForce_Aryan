"""
Unit tests for CoverageAnalyzer.
"""
import pytest
from src.analyzers.coverage_analyzer import CoverageAnalyzer, LineInfo
from src.interfaces.base_interfaces import (
    TestSuite, TestCase, TestType, Language, CoverageGap
)


class TestCoverageAnalyzer:
    """Test cases for CoverageAnalyzer functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = CoverageAnalyzer()
    
    def test_init(self):
        """Test CoverageAnalyzer initialization."""
        assert self.analyzer is not None
        assert 'python' in self.analyzer._executable_patterns
        assert 'java' in self.analyzer._executable_patterns
        assert 'javascript' in self.analyzer._executable_patterns
    
    def test_parse_code_lines_python(self):
        """Test parsing Python code into lines with metadata."""
        code = """def add(a, b):
    # This is a comment
    return a + b

def multiply(x, y):
    result = x * y
    return result
"""
        lines = self.analyzer._parse_code_lines(code, 'python')
        
        assert len(lines) == 8
        
        # Check function definition line
        assert lines[0].line_number == 1
        assert lines[0].is_executable == True
        assert lines[0].function_name == 'add'
        
        # Check comment line
        assert lines[1].line_number == 2
        assert lines[1].is_executable == False
        
        # Check return statement
        assert lines[2].line_number == 3
        assert lines[2].is_executable == True
        assert lines[2].function_name == 'add'
    
    def test_parse_code_lines_java(self):
        """Test parsing Java code into lines with metadata."""
        code = """public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    private int multiply(int x, int y) {
        int result = x * y;
        return result;
    }
}"""
        lines = self.analyzer._parse_code_lines(code, 'java')
        
        assert len(lines) == 10
        
        # Check method definition
        method_line = next((l for l in lines if 'add' in l.content), None)
        assert method_line is not None
        assert method_line.is_executable == True
    
    def test_parse_code_lines_javascript(self):
        """Test parsing JavaScript code into lines with metadata."""
        code = """function add(a, b) {
    return a + b;
}

const multiply = (x, y) => {
    const result = x * y;
    return result;
};"""
        lines = self.analyzer._parse_code_lines(code, 'javascript')
        
        assert len(lines) == 8
        
        # Check function definition
        assert lines[0].is_executable == True
        assert lines[0].function_name == 'add'
        
        # Check arrow function
        arrow_func_line = next((l for l in lines if 'const multiply' in l.content), None)
        assert arrow_func_line is not None
        assert arrow_func_line.is_executable == True
    
    def test_map_test_coverage(self):
        """Test mapping test cases to covered functions."""
        lines = [
            LineInfo(1, "def add(a, b):", True, "add"),
            LineInfo(2, "    return a + b", True, "add"),
            LineInfo(3, "def multiply(x, y):", True, "multiply"),
            LineInfo(4, "    return x * y", True, "multiply"),
        ]
        
        test_cases = [
            TestCase(
                name="test_add_positive_numbers",
                test_type=TestType.UNIT,
                function_name="add",
                description="Test adding positive numbers",
                test_code="assert add(2, 3) == 5"
            )
        ]
        
        test_suite = TestSuite(
            language=Language.PYTHON,
            framework="pytest",
            test_cases=test_cases
        )
        
        covered_functions = self.analyzer._map_test_coverage(test_suite, lines)
        
        assert "add" in covered_functions
        assert "multiply" not in covered_functions
    
    def test_calculate_line_coverage(self):
        """Test line-by-line coverage calculation."""
        lines = [
            LineInfo(1, "def add(a, b):", True, "add"),
            LineInfo(2, "    return a + b", True, "add"),
            LineInfo(3, "def multiply(x, y):", True, "multiply"),
            LineInfo(4, "    return x * y", True, "multiply"),
        ]
        
        covered_functions = {"add"}
        
        line_coverage = self.analyzer._calculate_line_coverage(lines, covered_functions)
        
        assert line_coverage[1] == True  # add function definition
        assert line_coverage[2] == True  # add return statement
        assert line_coverage[3] == False  # multiply function definition
        assert line_coverage[4] == False  # multiply return statement
    
    def test_identify_untested_functions(self):
        """Test identification of untested functions."""
        lines = [
            LineInfo(1, "def add(a, b):", True, "add"),
            LineInfo(2, "    return a + b", True, "add"),
            LineInfo(3, "def multiply(x, y):", True, "multiply"),
            LineInfo(4, "    return x * y", True, "multiply"),
            LineInfo(5, "def divide(x, y):", True, "divide"),
            LineInfo(6, "    return x / y", True, "divide"),
        ]
        
        covered_functions = {"add", "multiply"}
        
        untested = self.analyzer._identify_untested_functions(lines, covered_functions)
        
        assert "divide" in untested
        assert "add" not in untested
        assert "multiply" not in untested
    
    def test_identify_coverage_gaps(self):
        """Test identification of coverage gaps."""
        lines = [
            LineInfo(1, "def add(a, b):", True, "add", True),  # Mark as covered
            LineInfo(2, "    return a + b", True, "add", True),  # Mark as covered
            LineInfo(3, "def multiply(x, y):", True, "multiply"),
            LineInfo(4, "    return x * y", True, "multiply"),
        ]
        
        untested_functions = ["multiply"]
        
        gaps = self.analyzer._identify_coverage_gaps(lines, untested_functions)
        
        assert len(gaps) >= 1
        # Find the gap for multiply function
        multiply_gap = next((gap for gap in gaps if gap.function_name == "multiply"), None)
        assert multiply_gap is not None
        assert multiply_gap.line_range == (3, 4)
        assert "no test coverage" in multiply_gap.description
    
    def test_estimate_coverage_full_coverage(self):
        """Test coverage estimation with full coverage."""
        code = """def add(a, b):
    return a + b

def multiply(x, y):
    return x * y
"""
        
        test_cases = [
            TestCase(
                name="test_add",
                test_type=TestType.UNIT,
                function_name="add",
                description="Test add function",
                test_code="assert add(2, 3) == 5"
            ),
            TestCase(
                name="test_multiply",
                test_type=TestType.UNIT,
                function_name="multiply",
                description="Test multiply function",
                test_code="assert multiply(2, 3) == 6"
            )
        ]
        
        test_suite = TestSuite(
            language=Language.PYTHON,
            framework="pytest",
            test_cases=test_cases
        )
        
        coverage = self.analyzer.estimate_coverage(test_suite, code)
        
        assert coverage.overall_percentage == 100.0
        assert len(coverage.untested_functions) == 0
        assert len(coverage.coverage_gaps) == 0
    
    def test_estimate_coverage_partial_coverage(self):
        """Test coverage estimation with partial coverage."""
        code = """def add(a, b):
    return a + b

def multiply(x, y):
    return x * y

def divide(x, y):
    if y == 0:
        raise ValueError("Division by zero")
    return x / y
"""
        
        test_cases = [
            TestCase(
                name="test_add",
                test_type=TestType.UNIT,
                function_name="add",
                description="Test add function",
                test_code="assert add(2, 3) == 5"
            )
        ]
        
        test_suite = TestSuite(
            language=Language.PYTHON,
            framework="pytest",
            test_cases=test_cases
        )
        
        coverage = self.analyzer.estimate_coverage(test_suite, code)
        
        assert coverage.overall_percentage < 100.0
        assert "multiply" in coverage.untested_functions
        assert "divide" in coverage.untested_functions
        assert len(coverage.coverage_gaps) >= 2
    
    def test_estimate_coverage_no_coverage(self):
        """Test coverage estimation with no coverage."""
        code = """def add(a, b):
    return a + b
"""
        
        test_suite = TestSuite(
            language=Language.PYTHON,
            framework="pytest",
            test_cases=[]
        )
        
        coverage = self.analyzer.estimate_coverage(test_suite, code)
        
        assert coverage.overall_percentage == 0.0
        assert "add" in coverage.untested_functions
        assert len(coverage.coverage_gaps) >= 1
    
    def test_suggest_additional_tests(self):
        """Test suggestion of additional test cases."""
        gaps = [
            CoverageGap(
                function_name="multiply",
                line_range=(3, 4),
                description="Function 'multiply' has no test coverage",
                suggested_tests=["Add unit test for multiply"]
            ),
            CoverageGap(
                function_name="divide",
                line_range=(6, 9),
                description="Function 'divide' has no test coverage",
                suggested_tests=["Add unit test for divide", "Test division by zero"]
            )
        ]
        
        suggested_tests = self.analyzer.suggest_additional_tests(gaps)
        
        assert len(suggested_tests) == 2
        assert suggested_tests[0].function_name == "multiply"
        assert suggested_tests[1].function_name == "divide"
        assert all(test.test_type == TestType.UNIT for test in suggested_tests)
    
    def test_identify_gaps_method(self):
        """Test the identify_gaps method."""
        from src.interfaces.base_interfaces import CoverageReport
        
        gaps = [
            CoverageGap(
                function_name="test_func",
                line_range=(1, 5),
                description="Test gap",
                suggested_tests=["Test suggestion"]
            )
        ]
        
        coverage = CoverageReport(
            overall_percentage=75.0,
            line_coverage={1: True, 2: False, 3: True, 4: False},
            untested_functions=["test_func"],
            coverage_gaps=gaps
        )
        
        identified_gaps = self.analyzer.identify_gaps(coverage)
        
        assert len(identified_gaps) == 1
        assert identified_gaps[0].function_name == "test_func"
    
    def test_generate_basic_test_template(self):
        """Test generation of basic test templates."""
        gap = CoverageGap(
            function_name="multiply",
            line_range=(3, 4),
            description="Function 'multiply' has no test coverage",
            suggested_tests=["Add unit test for multiply"]
        )
        
        template = self.analyzer._generate_basic_test_template(gap)
        
        assert "test_multiply_gap" in template
        assert "multiply" in template
        assert "Lines 3-4" in template
        assert "def test_" in template
    
    def test_coverage_with_comments_and_empty_lines(self):
        """Test coverage calculation ignoring comments and empty lines."""
        code = """# This is a comment
def add(a, b):
    # Another comment
    
    return a + b  # Inline comment

# Final comment
"""
        
        test_cases = [
            TestCase(
                name="test_add",
                test_type=TestType.UNIT,
                function_name="add",
                description="Test add function",
                test_code="assert add(2, 3) == 5"
            )
        ]
        
        test_suite = TestSuite(
            language=Language.PYTHON,
            framework="pytest",
            test_cases=test_cases
        )
        
        coverage = self.analyzer.estimate_coverage(test_suite, code)
        
        # Should have 100% coverage since only executable lines are counted
        assert coverage.overall_percentage == 100.0
        
        # Verify that comments and empty lines are not counted in coverage
        executable_line_count = sum(1 for covered in coverage.line_coverage.values())
        assert executable_line_count == 2  # Only function def and return statement
    
    def test_coverage_with_complex_control_flow(self):
        """Test coverage with complex control flow structures."""
        code = """def complex_function(x, y):
    if x > 0:
        if y > 0:
            return x + y
        else:
            return x - y
    else:
        for i in range(y):
            x += i
        return x
"""
        
        test_cases = [
            TestCase(
                name="test_complex_function_positive",
                test_type=TestType.UNIT,
                function_name="complex_function",
                description="Test complex function with positive values",
                test_code="assert complex_function(5, 3) == 8"
            )
        ]
        
        test_suite = TestSuite(
            language=Language.PYTHON,
            framework="pytest",
            test_cases=test_cases
        )
        
        coverage = self.analyzer.estimate_coverage(test_suite, code)
        
        # Should detect that the function is tested but may have partial coverage
        assert coverage.overall_percentage > 0
        assert len(coverage.untested_functions) == 0  # Function is tested
        
        # Check that all executable lines are identified
        assert len(coverage.line_coverage) > 5  # Multiple executable lines


if __name__ == "__main__":
    pytest.main([__file__])