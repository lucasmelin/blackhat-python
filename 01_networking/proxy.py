import sys
import socket
import threading

HEX_FILTER = "".join([(len(repr(chr(i))) == 3) and chr(i) or "." for i in range(256)])


def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()
    results = list()
    for i in range(0, len(src), length):
        word = str(src[i : i + length])
        printable = word.translate(HEX_FILTER)
        hexa = " ".join([f"{ord(c):02X}" for c in word])
        hexwidth = length * 3
        results.append(f"{i:04x}  {hexa:<{hexwidth}}  {printable}")
    if show:
        for line in results:
            print(line)
    else:
        return results


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
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)

    while loop:
        local_buffer = receive_from(client_socket)
        if local_buffer:
            print(f"[<==] Received {len(local_buffer)} bytes from local.")
            hexdump(local_buffer)

            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Sent to remote.")

        remote_buffer = receive_from(remote_socket)
        if remote_buffer:
            print(f"[<==] Received {len(remote_buffer)} bytes from remote.")
            hexdump(remote_buffer)

            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)

            print("[==>] Sent to local.")

        if not local_buffer or not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print("[*] No more data. Closing connections.")
            loop = False
            break


def receive_from(connection: socket.socket) -> bytes:
    buffer = b""
    connection.settimeout(10)
    while True:
        data = connection.recv(4096)
        if not data:
            break
        buffer += data
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
    except Exception as e:
        print(f"[!!] Failed to listen on {localhost}:{localport}")
        print(f"[!!] Check for other listening sockets or correct permissions.")
        raise e

    print(f"[*] Listening on {localhost}:{localport}")
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        print(f"[>] Received incoming connection from {addr[0]}:{addr[1]}")
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remotehost, remoteport, receive_first),
        )
        proxy_thread.start()


if __name__ == "__main__":
    if len(sys.argv[1:]) != 5:
        print("Usage: proxy.py [localhost] [localport]", end="")
        print("[remotehost] [remoteport] [receive_first]")
        print("Example: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
