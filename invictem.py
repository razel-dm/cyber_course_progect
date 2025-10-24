import socket
import json
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9323
RETRY_DELAY = 2


class JsonSocket:
    """Line-delimited JSON over a socket using a file-like wrapper."""

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._fp = sock.makefile("rwb")

    def send(self, obj: dict) -> None:
        self._fp.write((json.dumps(obj) + "\n").encode("utf-8"))
        self._fp.flush()

    def recv(self) -> dict:
        line = self._fp.readline()
        if not line:
            raise ConnectionError("peer closed connection")
        return json.loads(line.decode("utf-8"))

    def close(self) -> None:
        try:
            self._fp.close()
        finally:
            self._sock.close()


class SimpleExecutor:
    """Minimal placeholder: acknowledges any command."""

    def run(self, command: str) -> dict:
        return {"status": "Ok", "echo": command}


class AgentClient:
    def __init__(self, host: str, port: int, retry_delay: float = 1.0):
        self.host = host
        self.port = port
        self.retry_delay = retry_delay
        self.executor = SimpleExecutor()

    def _connect_with_retry(self) -> JsonSocket:
        while True:
            try:
                sock = socket.create_connection(
                    (self.host, self.port), timeout=5)
                sock.settimeout(None)
                print("[agent] connected to server.")
                return JsonSocket(sock)
            except OSError:
                print("[agent] server unavailable, retrying ...")
                time.sleep(self.retry_delay)

    def run(self) -> None:
        jsock = self._connect_with_retry()
        try:
            while True:
                try:
                    incoming = jsock.recv()
                except ConnectionError:
                    print("[agent] server disconnected.")
                    break

                if incoming.get("type") == "command":
                    cmd = incoming.get("data", "")
                    if cmd.lower() == "exit":
                        print("[agent] received exit. closing.")
                        break
                    result = self.executor.run(cmd)
                    jsock.send({"type": "result", **result})
        finally:
            jsock.close()


if __name__ == "__main__":
    AgentClient(SERVER_HOST, SERVER_PORT, RETRY_DELAY).run()