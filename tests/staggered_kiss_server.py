import socket
import time

# List of hex strings (copy from your dump, one per frame)
hex_frames = [
    # USING PACKETS FROM KN6DB-14 for testing
    "c0008ea0a698964060969c6c8884407c9c6c8ab04040e903f0244750524d432c3032313835312c412c333334382e383437302c4e2c31313830302e313638352c572c3030302e302c3237342e302c3233313130352c3031332e342c452a36440d0ac0",
    "c0008ea0a698964060969c6c8884407c9c6c8ab04040e303f0244750524d432c3032303635312c412c333334382e383437342c4e2c31313830302e313638392c572c3030302e302c3237342e302c3233313130352c3031332e342c452a36410d0ac0",
    "c0008ea0a698964060969c6c8884407c9c6c8ab04040e303f0244750524d432c3032303635312c412c333334382e383437342c4e2c31313830302e313638392c572c3030302e302c3237342e302c3233313130352c3031332e342c452a36410d0ac0",
    "c0008ea0a698964060969c6c8884407c9c6c8ab04040e303f0244750524d432c3032303635312c412c333334382e383437342c4e2c31313830302e313638392c572c3030302e302c3237342e302c3233313130352c3031332e342c452a36410d0ac0",
    "c0008ea0a698964060969c6c8884407c9c6c8ab04040e303f0244750524d432c3032303635312c412c333334382e383437342c4e2c31313830302e313638392c572c3030302e302c3237342e302c3233313130352c3031332e342c452a36410d0ac0"
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
