import aprslib 

callsign = "GW2598"  # Replace with your callsign

def callback(packet):
    try:
        if 'latitude' in packet and 'longitude' in packet:
            position_info = f"Position: {packet['latitude']}, {packet['longitude']}"
            
            # Add altitude information if available
            if 'altitude' in packet:
                position_info += f", Altitude: {packet['altitude']} meters"
            
            print(position_info)
        else:
            print("No position data in this packet")
    except Exception as e:
        print(f"Error processing packet: {e}")

AIS = aprslib.IS(callsign)
AIS.connect()
AIS.consumer(callback, raw=False)
