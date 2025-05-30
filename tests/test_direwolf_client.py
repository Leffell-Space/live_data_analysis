"""
Test script for get_from_direwolf.py using staggered_kiss_server.py
This script runs the KISS server in a thread and then connects the client to it.
"""

import os
import sys
import threading
import time
import tempfile

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.get_from_direwolf import main as client_main # pylint: disable=wrong-import-position
from tests.staggered_kiss_server import load_frames_from_file, run_server # pylint: disable=wrong-import-position

def create_test_data():
    """Create sample KISS/APRS test data"""
    # Simple APRS position report in KISS format
    # This is a basic KISS frame with APRS data for a position
    test_data = [
        # KISS Frame with APRS position (C0 = KISS delimiter)
        b'\xc0\x00KK6GPV-9>APRS,WIDE1-1,WIDE2-1:!3722.55N/12159.14W-PHG2280/A=000123Test Balloon\xc0', # pylint: disable=line-too-long
        # Another position with different coordinates
        b'\xc0\x00KK6GPV-9>APRS,WIDE1-1,WIDE2-1:!3723.00N/12158.50W-PHG2280/A=000456Second Point\xc0', # pylint: disable=line-too-long
        # A third position with increased altitude
        b'\xc0\x00KK6GPV-9>APRS,WIDE1-1,WIDE2-1:!3723.25N/12158.25W-PHG2280/A=000789Third Point\xc0'
    ]

    # Write test data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as f:
        for frame in test_data:
            f.write(frame)
        temp_filename = f.name

    return temp_filename

def server_thread(test_file, delay=2):
    """Run the KISS server in a thread"""
    frames = load_frames_from_file(test_file)
    run_server(frames, delay=delay)

def run_test(test_duration=10):
    """Run the complete test with both server and client"""
    # Create test data file
    test_file = create_test_data()
    print(f"Created test data file: {test_file}")

    # Start server in a separate thread
    server = threading.Thread(target=server_thread, args=(test_file, 2))
    server.daemon = True  # Thread will exit when main program exits
    server.start()

    # Give the server a moment to start up
    time.sleep(1)

    # Set a timeout for the client
    client_timer = threading.Timer(test_duration, lambda: sys.exit(0))
    client_timer.daemon = True
    client_timer.start()

    # Run the client
    try:
        client_main()  # This will connect to the server and process frames
    except SystemExit:
        print("Test completed successfully")
    finally:
        # Clean up the temporary file
        try:
            os.unlink(test_file)
        except OSError as e:
            print(f"Could not delete temporary file: {e}")

if __name__ == "__main__":
    run_test()
