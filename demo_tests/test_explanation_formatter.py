from src.utils.explanation_formatter import ExplanationFormatter

class DummyFunc:
    def __init__(self, name, args=None, complexity=1, docstring=None):
        self.name = name
        self.args = args or []
        self.complexity = complexity
        self.docstring = docstring

class DummyAnalysis:
    def __init__(self):
        self.language = 'python'
        self.functions = [DummyFunc('add', ['a','b'])]
        self.classes = []
        self.imports = ['math']
        self.edge_cases = ['division by zero']
        self.complexity_score = 1

class DummyTest:
    def __init__(self, name, test_type='unit', function_name='add', description='basic test'):
        class T:
            def __init__(self, v):
                self.value = v
        t = T(test_type)
        self.name = name
        self.test_type = t
        self.function_name = function_name
        self.description = description


def test_analysis_explanation_smoke():
    a = DummyAnalysis()
    out = ExplanationFormatter.analysis_explanation(a)
    assert 'Language: python' in out
    assert 'Functions: [' in out


def test_test_generation_reasoning_smoke():
    a = DummyAnalysis()
    tests = [DummyTest('test_add_basic', 'unit', 'add', 'basic')]
    out = ExplanationFormatter.test_generation_reasoning(a, tests)
    assert 'Test generation reasoning:' in out


def test_edge_case_explanations_smoke():
    a = DummyAnalysis()
    out = ExplanationFormatter.edge_case_explanations(a)
    assert isinstance(out, list)
    assert out and 'description' in out[0]
