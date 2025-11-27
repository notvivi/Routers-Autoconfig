# Autor: Vilma Tomanová
# Datum: 2025-25-11
# Popis: Script pro posílání příkazů na routery pomocí vláken.

import threading
import paramiko
import time
import json
import logging



class LinuxVps:
    def __init__(self, host,port, user, status):
        self.host = host
        self.port = port
        self.user = user
        self.status = status


lock = threading.Lock()
json_file = "../res/linuxvps.json"

def update_status(port, new_status):
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
    threads = []

    start = time.time()
    for linuxvps in linuxvpss:
        t = threading.Thread(target=configure_linux, args=(linuxvps,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    end = time.time()
    print("Vypocet trval {:.6f} sec.".format((end - start)))


def configure_linux(linuxvps):

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(hostname=linuxvps.host, port=linuxvps.port, username=linuxvps.user, password="jooouda")

            remote = ssh.invoke_shell()
            time.sleep(1)

            commands = ["uptime","date"]

            for cmd in commands:
                remote.send(cmd + "\n")
                time.sleep(1)
            update_status(linuxvps.port, "done")

            remote.close()
            ssh.close()

        except Exception as e:
            print(f"Failed to connect to {linuxvps.port}: {e}")
            update_status(linuxvps.port, "error")
            logging.error(f"Failed to connect to {linuxvps.port}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.ERROR, filename='../log/logfile.log', filemode='w',
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    with open(json_file) as f:
        jsondata = json.load(f)
        linuxvpss = [LinuxVps(linuxvps["host"], linuxvps["port"], linuxvps["user"], linuxvps["status"]) for linuxvps in jsondata["servers"]]
    main_loop(linuxvpss)