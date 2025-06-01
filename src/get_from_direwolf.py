"""
KISS Protocol Test Client
Connects to a KISS server (e.g., kiss_test_server.py) on port 8001 and prints received APRS packets.
Retains all received points and writes them to tracker.kml.
Also creates/updates tracker_link.kml for Google Earth auto-refresh.
"""

import socket
import os
import urllib.parse
import string
import datetime
import sys
import re
import aprslib
import simplekml
import dotenv #env variables
import pytz  #timezones

if len(sys.argv) > 1:
    CALLSIGN = sys.argv[1]
    print(f"CALLSIGN = {CALLSIGN}")

dotenv.load_dotenv()
CALLSIGN = os.getenv("CALLSIGN")
print(f"CALLSIGN = {CALLSIGN}")

positions = []

CALLSIGN_FILTER = CALLSIGN  # Add callsign

def get_eastern_time_str():
    """
    Decode a KISS frame to extract the APRS packet string in standard format.
    """
    eastern = pytz.timezone("US/Eastern")  # Get the US/Eastern timezone object
    return datetime.datetime.now(tz=pytz.utc).astimezone(eastern).strftime("%Y-%m-%d %I:%M:%S %p %Z")    # Return the current time in US/Eastern pylint: disable=line-too-long


def decode_kiss_frame(data):
    """
    Decode a KISS frame to extract the APRS packet string in standard format.
    """
    result = None
    if len(data) >= 3 and data[0] == 0xC0 and data[-1] == 0xC0:
        payload = data[1:-1]  # Remove KISS framing
        if len(payload) >= 16:
            # Remove KISS command byte (first byte)
            payload = payload[1:]
            # Parse AX.25 address fields
            addresses = []
            addr_end = None
            for i in range(0, 56, 7):  # Up to 8 addresses (7 bytes each)
                if i + 7 > len(payload):
                    break
                addr = payload[i:i+7]
                callsign = ''.join([chr((b >> 1) & 0x7F) for b in addr[:6]]).strip()
                ssid = (addr[6] >> 1) & 0x0F
                last = addr[6] & 0x01
                if ssid:
                    callsign = f"{callsign}-{ssid}"
                addresses.append(callsign)
                if last:
                    addr_end = i + 7
                    break
            if addr_end is not None and len(payload) >= addr_end + 3:
                # APRS body (skip Control and PID)
                body = payload[addr_end + 2:]
                # Compose Direwolf-style packet
                if len(addresses) >= 2:
                    header = addresses[1] + '>' + addresses[0]
                    if len(addresses) > 2:
                        header += ',' + ','.join(addresses[2:])
                    try:
                        body_str = body.decode('ascii', errors='replace')
                        result = f"{header}:{body_str}".strip()
                    except UnicodeDecodeError:
                        result = None
    return result

def parse_aprs(packet_str):
    """
    Parse APRS packet string and extract lat, lon, alt, and from callsign if available.
    For raw NMEA packets, extract from_call and lat/lon from $GPRMC if present.
    """
    # Remove non-printable characters
    packet_str = ''.join(filter(lambda x: x in string.printable, packet_str))
    try:
        # Try normal aprslib parsing first
        parsed = aprslib.parse(packet_str)
        lat = parsed.get('latitude')
        lon = parsed.get('longitude')
        alt = parsed.get('altitude')
        from_call = parsed.get('from')
        return lat, lon, alt, from_call
    except Exception: # pylint: disable=broad-except
        # Fallback: extract from_call manually for NMEA packets
        try:
            # Format: FROMCALL>...:body
            if '>' in packet_str:
                from_call = packet_str.split('>',maxsplit=1)[0].strip()
            else:
                from_call = None
            # Try to extract lat/lon from $GPRMC
            match = re.search(r'\$GPRMC,([^,]*),A,([^,]*),([NS]),([^,]*),([EW])', packet_str)
            if match:
                # Example: $GPRMC,021851,A,3348.8470,N,11800.1685,W,...
                lat_raw = match.group(2)
                lat_dir = match.group(3)
                lon_raw = match.group(4)
                lon_dir = match.group(5)
                # Convert to decimal degrees
                lat = int(lat_raw[:2]) + float(lat_raw[2:]) / 60.0
                if lat_dir == 'S':
                    lat = -lat
                lon = int(lon_raw[:3]) + float(lon_raw[3:]) / 60.0
                if lon_dir == 'W':
                    lon = -lon
                return lat, lon, None, from_call
            return None, None, None, from_call
        except Exception as e: # pylint: disable=broad-except
            print(f"APRS parse error: {e} | Packet: {repr(packet_str)}")
            return None, None, None, None

def write_kml(points, filename=None):
    """
    Creates a KML file with placemarks for a list of geographic points.

    Each point is added as a placemark with its latitude, longitude, and altitude.
    The placemark's name is set to the current timestamp in US/Eastern time.
    If no filename is provided, the KML file is saved as 'tracker.kml' 
    in the same directory as this script.
    """
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "tracker.kml")
    kml = simplekml.Kml()
    for lat, lon, alt, timestamp in points:
        pnt = kml.newpoint(name="Received at " + timestamp, coords=[(lon, lat, alt if alt else 0)])
        pnt.altitudemode = simplekml.AltitudeMode.absolute
    kml.save(filename)

def write_networklink_kml(target_path=None, link_filename=None, refresh_interval=5):
    """
    Write a KML NetworkLink referencing another KML file for live updates (e.g., in Google Earth).

    """
    if target_path is None:
        target_path = os.path.join(os.path.dirname(__file__), "tracker.kml")
    if link_filename is None:
        link_filename = os.path.join(os.path.dirname(__file__), "tracker_link.kml")
    abs_path = os.path.abspath(target_path)
    href = 'file:///' + urllib.parse.quote(abs_path.replace("\\", "/"))
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
    with open(link_filename, "w", encoding="utf-8") as f:
        f.write(kml_content)

# Clear the KML file at startup so only new, filtered positions are shown
def clear_kml(filename=None):
    """
    Clears the contents of a KML file. Used for clearing only tracker.kml not tracker_link.kml.
    """
    if filename is None:
        filename = os.path.join(os.path.dirname(__file__), "tracker.kml")
    kml = simplekml.Kml()
    kml.save(filename)

def process_aprs_packet(packet):
    """
    Process a decoded APRS packet: parse, filter, print, and update KML if appropriate.
    """
    if packet and ':' in packet:
        lat, lon, alt, from_call = parse_aprs(packet)
        if lat is not None and lon is not None:
            # Filter by base callsign (ignore SSID, case-insensitive)
            base_call = from_call.split('-')[0].strip().upper() if from_call else None
            filter_base = CALLSIGN_FILTER.split('-', maxsplit=1)[0].strip().upper() if CALLSIGN_FILTER else None #pylint: disable=line-too-long
            if filter_base is None or (base_call and base_call == filter_base):
                timestamp = get_eastern_time_str()
                print(f"Accepted: {lat}, {lon}, {alt}, {from_call}, {timestamp}")
                positions.append((lat, lon, alt, timestamp))
                write_kml(positions)
            else:
                print(f"Ignored packet from {from_call} (filter: {CALLSIGN_FILTER})")
        else:
            print(f"Received APRS packet but could not parse position: {packet}")
    elif packet:
        print(f"Received malformed APRS packet (no body): {packet}")
        print(f"Raw packet: {repr(packet)}")

def main(host='localhost', port=8001):
    '''Always create/update the NetworkLink KML at startup'''
    clear_kml()  # <-- Clear KML file before starting
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
                process_aprs_packet(packet)
    except KeyboardInterrupt:
        print("\nStopped by user.")
    except OSError as e:
        print(f"Socket error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()
