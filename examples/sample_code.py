"""
Sample Python code for testing the Test Case Generator Bot
"""
import math
from typing import List, Optional

def calculate_average(numbers: List[float]) -> float:
    """Calculate the average of a list of numbers.
    
    Args:
        numbers: List of numbers to average
        
    Returns:
        The average of the numbers
        
    Raises:
        ValueError: If the list is empty
        TypeError: If any element is not a number
    """
    if not numbers:
        raise ValueError("Cannot calculate average of empty list")
    
    total = sum(numbers)
    return total / len(numbers)

def find_max_value(data: List[int]) -> Optional[int]:
    """Find the maximum value in a list.
    
    Args:
        data: List of integers
        
    Returns:
        Maximum value or None if list is empty
    """
    if not data:
        return None
    
    max_val = data[0]
    for num in data:
        if num > max_val:
            max_val = num
    
    return max_val

def fibonacci(n: int) -> int:
    """Calculate the nth Fibonacci number.
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("Fibonacci sequence is not defined for negative numbers")
    
    if n <= 1:
        return n
    
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    
    return b

def process_user_data(user_input: str) -> dict:
    """Process user input and return structured data.
    
    This function demonstrates several potential edge cases and risks.
    """
    # Potential division by zero
    score = len(user_input) / len(user_input.split())
    
    # Potential index error
    first_char = user_input[0]
    
    # File operation (integration test candidate)
    with open('user_data.txt', 'w') as f:
        f.write(user_input)
    
    # Nested loops (performance risk)
    processed_chars = []
    for char in user_input:
        for i in range(len(user_input)):
            if char == user_input[i]:
                processed_chars.append((char, i))
    
    return {
        'score': score,
        'first_char': first_char,
        'processed_chars': processed_chars,
        'length': len(user_input)
    }

class Calculator:
    """Simple calculator class for demonstration."""
    
    def __init__(self):
        self.history = []
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def divide(self, a: float, b: float) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        
        result = a / b
        self.history.append(f"{a} / {b} = {result}")
        return result
    
    def get_history(self) -> List[str]:
        """Get calculation history."""
        return self.history.copy()
    
    def clear_history(self):
        """Clear calculation history."""
        self.history.clear()