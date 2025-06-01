"""
Simple script to run the staggered_kiss_server and then get_from_direwolf.py
"""
import os
import subprocess
import sys
import time
import logging

# Make sure we're running from the project root (one directory up from this file)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.chdir(project_root)

# Paths to the scripts
server_script = os.path.join(project_root, 'tests', 'staggered_kiss_server.py')
client_script = os.path.join(project_root, 'src', 'get_from_direwolf.py')

print(f"Starting server: {server_script}")
server_proc = subprocess.Popen(['python', server_script]) #pylint: disable=consider-using-with

# Give the server a moment to start up
time.sleep(2)

print(f"Running client: {client_script}")
result = subprocess.run(['python', client_script], check=False)
logging.info("Client completed with exit code: %d", result.returncode)

# Clean up the server process
server_proc.terminate()
try:
    server_proc.wait(timeout=5)
except subprocess.TimeoutExpired:
    server_proc.kill()

# Exit with the same code as the client
sys.exit(result.returncode)
