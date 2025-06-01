"""
Test script for get_from_direwolf.py using staggered_kiss_server.py
This script runs the KISS server in a thread and then connects the client to it.
"""

import os
import sys
import threading
import time
import tempfile
import unittest
from unittest.mock import patch

# Add the parent directory to the path so we can import the modules
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

# Import our modules explicitly to avoid module name collisions
from src.get_from_direwolf import main as client_main  # pylint: disable=wrong-import-position
from tests.staggered_kiss_server import load_frames_from_file, run_server  # pylint: disable=wrong-import-position

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

class TestDirewolfClient(unittest.TestCase):
    """Test case for the Direwolf KISS client"""

    def setUp(self):
        """Setup test environment"""
        self.test_file = create_test_data()
        print(f"Created test data file: {self.test_file}")

        # Start server in a separate thread
        self.server = threading.Thread(target=server_thread, args=(self.test_file, 2))
        self.server.daemon = True
        self.server.start()

        # Give the server a moment to start up
        time.sleep(1)

    def tearDown(self):
        """Clean up after test"""
        # Clean up the temporary file
        try:
            os.unlink(self.test_file)
        except OSError as e:
            print(f"Could not delete temporary file: {e}")

    @patch('src.get_from_direwolf.process_aprs_data')
    def test_client_receives_data(self, mock_process_aprs_data):
        """Test that client receives and processes data from the server"""
        # Set a timeout for the client (shorter for unit tests)
        test_duration = 8  # Enough time to receive all 3 test frames

        client_timer = threading.Timer(test_duration, lambda: sys.exit(0))
        client_timer.daemon = True
        client_timer.start()

        # Run the client
        try:
            client_main()  # This will connect to the server and process frames
        except SystemExit:
            pass

        # Assert that process_aprs_data was called at least 3 times (for our 3 test frames)
        self.assertGreaterEqual(mock_process_aprs_data.call_count, 3,
                               "Client should have processed at least 3 APRS frames")

        # Check the content of the calls to verify data was processed correctly
        # We can check for specific callsigns, coordinates or other data in the processed frames
        for call in mock_process_aprs_data.call_args_list:
            args, _ = call
            packet = args[0]
            self.assertIn("KK6GPV-9", str(packet),
                          "Expected callsign not found in processed packet")

def run_test():
    """Run the test as a standalone script"""
    unittest.main(argv=['first-arg-is-ignored'], exit=False)

# Only run the test when this script is executed directly
if __name__ == "__main__":
    run_test()
