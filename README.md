# live_data_analysis

Realtime analysis of APRS data

## Overview

This project provides tools for receiving, decoding, and visualizing APRS (Automatic Packet Reporting System) data in real time. It supports both online APRS-IS sources and local KISS TNCs (such as Direwolf), and can output position data to KML files for visualization in Google Earth.

## Features

- Connect to APRS-IS servers and stream live APRS packets for a specified callsign
- Connect to a local KISS TNC (e.g., Direwolf) and decode APRS packets
- Extract and store latitude, longitude, and altitude from received packets
- Output received positions to KML files for mapping and visualization
- Auto-refresh KML link for live tracking in Google Earth

## Requirements

- Python 3.8+
- [aprslib](https://github.com/rossengeorgiev/aprs-python)
- [simplekml](https://simplekml.readthedocs.io/en/latest/)

Install dependencies with:
```sh
pip install aprslib simplekml
```

## Usage

### 1. Get Data from APRS-IS

Edit `src/get_data_online.py` to set your target `CALLSIGN`, then run:
```sh
python src/get_data_online.py
```
This will print position updates for the specified callsign.

### 2. Get Data from Direwolf (KISS TNC)

Make sure Direwolf is running and listening on port 8001. Then run:
```sh
python src/get_from_direwolf.py
```
This will decode incoming APRS packets, print positions, and update `tracker.kml` and `tracker_link.kml` for Google Earth.

## Project Structure

```
live_data_analysis/
├── src/
│   ├── get_data_online.py
│   └── get_from_direwolf.py
├── tracker.kml
├── tracker_link.kml
└── README.md
```

## Notes

- For best results, ensure your Python environment matches the one where dependencies are installed.
- To visualize live tracks, open `tracker_link.kml` in Google Earth.

## License

See LICENSE