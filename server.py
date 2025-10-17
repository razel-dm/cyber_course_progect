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

    