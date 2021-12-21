import sys
import socket
import argparse
import threading
import subprocess


def client_sender(buffer, target, port: int) -> None:
    """Send data to a target."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if buffer:
            client.send(buffer)
        while True:
            recv_len = 1
            response = b""
            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response.decode())
            buffer = input("").encode()
            buffer += b"\n"

            client.send(buffer)
    except:
        print("[*] Exception! Exiting.")
        client.close()


def server_loop(target, port, upload, execute, command) -> None:
    """Listen for incoming connections on a distinct thread."""
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))
    server.listen(5)

    while True:
        client, addr = server.accept()
        print(f"[*] Accepted connection from: {addr[0]}:{addr[1]}")
        client_thread = threading.Thread(
            target=client_handler, args=(client, upload, execute, command)
        )
        client_thread.start()


def run_command(command) -> bytes:
    """Run a command and return the output."""
    command = command.decode().rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = b"Failed to execute command.\r\n"
    return output


def client_handler(client_socket, upload, execute, command) -> None:
    """Handle client requests."""
    if upload:
        file_buffer = b""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data
        try:
            file_descriptor = open(upload, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()

            client_socket.send(f"Successfully saved file to {upload}".encode())
        except:
            client_socket.send(f"Failed to save file to {upload}".encode())

    if execute:
        output = run_command(execute)
        client_socket.send(output)
    if command:
        while True:
            client_socket.send(b"<BHP:#> ")
            cmd_buffer = b""
            while b"\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)
            response = run_command(cmd_buffer)
            client_socket.send(response)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BHP Net Tool",
        epilog="Example usage: python simple_netcat.py -t 192.168.0.1 -p 5555 -l -c",
    )
    parser.add_argument("-t", "--target", default="0.0.0.0", help="Target IP address")
    parser.add_argument("-p", "--port", default=0, help="Target port", type=int)
    parser.add_argument(
        "-l",
        "--listen",
        help="Listen on [host]:[port] for incoming connections",
        action="store_true",
    )
    parser.add_argument(
        "-e", "--execute", help="Execute the given file upon receiving a connection"
    )
    parser.add_argument(
        "-c", "--command", help="Initialize a command shell", action="store_true"
    )
    parser.add_argument(
        "-u",
        "--upload",
        help="Upload a file and write to [destination]",
        metavar="destination",
    )
    args = parser.parse_args()

    if not args.listen and args.target and args.port:
        buffer = sys.stdin.read()
        client_sender(buffer, args.target, args.port)
    if args.listen:
        server_loop(args.target, args.port, args.upload, args.execute, args.command)
