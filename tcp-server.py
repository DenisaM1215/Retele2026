import socket
import threading

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


class State:
    def __init__(self):
        self.data = {}
        self.lock = threading.Lock()

    def add(self, key, value):
        with self.lock:
            self.data[key] = value
        return "OK - record add"

    def get(self, key):
        with self.lock:
            if key in self.data:
                return f"DATA {self.data[key]}"
            return "ERROR invalid key"

    def remove(self, key):
        with self.lock:
            if key in self.data:
                del self.data[key]
                return "OK value deleted"
            return "ERROR invalid key"

    def list_all(self):
        with self.lock:
            if not self.data:
                return "DATA|"
            entries = ",".join(f"{k}={v}" for k, v in self.data.items())
            return f"DATA|{entries}"

    def count(self):
        with self.lock:
            return f"DATA {len(self.data)}"

    def clear(self):
        with self.lock:
            self.data.clear()
        return "all data deleted"

    def update(self, key, value):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            self.data[key] = value
        return "Data updated"

    def pop(self, key):
        with self.lock:
            if key not in self.data:
                return "ERROR invalid key"
            value = self.data.pop(key)
        return f"Data {value}"


state = State()


def process_command(command):
    parts = command.strip().split()
    if not parts:
        return "ERROR empty command"

    cmd = parts[0].upper()

    if cmd == "ADD":
        if len(parts) < 3:
            return "ERROR usage: ADD <key> <value>"
        key, value = parts[1], " ".join(parts[2:])
        return state.add(key, value)

    elif cmd == "GET":
        if len(parts) != 2:
            return "ERROR usage: GET <key>"
        return state.get(parts[1])

    elif cmd == "REMOVE":
        if len(parts) != 2:
            return "ERROR usage: REMOVE <key>"
        return state.remove(parts[1])

    elif cmd == "LIST":
        return state.list_all()

    elif cmd == "COUNT":
        return state.count()

    elif cmd == "CLEAR":
        return state.clear()

    elif cmd == "UPDATE":
        if len(parts) < 3:
            return "ERROR usage: UPDATE <key> <new_value>"
        key, value = parts[1], " ".join(parts[2:])
        return state.update(key, value)

    elif cmd == "POP":
        if len(parts) != 2:
            return "ERROR usage: POP <key>"
        return state.pop(parts[1])

    elif cmd == "QUIT":
        return "QUIT"

    else:
        return f"ERROR unknown command: {parts[0]}"


def handle_client(client_socket, addr):
    print(f"[SERVER] Client conectat: {addr}")
    with client_socket:
        while True:
            try:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                command = data.decode("utf-8").strip()
                print(f"[SERVER] Comanda primita de la {addr}: {command}")

                response = process_command(command)

                if response == "QUIT":
                    farewell = "La revedere!"
                    client_socket.sendall(
                        f"{len(farewell)} {farewell}".encode("utf-8")
                    )
                    print(f"[SERVER] Client {addr} a trimis QUIT. Conexiune inchisa.")
                    break

                response_data = f"{len(response)} {response}".encode("utf-8")
                client_socket.sendall(response_data)

            except Exception as e:
                error_msg = f"ERROR {str(e)}"
                client_socket.sendall(
                    f"{len(error_msg)} {error_msg}".encode("utf-8")
                )
                break

    print(f"[SERVER] Conexiune inchisa: {addr}")


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))
        server_socket.listen()
        print(f"[SERVER] Asculta pe {HOST}:{PORT}")
        print("[SERVER] Comenzi disponibile: ADD, GET, REMOVE, LIST, COUNT, CLEAR, UPDATE, POP, QUIT")

        while True:
            client_socket, addr = server_socket.accept()
            threading.Thread(
                target=handle_client, args=(client_socket, addr), daemon=True
            ).start()


if __name__ == "__main__":
    start_server()
