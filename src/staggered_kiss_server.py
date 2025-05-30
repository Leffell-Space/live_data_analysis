import socket
import time

def extract_kiss_frames(data):
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

def main():
    with open("test.txt", "rb") as f:
        data = f.read()
    frames = extract_kiss_frames(data)

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind(("localhost", 8001))
    server_sock.listen(1)
    print("Staggered KISS server listening on localhost:8001")

    client_sock, addr = server_sock.accept()
    print(f"Client connected from {addr}")

    try:
        for frame in frames:
            client_sock.sendall(frame)
            print("Sent one frame, waiting 5 seconds...")
            time.sleep(5)
    finally:
        client_sock.close()
        server_sock.close()
        print("Server closed.")

if __name__ == "__main__":
    main()