'''Simulates APRS data that will be recieved using direworlf.'''
import socket
import time

def extract_kiss_frames(data):
    '''Extract KISS frames from raw data.'''
    frames = []
    start = 0
    while True:
        start = data.find(b'\xC0', start)
        if start == -1:
            break
        end = data.find(b'\xC0', start + 1)
        if end == -1:
            break
        frame = data[start:end+1]
        frames.append(frame)
        start = end + 1
    return frames

def load_frames_from_file(filename):
    '''Load KISS frames from a file.'''
    with open(filename, "rb") as f:
        data = f.read()
    return extract_kiss_frames(data)

def run_server(frames, host="localhost", port=8001, delay=5):
    '''Run a TCP server that sends KISS frames with a delay.'''
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    print(f"Staggered KISS server listening on {host}:{port}")

    client_sock, addr = server_sock.accept()
    print(f"Client connected from {addr}")

    try:
        for frame in frames:
            client_sock.sendall(frame)
            print(f"Sent one frame, waiting {delay} seconds...")
            time.sleep(delay)
        return True
    except Exception as e: # pylint: disable=broad-except
        print(f"Error in server: {e}")
        return False
    finally:
        client_sock.close()
        server_sock.close()
        print("Server closed.")

def main():
    '''Main function to run the staggered KISS server.'''
    frames = load_frames_from_file("test.txt")
    run_server(frames)

if __name__ == "__main__":
    main()
