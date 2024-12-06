import os
import pathlib

def create_project_structure():
    # Define the base structure
    project_structure = {
        "trading-assistant": {
            "README.md": "# Trading Assistant\nGen-Z focused AI Trading Assistant",
            "requirements.txt": """
yfinance>=0.2.0
pandas>=1.5.0
numpy>=1.21.0
ta>=0.10.0
            """.strip(),
            "setup.py": """
from setuptools import setup, find_packages

setup(
    name="trading_assistant",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
            """.strip(),
            "src": {
                "trading_assistant": {
                    "__init__.py": "",
                    "core": {
                        "__init__.py": "",
                        "personas.py": "",
                        "market_data.py": "",
                        "strategy.py": ""
                    },
                    "commands": {
                        "__init__.py": "",
                        "scan.py": "",
                        "strategy.py": "",
                        "build.py": "",
                        "analyze.py": "",
                        "backtest.py": ""
                    },
                    "utils": {
                        "__init__.py": "",
                        "helpers.py": ""
                    }
                }
            },
            "tests": {
                "__init__.py": ""
            }
        }
    }
    
    def create_structure(base_path, structure):
        for name, content in structure.items():
            path = os.path.join(base_path, name)
            
            if isinstance(content, dict):
                # If it's a dictionary, it's a directory
                os.makedirs(path, exist_ok=True)
                create_structure(path, content)
            else:
                # If it's not a dictionary, it's a file
                with open(path, 'w') as f:
                    f.write(content)
    
    # Get the current working directory
    current_dir = os.getcwd()
    
    # Create the project structure
    create_structure(current_dir, project_structure)
    
    print("Project structure created successfully!")
    print("\nNext steps:")
    print("1. cd trading-assistant")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate  # On Windows: venv\\Scripts\\activate")
    print("4. pip install -r requirements.txt")

if __name__ == "__main__":
    create_project_structure()