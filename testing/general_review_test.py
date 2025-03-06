"""Test cases for the Code Review Assistant to demonstrate comprehensive reviews.

This file contains various code examples designed to test different aspects of
code quality review, from basic function design to complex architecture patterns.
Each example is designed to have specific areas for improvement that should be
addressed in a thorough review.
"""

import sys
import time


# Example 1: Simple function with performance issues
def fibonacci(n):
    """Calculate the nth Fibonacci number recursively."""
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# Example 2: Missing error handling
def divide_numbers(a, b):
    """Divide two numbers."""
    return a / b


# Example 3: Poor data handling
def process_user_data(data):
    """Process user data and return results."""
    results = []
    
    for item in data:
        # Direct dictionary access without checks
        user_id = item['id']
        name = item['name']
        age = item['age']
        
        # Simple processing without validation
        processed_item = {
            'user_id': user_id,
            'full_name': name,
            'age_in_months': age * 12
        }
        results.append(processed_item)
    
    return results


# Example 4: Poor class design (missing docstrings, no proper encapsulation)
class DataProcessor:
    def __init__(self, data_source):
        self.source = data_source
        self.processed = False
        self.results = []
    
    def process(self):
        # Simulate processing
        time.sleep(1)
        self.results = [f"Processed {item}" for item in self.source]
        self.processed = True
    
    def get_results(self):
        return self.results


# Example 5: Singleton implementation with issues
class DatabaseConnection:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            # Initialize connection (simplified)
            cls._instance.connected = True
        return cls._instance
    
    def query(self, sql):
        # No SQL injection protection
        return f"Results for: {sql}"


# Example 6: Poor resource management
def read_large_file(filename):
    """Read a large file and return its contents."""
    file = open(filename, 'r')
    content = file.read()
    # file is never closed!
    return content


# Example 7: Inefficient algorithm
def find_duplicates(items):
    """Find duplicate items in a list."""
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates


if __name__ == "__main__":
    # Example usage
    print(fibonacci(10))
    print(divide_numbers(10, 2))
    
    sample_data = [
        {'id': 1, 'name': 'Alice', 'age': 30},
        {'id': 2, 'name': 'Bob', 'age': 25},
    ]
    print(process_user_data(sample_data))
    
    processor = DataProcessor(['item1', 'item2'])
    processor.process()
    print(processor.get_results())
    
    db = DatabaseConnection()
    print(db.query("SELECT * FROM users WHERE name='John'"))
    
    # This would fail in practice
    # print(read_large_file("nonexistent_file.txt"))
    
    numbers = [1, 2, 3, 2, 4, 5, 3, 6]
    print(find_duplicates(numbers))
