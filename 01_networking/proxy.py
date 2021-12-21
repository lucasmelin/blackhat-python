import sys
import socket
import argparse
import threading


def proxy_handler(
    client_socket: socket.socket,
    remote_host: str,
    remote_port: int,
    receive_first: bool,
) -> None:
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
    loop = True
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
        remote_buffer = response_handler(remote_buffer)
        if remote_buffer:
            print(f"[<==] Sending {len(remote_buffer)} bytes to localhost.")

            client_socket.send(remote_buffer)
    while loop:
        local_buffer = receive_from(client_socket)
        if local_buffer:
            print(f"[==>] Received {len(local_buffer)} bytes from localhost.")
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print(f"[==>] Sent to remote.")
        remote_buffer = receive_from(remote_socket)
        if remote_buffer:
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)

            print(f"[<==] Sent to localhost.")

        if not local_buffer or not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print(f"[*] No more data. Closing connections.")
            loop = False
            break


def hexdump(src, length=16) -> None:
    result = []
    digits = 4 if isinstance(src, str) else 2
    for i in range(0, len(src), length):
        s = src[i : i + length]
        hexa = b" ".join(["%0*X" % (digits, ord(x)) for x in s])
        text = b"".join([x if 0x20 <= ord(x) < 0x7F else b"." for x in s])
        result.append(b"%04X %-*s %s" % (i, length * (digits + 1), hexa, text))
    print(b"\n".join(result))


def receive_from(connection: socket.socket) -> bytes:
    buffer = b""
    connection.settimeout(2)
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer


def request_handler(buffer: bytes) -> bytes:
    # Here we can modify the packets before forwarding them
    return buffer


def response_handler(buffer: bytes) -> bytes:
    # Here we can modify the packets before forwarding them
    return buffer


def server_loop(
    localhost: str,
    localport: int,
    remotehost: str,
    remoteport: int,
    receive_first: bool,
):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((localhost, localport))
    except:
        print(f"[!!] Failed to listen on {localhost}:{localport}")
        print(f"[!!] Check for other listening sockets or correct permissions.")
        sys.exit(0)
    print(f"[*] Listening on {localhost}:{localport}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        print(f"[==>] Received incoming connection from {addr[0]}:{addr[1]}")
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remotehost, remoteport, receive_first),
        )
        proxy_thread.start()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simple TCP proxy.",
    )
    parser.add_argument("--localhost", type=str, help="the local")
    parser.add_argument("--localport", type=int, help="the local port")
    parser.add_argument("--remotehost", type=str, help="the remote host")
    parser.add_argument("--remoteport", type=int, help="the remote port")
    parser.add_argument("-f", "--first", help="receive first", action="store_true")

    args = parser.parse_args()
    server_loop(
        args.localhost, args.localport, args.remotehost, args.remoteport, args.first
    )
