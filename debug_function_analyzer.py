"""
Debug script to test function analyzer.
"""
from src.analyzers.function_analyzer import FunctionAnalyzer

def test_python_parsing():
    analyzer = FunctionAnalyzer()
    
    python_code = '''
def add(a, b):
    """Add two numbers."""
    return a + b

def greet(name: str = "World") -> str:
    """Greet someone."""
    return f"Hello, {name}!"
'''
    
    try:
        functions = analyzer.analyze_functions(python_code, 'python')
        print(f"Found {len(functions)} functions:")
        
        for func in functions:
            print(f"  Function: {func.name}")
            print(f"    Parameters: {[p.name for p in func.parameters]}")
            print(f"    Return type: {func.return_type}")
            print(f"    Docstring: {func.docstring}")
            print(f"    Line range: {func.line_range}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_python_parsing()