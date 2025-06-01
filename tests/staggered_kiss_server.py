import socket
import time

# List of hex strings (copy from your dump, one per frame)
hex_frames = [
    # KN6DB-14 (to WIDE1-1, simple APRS position)
    "c082a0a4a6404060969c6c8884407cae92888a6240626103f021333334382e38344a2f31313731362e3931573e546573742031c0",
    "c0969c9a9088968a68aa9c6c968a88606103f021333334392e39394e2f31313731372e3931573e546573742032c0", 
    "c0969c9a9088968a68aa9c6c968a88606103f021333335302e35304e2f31313731382e3931573e546573742033c0",
    "c0969c9a9088968a68aa9c6c968a88606103f021333335312e31314e2f31313731392e3931573e546573742034c0",
    "c0969c9a9088968a68aa9c6c968a88606103f021333335322e32324e2f31313732302e3931573e546573742035c0",
    # NOCALL (to WIDE1-1, simple APRS position)
    "c09c9e86829898619e8c6c968a88606103f021333334382e38344e2f31313731362e3931573e546573742036c0",
    "c09c9e86829898619e8c6c968a88606103f021333334392e39394e2f31313731372e3931573e546573742037c0",
    "c09c9e86829898619e8c6c968a88606103f021333335032e35304e2f31313731382e3931573e546573742038c0",
    "c09c9e86829898619e8c6c968a88606103f021333335312e31314e2f31313731392e3931573e546573742039c0",
    "c09c9e86829898619e8c6c968a88606103f021333335322e32324e2f31313732302e3931573e54657374203130c0"
]

def main(host="localhost", port=8001, delay=2):
    frames = [bytes.fromhex(h) for h in hex_frames]
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(1)
    print(f"Server listening on {host}:{port}")
    client_sock, addr = server_sock.accept()
    print(f"Client connected from {addr}")
    try:
        for frame in frames:
            print(f"Sending: {frame.hex()}")
            client_sock.sendall(frame)
            time.sleep(delay)
    finally:
        client_sock.close()
        server_sock.close()
        print("Server closed.")

if __name__ == "__main__":
    main()
