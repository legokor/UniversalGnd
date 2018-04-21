import socket
import threading


def listen():
    while running:
        connection, address = sck.accept()
        print('client connected')
        thread = threading.Thread(target=digest_message, args=(connection,))
        thread.daemon = True
        thread.start()


def digest_message(conn):
    while running:
        digest = conn.recv(1)
        print(digest)
        if digest == b'o':
            print('sending')
            conn.send(bytes('test message', 'UTF-8'))


running = True

sck = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sck.bind(('0.0.0.0', 1360))
sck.listen(5)

t1 = threading.Thread(target=listen)
t1.daemon = True
t1.start()

while running:
    cmd = input('? ')
    if cmd == "exit":
        running = False
