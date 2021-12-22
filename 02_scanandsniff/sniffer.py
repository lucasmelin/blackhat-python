import socket
import os


def windows_sniffer(host):
    # Sniff all packets, regardless of protocol
    socket_protocol = socket.IPPROTO_IP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))

    # Include the IP headers in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # Send an IOCTL to set up promiscuous mode on Windows
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)

    # Read in a single packet
    print(sniffer.recvfrom(65565))

    # Turn off promiscuous mode on Windows
    sniffer.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)


def linux_sniffer(host):
    # Sniff only ICMP packets
    socket_protocol = socket.IPPROTO_ICMP

    sniffer = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket_protocol)
    sniffer.bind((host, 0))

    # Include the IP headers in the capture
    sniffer.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    # Read in a single packet
    print(sniffer.recvfrom(65565))


def main(host):
    if os.name == "nt":
        windows_sniffer(host)
    else:
        linux_sniffer(host)


if __name__ == "__main__":
    HOST = "127.0.0.1"
    main(HOST)
