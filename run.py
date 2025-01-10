import os
from src.web.app import app

# Print current working directory and file paths for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"Location of run.py: {os.path.abspath(__file__)}")

if __name__ == "__main__":
    app.run(debug=True)
