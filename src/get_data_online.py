"""Gets data from online APRS tracking systems."""
import aprslib

CALLSIGN = "KD2CIF-1" #this is a test CALLSIGN located in Staten Island

latitudes = []
longitudes = []

def callback(packet):
    """Callback that displays position information from AIS."""
    try:
        if packet['from'] == CALLSIGN and 'latitude' in packet and 'longitude' in packet:
            latitudes.append(packet['latitude'])
            longitudes.append(packet['longitude'])
            position_info = f"{CALLSIGN} - Position: {packet['latitude']}, {packet['longitude']}"
            if 'altitude' in packet:
                position_info += f", Altitude: {packet['altitude']} meters"
            print(position_info)
    except Exception as e: # pylint: disable=broad-except
        print(f"{CALLSIGN} - Error processing packet: {e}")

AIS = aprslib.IS(CALLSIGN)
AIS.connect()
AIS.consumer(callback, raw=False)
