import socket
import random
import json

UDP_IP = '127.0.0.1'
UDP_PORT = 4000
BUFFER_SIZE = 1024
MESSAGE = "pong"

def receive_from_client(s):
    data, ip = s.recvfrom(BUFFER_SIZE)
    return data, ip

def convertDictToBinary(dict):
    return json.dumps(dict).encode('utf-8')

def send_to_client(s, json_obj, ip):
    s.sendto(convertDictToBinary(json_obj), ip)
    return

def three_way_handshake(s):
    y = random.randint(0, 999999)
    data, ip = receive_from_client(s)
    print("Accepting a file upload...")
    data_json = json.loads(data)
    x = data_json["x"]
    new_x = x + 1
    send_to_client(s, {"x": new_x, "y": y}, ip)
    #begin data transfer
    data, ip = receive_from_client(s)
    data_json = json.loads(data)
    new_y = data_json["y"]
    handle_transfer(s, ip, new_x, new_y)

def handle_transfer(s, ip, x, y):
    lines = ""
    data = None
    while True:
        data = receive_from_client(s)
        if "fin" in json.loads(data[0]):
            break
        seq = json.loads(data[0])["seq"]
        lines = lines + json.loads(data[0])["line"]
        line_length = len(json.loads(data[0])["line"].encode("utf8"))
        ack = seq + line_length
        send_to_client(s, {"ack": ack}, ip)

    fin = json.loads(data[0])["fin"]
    ack = fin + 1
    send_to_client(s, {"fin": y + 1, "ack": ack}, ip)
    data = receive_from_client(s)
    new_ack = json.loads(data[0])["ack"]
    print("Lines: ")
    print(lines)
    print("Upload successfully completed.")

def listen_forever():
    print("Server started at port " + str(UDP_PORT) + ".")
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(("", UDP_PORT))
        three_way_handshake(s)

listen_forever()