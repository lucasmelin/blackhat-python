import socket
import argparse


def main(host: str, port: int, raw_data: str):
    host = host or "www.google.com"
    port = port or 80
    raw_data = raw_data or f"GET / HTTP/1.2\r\nHost: {host}\r\n\r\n"

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))

    client.send(raw_data.encode())
    response = client.recv(4096)

    print(response.decode("utf-8"))
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send data using TCP.",
        epilog="Example usage: python tcp_client.py --host www.google.com --port 80",
    )
    parser.add_argument("--host", type=str, help="the host to connect to")
    parser.add_argument("--port", type=int, help="the port to connect to")
    parser.add_argument("--data", type=str, help="the data to send")
    args = parser.parse_args()
    main(args.host, args.port, args.data)
