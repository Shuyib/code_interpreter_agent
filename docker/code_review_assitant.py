"""
This is a code review assistant that provides feedback on code quality, architecture, and data engineering practices.
It uses the Interpreter class to interact with the assistant and provides a custom instruction set to guide its responses.

You require only 531MB of VRAM to run this assistant. But it can be run on CPU as well.

Example usage:
Copy a snippet of code to your clipboard and run the script. It will suggest improvements and best practices.
Author: Shuyib
Date: 2023-10-12

How to run:
```python code_review_assistant.py -f <path_to_code_file> 
#or just run the script without arguments to use clipboard input.
```
"""

import subprocess
import sys
from typing import Dict, Union, Optional
import pkg_resources
import os
from datetime import datetime
import json


def get_package_versions() -> Dict[str, str]:
    """Get versions of installed packages."""
    return {
        pkg.key: pkg.version
        for pkg in pkg_resources.working_set
        if pkg.key in ["requests", "open-interpreter"]
    }


def check_dependencies():
    """Check required dependencies are installed."""
    try:
        installed = get_package_versions()
        required_packages = {
            "requests": "2.31.0",
            "open-interpreter": "0.1.12",
        }

        missing_pkgs = []
        for package, version in required_packages.items():
            if package not in installed:
                missing_pkgs.append(f"{package}=={version}")
            else:
                print(f"{package} version {installed[package]} is installed")

        if missing_pkgs:
            print(f"Missing required packages: {', '.join(missing_pkgs)}")
            print("In Docker, these should be pre-installed.")
            sys.exit(1)

    except Exception as e:
        print(f"Error checking packages: {e}")
        sys.exit(1)


def get_code_input(input_path: Optional[str] = None) -> str:
    """
    Get code input from various sources based on availability.

    Args:
        input_path: Optional path to a file containing code

    Returns:
        The code as a string
    """
    # Try to get code from file if specified
    if input_path:
        try:
            with open(input_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading input file {input_path}: {e}")
            sys.exit(1)

    # Try to use clipboard if available
    try:
        import pyperclip

        code = pyperclip.paste()
        if code.strip():
            print("Using code from clipboard")
            return code
    except ImportError:
        print("Pyperclip not available. Please provide input file.")
    except Exception as e:
        print(f"Error accessing clipboard: {e}")

    # Fallback to example code
    print("No input source available. Using example code...")
    return """
def add_numbers(a, b):
    return a + b

result = add_numbers(5, 10)
print(result)
"""

# Import interpreter here so it's available for the functions below
try:
    from interpreter import interpreter
except ImportError:
    # Handle case where interpreter module isn't available
    pass

def format_assistant_response(response: Union[str, list, dict]) -> str:
    """
    Formats the assistant's response for friendlier display.
    If the response is a dict with a 'content' key, returns its value.
    If it's a list containing such dicts, joins their 'content' values.
    Otherwise, converts the response to a string.
    """
    # Handle dictionary responses with a "content" key.
    if isinstance(response, dict):
        return response.get("content", str(response))

    # Handle a list containing dictionaries or strings.
    if isinstance(response, list):
        formatted = []
        for item in response:
            if isinstance(item, dict) and "content" in item:
                formatted.append(item["content"])
            else:
                formatted.append(str(item))
        return "\n".join(formatted)

    return str(response)

def save_code_review(
    original_code: str, assistant_response: Union[str, list, dict]
) -> str:
    """
    Save original code and a friendlier version of the assistant's review to a timestamped file.

    Parameters
    ----------
    original_code : str
        The original code snippet.
    assistant_response : Union[str, list, dict]
        The assistant's review and suggestions, can be a dict, list, or string.

    Returns
    -------
    str
        The file path of the saved review.
    """
    reviews_dir = os.environ.get("REVIEW_DIR", "code_reviews")
    os.makedirs(reviews_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"code_review_{timestamp}.md"
    filepath = os.path.join(reviews_dir, filename)

    # Format the assistant response to be more user-friendly.
    response_text = format_assistant_response(assistant_response)

    # Write the code review to the markdown file.
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# Code Review\n\n")
        f.write("## Original Code\n")
        f.write("```python\n")
        f.write(original_code)
        f.write("\n```\n\n")
        f.write("## Assistant's Review\n")

        # Write in chunks and flush for very large outputs.
        chunk_size = 2000
        for i in range(0, len(response_text), chunk_size):
            f.write(response_text[i : i + chunk_size])
            f.flush()

        f.write("\n")

    return filepath

def query_assistant(query: str) -> str:
    """
    This function queries the assistant with a given prompt.

    Parameters
    ----------
    query : str
        The prompt to send to the assistant.

    Returns
    -------
    str
        The assistant's response.

    Example
    -------
    >>> query_assistant("What is the capital of France?")
    "The capital of France is Paris."
    """
    return interpreter.chat(query)

def review_code(
    code: str, question: str = "suggest improvements and best practices"
) -> str:
    """Query assistant about code and save review."""
    # Get assistant's response
    prompt = f"Please review the following code snippet and {question}:\n\n{code}"
    response = interpreter.chat(prompt)

    # Save review
    review_file = save_code_review(code, response)
    print(f"\nReview saved to: {review_file}")

    return response

if __name__ == "__main__":
    print("Checking dependencies...")
    check_dependencies()

    # Now import required modules
    from interpreter import interpreter

    # Show interpreter version and model
    try:
        print(f"Open Interpreter version: {interpreter.__version__}")
    except AttributeError:
        print("Interpreter module does not have a __version__ attribute")

    # It is safer to set auto_run to False
    interpreter.auto_run = False

    interpreter.custom_instructions = """
    You are an elite Software Architect & Data Science Expert with a unique blend of engineering precision and analytical insight. Your expertise includes:

    🔹 Code Architecture & Quality
    - Master of clean code principles (SOLID, DRY, KISS)
    - Expert in scalable system design and architectural patterns
    - Documentation specialist emphasizing clarity and completeness

    🔹 Data Engineering Excellence
    - Data pipeline optimization and validation
    - Feature engineering and preprocessing mastery
    - Version control and data lineage tracking

    🔹 Production Engineering
    - Performance optimization specialist
    - Expert in failover strategies and thread safety
    - Resource management and scaling solutions

    🔹 ML/AI Development
    - Algorithm selection and optimization
    - Cross-validation and model evaluation expert
    - Hyperparameter tuning specialist
    - Production deployment architect

    IMPORTANT: Only review code. If the user input doesn't appear to contain programming code, respond with: 
    "I can only review code. Please submit actual programming code for review." 
    Then stop processing further. Examples of non-code inputs include: natural language text, data files, configuration without code context, URLs, or binary data.

    For each code review, provide:
    1. Initial analysis identifying key issues and strengths
    2. Specific, actionable implementation steps with code examples
    3. Testing strategies with sample test code when applicable
    4. Performance and scalability considerations with benchmarking techniques
    5. Best practices implementation roadmap in order of priority

    Your review should include:
    - Concrete implementation steps, not just theoretical advice
    - Example unit tests or test frameworks appropriate for the code
    - Benchmarking approaches to validate improvements
    - Refactoring sequences that can be implemented incrementally
    - Modern library and tool recommendations when relevant

    When reviewing code or data pipelines, always consider:
    - Performance implications with specific optimization techniques
    - Error handling patterns with example implementations
    - Scaling strategies with concrete architectural recommendations
    - Testing methodologies with sample test cases
    - Documentation standards with examples of good documentation
    """

    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Code Review Assistant")
    parser.add_argument("-f", "--file", help="Path to a file containing code to review")
    args = parser.parse_args()

    # Get code from appropriate source
    code = get_code_input(args.file)

    # Review the code
    response = review_code(code)
    print(response)


# Examples you can use to test the assistant
EXAMPLES = [
    """
def add_numbers(a, b):
    return a + b
result = add_numbers(5, 10)
print(result)
""",
    """
    # Random forest classifier that uses random data
    import numpy as np
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score
    # Generate random data
    X = np.random.rand(1000, 20)
    y = np.random.randint(0, 2, size=1000)
    # Split the data into training and testing sets
    # 70% training, 30% testing
    # This is a common split ratio in machine learning
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    # Create a random forest classifier
    # n_estimators is the number of trees in the forest
    # max_depth is the maximum depth of the trees
    # random_state ensures reproducibility
    # This is a common practice in machine learning
    # to ensure that the results can be reproduced
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    # Train the model
    model.fit(X_train, y_train)
    # Make predictions
    y_pred = model.predict(X_test)
    # Calculate accuracy
    # Accuracy is a common metric used to evaluate the performance of a classification model
    # It is the ratio of correctly predicted instances to the total instances
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy}")
    """,
    """
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def simulate_weather_data(num_points: int):
    np.random.seed(42)  # For reproducibility
    base_temp = 20  # Base temperature in Celsius
    temperature_data = base_temp + np.random.normal(0, 2, num_points)  # Simulate temperature with some noise
    return temperature_data

def predict_weather_data(data: np.ndarray):
    # Simple prediction: next value is the same as the last value (for demonstration purposes)
    last_value = data[-1]
    predictions = np.full(10, last_value)  # Predict the next 10 points
    return predictions

def visualize_weather_data(data: np.ndarray, predictions: np.ndarray):
    num_points = len(data)
    time_stamps = [datetime.now() - timedelta(minutes=i) for i in range(num_points)][::-1]
    future_time_stamps = [time_stamps[-1] + timedelta(minutes=i) for i in range(1, len(predictions) + 1)]

    plt.figure(figsize=(10, 5))
    plt.plot(time_stamps, data, label='Current Data')
    plt.plot(future_time_stamps, predictions, label='Predictions', linestyle='--')
    plt.xlabel('Time')
    plt.ylabel('Temperature (°C)')
    plt.title('Simulated Weather Data and Predictions')
    plt.legend()
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    num_points = 100  # Number of data points to simulate
    weather_data = simulate_weather_data(num_points)
    weather_predictions = predict_weather_data(weather_data)
    visualize_weather_data(weather_data, weather_predictions)
""",
]
