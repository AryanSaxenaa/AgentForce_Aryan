"""
Unit tests for ClassAnalyzer.
"""
import pytest
from src.analyzers.class_analyzer import ClassAnalyzer


class TestClassAnalyzer:
    def setup_method(self):
        self.analyzer = ClassAnalyzer()

    def test_python_classes(self):
        code = '''
class A:
    def m1(self):
        pass

class B(A):
    def __init__(self):
        pass
    def m2(self, x):
        return x
'''
        classes = self.analyzer.analyze_classes(code, 'python')
        names = [c.name for c in classes]
        assert 'A' in names and 'B' in names
        b = next(c for c in classes if c.name == 'B')
        assert 'm2' in b.methods
        assert 'A' in (b.inheritance or [])

    def test_javascript_classes(self):
        code = '''
class Greeter {
  constructor() { this.name = 'x'; }
  greet(name) { return `Hi ${name}`; }
}
'''
        classes = self.analyzer.analyze_classes(code, 'javascript')
        assert len(classes) == 1
        c = classes[0]
        assert c.name == 'Greeter'
        assert 'greet' in c.methods

    def test_java_classes(self):
        code = '''
public class Calc extends BaseCalc implements Closeable {
  public int add(int a, int b) { return a + b; }
  private void helper() {}
}
'''
        classes = self.analyzer.analyze_classes(code, 'java')
        assert len(classes) == 1
        c = classes[0]
        assert c.name == 'Calc'
        assert 'add' in c.methods
        assert any(b in (c.inheritance or []) for b in ['BaseCalc', 'Closeable'])
