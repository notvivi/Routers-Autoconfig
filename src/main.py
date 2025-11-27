# Author: Vilma Tomanová
# Date finished: 2025-27-11
# Description: Script for sending commands on linux with threads.
import hashlib
import threading
import paramiko
import time
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from lib.resource_path import resource_path


try:
    config_path = resource_path("config.json")
    with open(config_path, "r") as f:
        config = json.load(f)
except FileNotFoundError:
    print("Config file not found.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error decoding config file: {e}")
    exit(1)


json_file = config.get("json_file", "../res/linuxvps.json")
log_file = config.get("log_file", "../log/logfile.log")
raw_password = config.get("ssh_password", "heslo1213")
thread_count = config.get("threads", 20)
commands = config.get("commands", ["uptime", "date"])


class LinuxVps:
    """
    Model for the linux vps server.
    """
    def __init__(self, host,port, user, status, password_hash):
        self.host = host
        self.port = port
        self.user = user
        self.status = status
        self.password_hash = password_hash

lock = threading.Lock()

def update_status(port, new_status):
    """
    Updates the status of the linux vps server.
    :param port: Port of the linux vps server.
    :param new_status: New status of the linux vps server.
    :return: Nothing
    """
    with lock:
        with open(json_file, "r") as f:
            data = json.load(f)

        for server in data["servers"]:
            if server["port"] == port:
                server["status"] = new_status
                break

        with open(json_file, "w") as f:
            json.dump(data, f, indent=2)

def main_loop(linuxvpss):
    """
    Main loop for the linux vps server.
    :param linuxvpss: List of LinuxVps objects.
    :return: Nothing
    """
    start = time.time()

    if thread_count <= 0: print("Thread count is greater then or equal to 0")

    with ThreadPoolExecutor(max_workers=thread_count) as executor:
        executor.map(configure_linux, linuxvpss)
    end = time.time()
    print("Calculated for {:.6f} sec.".format((end - start)))


def sha256_password(password: str) -> str:
    """
    Hashes the password used for logging via ssh.
    :param password: Raw password as a string.
    :return: Hashed password as a string.
    """
    if(isinstance(password, str)):
        return hashlib.sha256(password.encode()).hexdigest()
    else: raise TypeError(f"Password {password} not supported")

def configure_linux(linuxvps):
    """
    Configures the linux vps server via ssh.
    :param linuxvps: Specific Linux vps server.
    :return: Nothing
    """
    hash_password = sha256_password(raw_password)

    if (not isinstance(raw_password, str)):
        raise TypeError(f"Password {raw_password} not supported")

    if (hash_password != linuxvps.password_hash):
        logging.error(f"Wrong password on {linuxvps.port}")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        ssh.connect(hostname=linuxvps.host, port=linuxvps.port, username=linuxvps.user, password=raw_password)

        remote = ssh.invoke_shell()
        time.sleep(1)

        for cmd in commands:
            remote.send(cmd + "\n")
            time.sleep(1)
        update_status(linuxvps.port, "done")

        remote.close()
        ssh.close()
    except Exception as e:
        update_status(linuxvps.port, "error")
        logging.error(f"Failed to connect to {linuxvps.port}: {e}")


if __name__ == "__main__":
    if isinstance(json_file, str) and isinstance(log_file, str):
        try:
            logging.basicConfig(level=logging.ERROR, filename=log_file, filemode='w',
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        except FileNotFoundError:
            print(f"Error: Log file not found: {log_file}")
        try:
            with open(json_file) as f:
                jsondata = json.load(f)
                linuxvpss = [LinuxVps(linuxvps["host"], linuxvps["port"], linuxvps["user"], linuxvps["status"], linuxvps["password_hash"]) for linuxvps in jsondata["servers"]]
                main_loop(linuxvpss)
        except FileNotFoundError:
            print(f"Error: JSON file not found: {json_file}")
            logging.error(f"JSON file not found: {json_file}")
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON file {json_file}: {e}")
            print(f"Error: JSON file is invalid: {json_file}")
        finally:
            input("Press Enter to exit...")
    else:
        print("Error: Couldnt find json file or log file")
