# Live Balloon Tracking

This project provides tools for receiving, decoding, and visualizing APRS (Automatic Packet Reporting System) data in real time. It supports both online APRS-IS sources and Direwolf, and can output position data to KML files for visualization in Google Earth.

## Features

- Connect to a local KISS TNC (e.g., Direwolf) and decode APRS packets
- Extract and store latitude, longitude, and altitude from received packets
- Output received positions to KML files for mapping and visualization
- Auto-refresh KML link for live tracking in Google Earth

## Requirements

- Python 3.13.3
- aprslib 0.7.2
- dotenv 1.1.0
- pytz 2025.2
- simplekml 1.3.6
- pyinstaller 6.11.1
- pylint 3.3.7
- boto3 1.38.27
  
The requirements.txt file is found in:
```txt
src/requirements.txt
```

Install dependencies in the project folder with:
```sh
pip install -r src/requirements.txt
```

## Installation

Either clone the repository:
```sh
git clone https://github.com/Leffell-Space/live_data_analysis
```
Or access the pre-built releases for each operating system: [Latest Release](https://github.com/Leffell-Space/live_data_analysis/releases/latest)
#### Then remember to install the requirements (see above)

## Usage

### 1a. Configure Your Digital Ocean Spaces Bucket 

Go to digital ocean and make a new spaces object. There should be two files in it: tracker.kml and tracker_link.kml. Set the space listing to public and get your access keys that will be needed in the next step when configuring your .env.

### 1b. Set Up Your .env File

In order for the for the python script to run properly the environment file must be set up. Download the [.env.example](https://github.com/Leffell-Space/live_data_analysis/blob/main/src/.env.example) and change all of the values in it to your own values. Also, remember to remove the .example file suffix from the filename. 

### 2. Begin Transmission Over Port 8001 (KISS Protocol)

There are two main options to do so:
#### A. Connect to HDSDR or another SDR software in order to receive radio packets from a radio
In order for this method to work, you must have an RTL-SDR adapter plugged into the USB port of your computer. You should tune the antenna to receive on or around 144.39 Hz. Additionally, you should make sure that the application (HDSDR or whatever else you are using) is configured to act as a virtual audio input and then set that input in the direwolf.conf file that should be in your direwolf folder. For more information about that please see: [wb2osz/direwolf](https://github.com/wb2osz/direwolf)

#### B. Run Direwolf Using an Audio File
Again make sure Direwolf is properly installed on your computer! The audio file you are running should contain APRS packet data and not data from another frequency, as direwolf was specifically for APRS. In the directory where your audio file is run:
```sh
direwolf - < your_audio_file.wav
```
Note that the audio file must be in .wav and must be mono output. Also, Direwolf will begin transmitting rapidly over 8001 from an audio file; therefore, if you are using the Direwolf script with this you must complete the next step in very quick succession after running this command. The testing audio I used is from [wa8lmf.net](http://www.wa8lmf.net/TNCtest/) and you can find the download for the specific one here in [my personal drive](https://drive.google.com/file/d/1D4iSMrX_BVh4LJDBBV9oVMFSp4jXLrLQ/view?usp=sharing). I would suggest using this one because there is a whole process to get the file in mono output but if you really want to there are other tests at the link above.

### 2. Get Data from Direwolf Using the Python Script

Make sure Direwolf is running and listening on port 8001. Then run:
```sh
python3 src/get_from_direwolf.py
```
This will decode incoming APRS packets, print positions, and update `tracker.kml` and `tracker_link.kml` for Google Earth. **Note that this command must be run in a different terminal than the command that starts up the server.**

### 3. Open tracker_link.kml in Google Earth

Download tracker_link.kml from your Digital Ocean Spaces page. You must have Google Earth Pro (not paid just the desktop version) in order to get live updates. Download it here: [Google Earth Pro](https://www.google.com/earth/about/versions/). Then in Google Earth Pro go to file → open → and then your tracker_link.kml. You should see all of the pins that are meant to be there, marked by their EST received date and time. This means it will mark it by the time/date that it receives the data not the timestamp of the data found within the APRS packet. 

## License

See LICENSE
