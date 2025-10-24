

import socket
import json
import time
from typing import Optional

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9323
RETRY_DELAY = 2.0

MENU_TEXT = """Available commands:
1. echo <message> - Echoes the message back.
2. screenshot - Asks agent for a screenshot (base64 PNG returned).
3. rickroll - Opens Rick Astley video on the agent side (if GUI).
4. exit - Closes the session and stops the agent.
"""


class JsonSocket:
    """Line-delimited JSON over a socket using a text file wrapper."""

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


class C2Server:
    def __init__(self, host: str, port: int, menu: str):
        self.host = host
        self.port = port
        self.menu = menu
        self._lsock: Optional[socket.socket] = None

    def _listen(self) -> None:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((self.host, self.port))
        s.listen(1)
        self._lsock = s
        print(f"[server] listening on {self.host}:{self.port}")

    def _accept(self) -> JsonSocket:
        assert self._lsock is not None
        conn, addr = self._lsock.accept()
        print(f"[server] client connected from {addr}")
        return JsonSocket(conn)

    def run(self) -> None:
        try:
            self._listen()
            jsock = self._accept()
            print(self.menu)
            try:
                while True:
                    try:
                        cmd = input("server> ").strip()
                    except (EOFError, KeyboardInterrupt):
                        cmd = "exit"

                    if not cmd:
                        continue

                    jsock.send({"type": "command", "data": cmd})

                    if cmd.lower() == "exit":
                        print("[server] sent exit to agent, closing.")
                        break

    
                    try:
                        reply = jsock.recv()
                    except ConnectionError:
                        print("[server] agent disconnected.")
                        break
                    except json.JSONDecodeError:
                        print("[server] received invalid JSON from agent.")
                        continue

                   
                    if isinstance(reply, dict) and reply.get("type") == "result":
                        if "screenshot_b64" in reply:
                            b64 = reply["screenshot_b64"]
                            print("[server] received screenshot (base64 length {})".format(len(b64)))
                         
                            save = input("Save screenshot to file? (y/N) ").strip().lower()
                            if save == "y":
                                fname = input("Filename (e.g. out.png): ").strip() or "screenshot.png"
                                try:
                                    import base64
                                    with open(fname, "wb") as f:
                                        f.write(base64.b64decode(b64))
                                    print(f"[server] screenshot saved to {fname}")
                                except Exception as e:
                                    print("[server] failed to save screenshot:", e)
                        else:
                            print("[server] agent replied:", reply)
                    else:
                        print("[server] agent replied:", reply)
            finally:
                jsock.close()
        finally:
            if self._lsock:
                self._lsock.close()


if __name__ == "__main__":
    C2Server(SERVER_HOST, SERVER_PORT, MENU_TEXT).run()
