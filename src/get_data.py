import aprslib 

callsign = ""  # Replace with your callsign

def callback(packet):
    try:
        # Only process packets from your callsign
        if packet.get('from') == callsign and 'latitude' in packet and 'longitude' in packet:
            position_info = f"{callsign} - Position: {packet['latitude']}, {packet['longitude']}"
            
            # Add altitude information if available
            if 'altitude' in packet:
                position_info += f", Altitude: {packet['altitude']} meters"
            
            print(position_info)
        # else:
        #     print(f"{callsign} - No position data in this packet or not from your callsign")
    except Exception as e:
        print(f"{callsign} - Error processing packet: {e}")

AIS = aprslib.IS(callsign)
AIS.connect()
AIS.consumer(callback, raw=False)
