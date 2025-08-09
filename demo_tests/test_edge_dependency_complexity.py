"""Focused tests for EdgeCaseDetector, DependencyAnalyzer, ComplexityAnalyzer, and AnalysisOrchestrator."""
from src.analyzers import EdgeCaseDetector, DependencyAnalyzer, ComplexityAnalyzer, AnalysisOrchestrator


def test_edge_case_detector_python():
    code = """
import os

def f(x):
    if x is None:
        return 0
    if len(x) == 0:
        return -1
    return 10 / x[0]
"""
    detector = EdgeCaseDetector()
    cases = detector.detect(code, 'python')
    kinds = {c.type for c in cases}
    assert 'null_check' in kinds
    assert 'empty_collection' in kinds
    assert 'division_by_zero' in kinds
    assert 'index_bounds' in kinds


def test_dependency_analyzer_python():
    code = """
from math import sqrt
import json
"""
    deps = DependencyAnalyzer().detect(code, 'python')
    names = [d.name for d in deps]
    assert 'math' in names
    assert 'json' in names


def test_complexity_analyzer_basic():
    code = """
for i in range(10):
    if i % 2 == 0:
        pass
"""
    metrics = ComplexityAnalyzer().analyze(code)
    assert metrics.lines_of_code >= 3
    assert metrics.cyclomatic_complexity >= 2


def test_orchestrator_integration():
    code = """
class C:
    def add(self, a, b):
        return a + b
"""
    analysis = AnalysisOrchestrator().analyze(code, 'python')
    assert analysis.language == 'python'
    assert any(f.name == 'add' for f in analysis.functions)
    assert any(c.name == 'C' for c in analysis.classes)
    assert analysis.complexity_metrics.lines_of_code > 0
