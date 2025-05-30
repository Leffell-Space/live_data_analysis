import aprslib 

callsign = "KD2CIF-1" #this is a test callsign located in Staten Island

latitudes = []
longitudes = []

def callback(packet):
    try:
        if packet['from'] == callsign and 'latitude' in packet and 'longitude' in packet:
            latitudes.append(packet['latitude'])
            longitudes.append(packet['longitude'])
            position_info = f"{callsign} - Position: {packet['latitude']}, {packet['longitude']}"
            if 'altitude' in packet:
                position_info += f", Altitude: {packet['altitude']} meters"
            print(position_info)
    except Exception as e:
        print(f"{callsign} - Error processing packet: {e}")

AIS = aprslib.IS(callsign)
AIS.connect()
AIS.consumer(callback, raw=False)
