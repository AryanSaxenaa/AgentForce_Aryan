"""
Debug script to test Java function analyzer.
"""
from src.analyzers.function_analyzer import FunctionAnalyzer

def test_java_parsing():
    analyzer = FunctionAnalyzer()
    
    java_code = '''
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
    
    public String greet(String name) {
        return "Hello, " + name;
    }
}
'''
    
    try:
        functions = analyzer.analyze_functions(java_code, 'java')
        print(f"Found {len(functions)} functions:")
        
        for func in functions:
            print(f"  Function: {func.name}")
            print(f"    Parameters: {[(p.name, p.type_hint) for p in func.parameters]}")
            print(f"    Return type: {func.return_type}")
            print(f"    Line range: {func.line_range}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_java_parsing()