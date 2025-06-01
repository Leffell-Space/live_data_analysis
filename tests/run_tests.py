"""
Simple script to run the direwolf client tests directly,
avoiding the Python unittest discovery mechanism which can
cause conflicts with other tests.
"""
import os
import subprocess
import sys
import logging

# Make sure we're running from the project root (one directory up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)

# Run the specific test script directly
test_script = os.path.join(project_root, 'tests', 'test_direwolf_client.py')
print(f"Running test: {test_script}")

# Execute the test script as a subprocess
result = subprocess.run(['python', test_script], check=False)
logging.info("Test completed with exit code: %d", result.returncode)

# Exit with the same code as the test
sys.exit(result.returncode)
