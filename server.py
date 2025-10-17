import socket
import json
import time

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 9323
RETRY_DELAY = 2


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
