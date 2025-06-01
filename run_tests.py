"""
Simple script to run the direwolf client tests directly,
avoiding the Python unittest discovery mechanism which can
cause conflicts with other tests.
"""
import os
import subprocess

# Make sure we're running from the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)

# Run the specific test script directly
test_script = os.path.join(project_root, 'tests', 'test_direwolf_client.py')
print(f"Running test: {test_script}")

# Execute the test script as a subprocess
subprocess.run(['python', test_script], check=True)
