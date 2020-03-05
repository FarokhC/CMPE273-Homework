import socket
import sys
import time

TCP_IP = '127.0.0.1'
TCP_PORT = 5000
BUFFER_SIZE = 1024
MESSAGE = "ping"

def send(num_messages, delay, id=0):
    count = 0

    while count < int(num_messages):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        print("Sending data:" + MESSAGE)
        s.send(f"{id}:{MESSAGE}".encode())
        data = s.recv(BUFFER_SIZE)
        print("received data:", data.decode())
        time.sleep(int(delay))
        count += 1
        s.close()

def get_client_id():
    id = input("Enter client id:")
    return id

def main(argv):
    send(argv[2], argv[3], argv[1])

if __name__ == "__main__":
    main(sys.argv)