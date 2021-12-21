import socket
import threading
import argparse


def main(ip: str, port: int):
    ip = ip or "0.0.0.0"
    port = port or 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((ip, port))
    server.listen(5)
    print(f"[*] Listening on {ip}:{port}")

    while True:
        client, address = server.accept()
        print(f"[*] Accepted connection from {address[0]}:{address[1]}")
        client_handler = threading.Thread(target=handle_client, args=(client,))
        client_handler.start()


def handle_client(client_socket):
    with client_socket as sock:
        request = sock.recv(1024)
        print(f'[*] Received: {request.decode("utf-8")}')
        sock.send(b"ACKKK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Receive data using TCP.",
        epilog="Example usage: python tcp_server.py --ip 0.0.0.0 --port 9999",
    )
    parser.add_argument("--ip", type=str, help="the bind IP")
    parser.add_argument("--port", type=int, help="the bind port")
    args = parser.parse_args()
    main(args.ip, args.port)
