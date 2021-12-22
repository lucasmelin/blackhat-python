import os


def run(**args):
    """Retrieves any environment variables on the remote system."""
    print("[*] In environment module")
    return os.environ
