#!/usr/bin/env python3
"""
Demo script for coverage gap detection and reporting functionality.
Showcases the CoverageGapDetector capabilities with sample code analysis.
"""

from src.analyzers.coverage_gap_detector import (
    CoverageGapDetector, GapType, GapSeverity
)
from src.analyzers.coverage_analyzer import CoverageAnalyzer
from src.interfaces.base_interfaces import (
    FunctionInfo, Parameter, TestSuite, TestCase, TestType, Language
)
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.progress import Progress, SpinnerColumn, TextColumn


def main():
    """Demonstrate coverage gap detection and reporting."""
    console = Console()
    
    console.print(Panel.fit(
        "[bold blue]Coverage Gap Detection and Reporting Demo[/bold blue]",
        border_style="blue"
    ))
    
    # Sample code with various coverage scenarios
    sample_code = '''def add_numbers(a, b):
    """Add two numbers together."""
    return a + b

def divide_numbers(a, b):
    """Divide two numbers with error handling."""
    if b == 0:
        raise ValueError("Cannot divide by zero")
    if a < 0:
        return None
    try:
        result = a / b
    except Exception as e:
        raise RuntimeError(f"Division failed: {e}")
    return result

def process_data(data, threshold=10):
    """Process data with complex logic."""
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
    
    return result

def validate_input(value):
    """Validate input with multiple conditions."""
    if value is None:
        raise ValueError("Value cannot be None")
    
    if isinstance(value, str):
        if not value.strip():
            return False
        return len(value) > 3
    
    if isinstance(value, (int, float)):
        return value >= 0
    
    return False'''
    
    # Display sample code
    console.print("\n[bold green]Sample Code to Analyze:[/bold green]")
    syntax = Syntax(sample_code, "python", theme="monokai", line_numbers=True)
    console.print(syntax)
    
    # Sample function information
    functions = [
        FunctionInfo(
            name="add_numbers",
            parameters=[Parameter("a", "int"), Parameter("b", "int")],
            return_type="int",
            complexity=1,
            line_range=(1, 3),
            docstring="Add two numbers together."
        ),
        FunctionInfo(
            name="divide_numbers", 
            parameters=[Parameter("a", "float"), Parameter("b", "float")],
            return_type="float",
            complexity=6,
            line_range=(5, 14),
            docstring="Divide two numbers with error handling."
        ),
        FunctionInfo(
            name="process_data",
            parameters=[
                Parameter("data", "list"),
                Parameter("threshold", "int", default_value=10)
            ],
            return_type="dict",
            complexity=8,
            line_range=(16, 30),
            docstring="Process data with complex logic."
        ),
        FunctionInfo(
            name="validate_input",
            parameters=[Parameter("value", "any")],
            return_type="bool",
            complexity=7,
            line_range=(32, 46),
            docstring="Validate input with multiple conditions."
        )
    ]
    
    # Simulate partial test coverage (only add_numbers and partial validate_input)
    covered_functions = {"add_numbers"}
    line_coverage = {
        1: True,   # def add_numbers
        2: True,   # docstring
        3: True,   # return a + b
        5: False,  # def divide_numbers (untested)
        6: False,  # docstring
        7: False,  # if b == 0
        8: False,  # raise ValueError
        9: False,  # if a < 0
        10: False, # return None
        11: False, # try
        12: False, # result = a / b
        13: False, # except
        14: False, # raise RuntimeError
        15: False, # return result
        16: False, # def process_data (untested)
        32: True,  # def validate_input (partially tested)
        33: True,  # docstring
        34: True,  # if value is None
        35: False, # raise ValueError (uncovered error handling)
        37: True,  # if isinstance(value, str)
        38: False, # if not value.strip() (uncovered edge case)
        39: False, # return False
        40: True,  # return len(value) > 3
        42: False, # if isinstance(value, (int, float)) (uncovered branch)
        43: False, # return value >= 0
        45: False, # return False (uncovered default case)
    }
    
    # Create test suite with limited coverage
    test_suite = TestSuite(
        language=Language.PYTHON,
        framework="pytest",
        test_cases=[
            TestCase(
                name="test_add_numbers",
                test_type=TestType.UNIT,
                function_name="add_numbers",
                description="Test basic addition",
                test_code="def test_add_numbers(): assert add_numbers(2, 3) == 5"
            ),
            TestCase(
                name="test_validate_input_string",
                test_type=TestType.UNIT,
                function_name="validate_input",
                description="Test string validation",
                test_code="def test_validate_input_string(): assert validate_input('hello') == True"
            )
        ]
    )
    
    console.print(f"\n[bold yellow]Current Test Coverage:[/bold yellow]")
    console.print(f"• Functions with tests: {', '.join(covered_functions)}")
    console.print(f"• Partially tested: validate_input")
    console.print(f"• Untested functions: divide_numbers, process_data")
    
    # Initialize gap detector and analyzer
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Analyzing coverage gaps...", total=None)
        
        gap_detector = CoverageGapDetector()
        analyzer = CoverageAnalyzer()
        
        # Generate detailed coverage report
        progress.update(task, description="Generating detailed coverage report...")
        detailed_report = gap_detector.generate_detailed_report(
            sample_code, "python", covered_functions, line_coverage, functions
        )
        
        # Detect coverage gaps
        progress.update(task, description="Detecting coverage gaps...")
        gaps = gap_detector.detect_coverage_gaps(
            sample_code, "python", covered_functions, line_coverage, functions
        )
        
        progress.update(task, description="Analysis complete!")
    
    # Display coverage metrics
    console.print(f"\n[bold cyan]Coverage Metrics:[/bold cyan]")
    metrics_table = Table(show_header=True, header_style="bold magenta")
    metrics_table.add_column("Metric", style="cyan")
    metrics_table.add_column("Value", style="green")
    
    metrics = detailed_report.metrics
    metrics_table.add_row("Overall Coverage", f"{detailed_report.overall_percentage:.1f}%")
    metrics_table.add_row("Function Coverage", f"{metrics.function_coverage:.1f}%")
    metrics_table.add_row("Statement Coverage", f"{metrics.statement_coverage:.1f}%")
    metrics_table.add_row("Branch Coverage", f"{metrics.branch_coverage:.1f}%")
    metrics_table.add_row("Complexity-Weighted Coverage", f"{metrics.complexity_weighted_coverage:.1f}%")
    metrics_table.add_row("Total Lines", str(metrics.total_lines))
    metrics_table.add_row("Executable Lines", str(metrics.executable_lines))
    metrics_table.add_row("Covered Lines", str(metrics.covered_lines))
    metrics_table.add_row("Uncovered Lines", str(metrics.uncovered_lines))
    
    console.print(metrics_table)
    
    # Display coverage gaps by type
    console.print(f"\n[bold red]Coverage Gaps Detected ({len(gaps)} total):[/bold red]")
    
    gap_types = {}
    for gap in gaps:
        gap_type = gap.gap_type.value
        if gap_type not in gap_types:
            gap_types[gap_type] = []
        gap_types[gap_type].append(gap)
    
    for gap_type, type_gaps in gap_types.items():
        console.print(f"\n[bold yellow]{gap_type.replace('_', ' ').title()} ({len(type_gaps)} gaps):[/bold yellow]")
        
        gaps_table = Table(show_header=True, header_style="bold blue")
        gaps_table.add_column("Function", style="cyan")
        gaps_table.add_column("Lines", style="yellow")
        gaps_table.add_column("Severity", style="red")
        gaps_table.add_column("Confidence", style="green")
        gaps_table.add_column("Description", style="white")
        
        for gap in type_gaps:
            severity_color = {
                GapSeverity.CRITICAL: "bright_red",
                GapSeverity.HIGH: "red",
                GapSeverity.MEDIUM: "yellow",
                GapSeverity.LOW: "green"
            }.get(gap.severity, "white")
            
            gaps_table.add_row(
                gap.function_name,
                f"{gap.line_range[0]}-{gap.line_range[1]}",
                f"[{severity_color}]{gap.severity.value.upper()}[/{severity_color}]",
                f"{gap.confidence:.1%}",
                gap.description
            )
        
        console.print(gaps_table)
    
    # Display recommendations
    console.print(f"\n[bold green]Recommendations:[/bold green]")
    for i, recommendation in enumerate(detailed_report.recommendations, 1):
        console.print(f"{i}. {recommendation}")
    
    # Display improvement suggestions
    console.print(f"\n[bold blue]Improvement Suggestions:[/bold blue]")
    for suggestion in detailed_report.improvement_suggestions:
        console.print(f"\n[bold cyan]{suggestion['description']}[/bold cyan]")
        console.print(f"Priority: {suggestion['priority']}, Count: {suggestion['count']}")
        console.print("Action items:")
        for action in suggestion['action_items']:
            console.print(f"  • {action}")
    
    # Generate test suggestions
    console.print(f"\n[bold magenta]Generated Test Suggestions:[/bold magenta]")
    suggested_tests = gap_detector.suggest_test_improvements(gaps[:5])  # Show first 5
    
    for i, test in enumerate(suggested_tests, 1):
        console.print(f"\n[bold yellow]Test {i}: {test.name}[/bold yellow]")
        console.print(f"Type: {test.test_type.value}")
        console.print(f"Description: {test.description}")
        console.print("Generated code:")
        test_syntax = Syntax(test.test_code, "python", theme="monokai")
        console.print(test_syntax)
    
    # Show integration with CoverageAnalyzer
    console.print(f"\n[bold green]Integration with CoverageAnalyzer:[/bold green]")
    
    # Use analyzer's new methods
    advanced_gaps = analyzer.detect_advanced_gaps(test_suite, sample_code, functions)
    improved_tests = analyzer.suggest_improved_tests(advanced_gaps[:3])
    
    console.print(f"Advanced gaps detected: {len(advanced_gaps)}")
    console.print(f"Improved test suggestions: {len(improved_tests)}")
    
    # Show sample improved test
    if improved_tests:
        console.print(f"\n[bold cyan]Sample Improved Test:[/bold cyan]")
        sample_test = improved_tests[0]
        console.print(f"Name: {sample_test.name}")
        console.print(f"Description: {sample_test.description}")
        improved_syntax = Syntax(sample_test.test_code, "python", theme="monokai")
        console.print(improved_syntax)
    
    console.print(f"\n[bold green]✅ Coverage gap detection and reporting demo completed![/bold green]")
    console.print(f"The system successfully identified {len(gaps)} coverage gaps and provided detailed recommendations.")


if __name__ == "__main__":
    main()