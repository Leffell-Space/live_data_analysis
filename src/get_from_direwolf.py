"""
KISS Protocol Test Client
Connects to a KISS server (e.g., kiss_test_server.py) on port 8001 and prints received APRS packets.
Retains all received points and writes them to tracker.kml.
Also creates/updates tracker_link.kml for Google Earth auto-refresh.
"""

import socket
import aprslib
import os
import simplekml

positions = []

def decode_kiss_frame(data):
    """
    Decode a KISS frame to extract the APRS packet string.
    """
    if len(data) < 3:
        return None
    if data[0] == 0xC0 and data[1] == 0x00 and data[-1] == 0xC0:
        payload = data[2:-1]
        payload = payload.replace(b'\xdb\xdc', b'\xc0')
        payload = payload.replace(b'\xdb\xdd', b'\xdb')
        try:
            packet_str = payload.decode('utf-8', errors='ignore').strip()
            return packet_str
        except Exception:
            return None
    return None

def parse_aprs(packet_str):
    """
    Parse APRS packet string and extract lat, lon, alt if available.
    """
    try:
        parsed = aprslib.parse(packet_str)
        lat = parsed.get('latitude')
        lon = parsed.get('longitude')
        alt = parsed.get('altitude')
        return lat, lon, alt
    except Exception as e:
        print(f"APRS parse error: {e}")
        return None, None, None

def write_kml(points, filename=None):
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "tracker.kml")
    kml = simplekml.Kml()
    for idx, (lat, lon, alt) in enumerate(points):
        pnt = kml.newpoint(name=f"Balloon {idx+1}", coords=[(lon, lat, alt if alt else 0)])
        pnt.altitudemode = simplekml.AltitudeMode.absolute
    kml.save(filename)

def write_networklink_kml(target_path=None, link_filename=None, refresh_interval=5):
    if target_path is None:
        target_path = os.path.join(os.path.dirname(__file__), "tracker.kml")
    if link_filename is None:
        link_filename = os.path.join(os.path.dirname(__file__), "tracker_link.kml")
    abs_path = os.path.abspath(target_path)
    href = f"file://{abs_path}"
    kml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <NetworkLink>
    <name>Live Balloon Tracker</name>
    <Link>
      <href>{href}</href>
      <refreshMode>onInterval</refreshMode>
      <refreshInterval>{refresh_interval}</refreshInterval>
    </Link>
  </NetworkLink>
</kml>
"""
    with open(link_filename, "w") as f:
        f.write(kml_content)

def main(host='localhost', port=8001):
    # Always create/update the NetworkLink KML at startup
    write_networklink_kml()
    print(f"Connecting to KISS server on {host}:{port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
        print("Connected. Waiting for APRS packets...")
        buffer = b''
        while True:
            data = sock.recv(1024)
            if not data:
                print("Connection closed by server.")
                break
            buffer += data
            # Process complete KISS frames
            while True:
                start = buffer.find(0xC0)
                if start == -1:
                    break
                end = buffer.find(0xC0, start + 1)
                if end == -1:
                    break
                frame = buffer[start:end+1]
                buffer = buffer[end+1:]
                packet = decode_kiss_frame(frame)
                if packet:
                    lat, lon, alt = parse_aprs(packet)
                    if lat is not None and lon is not None:
                        print(f"Lat: {lat}, Lon: {lon}, Alt: {alt if alt is not None else 'N/A'}")
                        positions.append((lat, lon, alt))
                        write_kml(positions)  # Now always writes to src/tracker.kml
                    else:
                        print(f"Received APRS packet but could not parse position: {packet}")
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()