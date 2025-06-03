"""
This script connects to port 8001 on specified hosts and dumps the data received.  
It is useful for debugging or monitoring services running on that port.
It has no other use than for testing.
"""
import socket

def dump_port_8001(hosts):
    """Connect to port 8001 on specified hosts and dump the data received."""
    port = 8001
    for host in hosts:
        try:
            with socket.create_connection((host, port), timeout=1) as s:
                print(f"Connected to {host}:{port}. Dumping data:")
                while True:
                    data = s.recv(4096)
                    if not data:
                        break
                    print(data.decode(errors="replace"), end="")
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            print(f"Could not connect to {host}:{port} ({e})")

if __name__ == "__main__":
    hosts_to_scan = [
        "127.0.0.1",
        "localhost",
        # Add more hosts as needed
    ]
    dump_port_8001(hosts_to_scan)
