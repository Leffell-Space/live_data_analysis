import unittest
import sys
import os
import threading
import time
import socket
import tempfile
import shutil

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
from tests.staggered_kiss_server import run_server
import get_from_direwolf

class TestClientServerIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create test APRS packets in KISS format
        self.test_frames = [
            b'\xC0\x00K1ABC>APRS,TCPIP*:=3751.50N/12227.93W-Test Balloon 1\xC0',
            b'\xC0\x00K1ABC>APRS,TCPIP*:=3752.10N/12227.50W-Test Balloon 2\xC0',
            b'\xC0\x00K1ABC>APRS,TCPIP*:=3752.80N/12226.90W-Test Balloon 3\xC0'
        ]
        
        # Create temporary directory for KML files
        self.temp_dir = tempfile.mkdtemp()
        self.kml_path = os.path.join(self.temp_dir, "tracker.kml")
        self.link_path = os.path.join(self.temp_dir, "tracker_link.kml")
        
        # Keep track of original directory for KML files
        self.original_dir = os.path.dirname(os.path.abspath(get_from_direwolf.__file__))
        
    def tearDown(self):
        # Clean up temporary directory
        shutil.rmtree(self.temp_dir)
        
    def test_end_to_end(self):
        # Patch get_from_direwolf's write_kml and write_networklink_kml to use temp dir
        original_write_kml = get_from_direwolf.write_kml
        original_write_networklink = get_from_direwolf.write_networklink_kml
        
        def patched_write_kml(points, filename=None):
            if filename is None:
                filename = self.kml_path
            return original_write_kml(points, filename)
            
        def patched_write_networklink(target_path=None, link_filename=None, refresh_interval=5):
            if target_path is None:
                target_path = self.kml_path
            if link_filename is None:
                link_filename = self.link_path
            return original_write_networklink(target_path, link_filename, refresh_interval)
            
        get_from_direwolf.write_kml = patched_write_kml
        get_from_direwolf.write_networklink_kml = patched_write_networklink
        
        try:
            # Start server in a thread
            server_port = 8003
            server_thread = threading.Thread(
                target=run_server,
                args=(self.test_frames, "localhost", server_port, 0.1)
            )
            server_thread.daemon = True
            server_thread.start()
            
            # Give server time to start
            time.sleep(0.2)
            
            # Reset positions
            get_from_direwolf.positions = []
            
            # Create client thread
            client_thread = threading.Thread(
                target=get_from_direwolf.main,
                args=("localhost", server_port)
            )
            client_thread.daemon = True
            client_thread.start()
            
            # Wait for client to process data (adjust timing as needed)
            time.sleep(1.5)
            
            # Verify positions were collected
            self.assertTrue(len(get_from_direwolf.positions) > 0, 
                           f"Expected positions to be collected, got {len(get_from_direwolf.positions)}")
            
            # Verify KML file was created
            self.assertTrue(os.path.exists(self.kml_path), 
                           f"KML file not created at {self.kml_path}")
            
            # Verify network link file was created
            self.assertTrue(os.path.exists(self.link_path), 
                           f"KML network link not created at {self.link_path}")
            
        finally:
            # Restore original functions
            get_from_direwolf.write_kml = original_write_kml
            get_from_direwolf.write_networklink_kml = original_write_networklink

if __name__ == '__main__':
    unittest.main()
