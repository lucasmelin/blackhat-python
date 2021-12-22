import os


def run(**args):
    """Retrieves any directories on the remote system."""
    print("[*] In dirlister module.")
    files = os.listdir(".")
    return str(files)
