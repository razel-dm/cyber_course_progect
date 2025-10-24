import socket
import json
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9323
RETRY_DELAY = 2
MENU_TEXT = """Available commands:
1. echo <message> - Echoes the message back.
2. screenshot - Takes a screenshot of the agent's screen.
3. rickroll - Plays the Rick Astley video.
4. exit - Closes the connection and exits.
"""


class JsonSocket:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = None
        self.connect()
    def connect(self):
        while True:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.host, self.port))
                print(f"Connected to server at {self.host}:{self.port}")
                break
            except ConnectionRefusedError:
                print(f"no connection, retrying in {RETRY_DELAY} ")
                time.sleep(RETRY_DELAY)

    def send_json(self, data):
        message = json.dumps(data).encode('utf-8')
        self.sock.sendall(message)

    def receive_json(self):
        received_data = self.sock.recv(4096)
        return json.loads(received_data.decode('utf-8'))

    def close(self):
        if self.sock:
            self.sock.close()
            print("Connection closed.")
class C2Server:
    def __init__(self, host: str, port: int, menu: str):
        self.host = host
        self.port = port
        self.menu = menu
        self._lsock: socket.socket | None = None

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

                    jsock.send({"type": "command", "data": cmd})

                    if cmd.lower() == "exit":
                        print("[server] closing session.")
                        break

                    try:
                        reply = jsock.recv()
                    except ConnectionError:
                        print("[server] agent disconnected.")
                        break

                    print(f"[server] agent replied: {reply}")
            finally:
                jsock.close()
        finally:
            if self._lsock:
                self._lsock.close()


if __name__ == "__main__":
    C2Server(SERVER_HOST, SERVER_PORT, MENU_TEXT).run()