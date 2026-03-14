import socket

HOST = "127.0.0.1"
PORT = 3333
BUFFER_SIZE = 1024


def receive_full_message(sock):
    """Primeste un mesaj length-prefixed de la server."""
    try:
        data = sock.recv(BUFFER_SIZE)
        if not data:
            return None

        string_data = data.decode("utf-8").strip()
        first_space = string_data.find(" ")

        if first_space == -1 or not string_data[:first_space].isdigit():
            return "ERROR: format invalid de raspuns de la server"

        message_length = int(string_data[:first_space])
        full_data = string_data[first_space + 1:]
        remaining = message_length - len(full_data)

        while remaining > 0:
            chunk = sock.recv(BUFFER_SIZE)
            if not chunk:
                return None
            full_data += chunk.decode("utf-8")
            remaining -= len(chunk)

        return full_data
    except Exception as e:
        return f"ERROR: {e}"


def print_help():
    print("""
Comenzi disponibile:
  ADD <cheie> <valoare>   - Adauga o inregistrare
  GET <cheie>             - Returneaza valoarea pentru cheie
  REMOVE <cheie>          - Sterge inregistrarea
  LIST                    - Afiseaza toate inregistrarile
  COUNT                   - Numarul total de inregistrari
  CLEAR                   - Sterge toate inregistrarile
  UPDATE <cheie> <val>    - Actualizeaza valoarea unei chei
  POP <cheie>             - Returneaza si sterge inregistrarea
  QUIT                    - Inchide conexiunea
  help                    - Afiseaza acest meniu
""")


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print(f"[CLIENT] Nu se poate conecta la server {HOST}:{PORT}. Asigura-te ca serverul ruleaza.")
            return

        print(f"[CLIENT] Conectat la {HOST}:{PORT}. Scrie 'help' pentru lista de comenzi.")

        while True:
            try:
                command = input("client> ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n[CLIENT] Iesire...")
                break

            if not command:
                continue

            if command.lower() == "help":
                print_help()
                continue

            # Trimite comanda la server
            s.sendall(command.encode("utf-8"))
            response = receive_full_message(s)

            if response is None:
                print("[CLIENT] Conexiunea a fost inchisa de server.")
                break

            print(f"Server> {response}")

            # Daca am trimis QUIT, inchidem si clientul
            if command.strip().upper() == "QUIT":
                break


if __name__ == "__main__":
    main()
