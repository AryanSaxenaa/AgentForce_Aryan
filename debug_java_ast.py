"""
Debug script to examine Java AST structure.
"""
from src.analyzers.code_parser import CodeParser

def debug_java_ast():
    parser = CodeParser()
    
    java_code = '''public int add(int a, int b) {
    return a + b;
}'''
    
    try:
        ast = parser.parse_code(java_code, 'java')
        
        def print_ast(node, indent=0):
            print("  " * indent + f"{node.node.type}: '{node.text[:50].replace(chr(10), '\\n')}'")
            for child in node.node.children:
                from src.analyzers.code_parser import ASTNode
                child_node = ASTNode(child, ast.source_code, ast.language)
                print_ast(child_node, indent + 1)
        
        print_ast(ast)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_java_ast()