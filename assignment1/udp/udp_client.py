import socket
import random
import json
import os
import sys

UDP_IP = '127.0.0.1'
UDP_PORT = 4000
BUFFER_SIZE = 1024
MESSAGE = "ping"

def send_to_server(s, json_obj):
    s.sendto(convertDictToBinary(json_obj), (UDP_IP, UDP_PORT))
    return s

def convertDictToBinary(dict):
    return json.dumps(dict).encode('utf-8')

def receive_from_server(s):
    data, ip = s.recvfrom(BUFFER_SIZE)
    return data.decode(), ip

def three_way_handshake():
    x = random.randint(0, 999999)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s = send_to_server(s, {"x": x})
    ret_data, ip = receive_from_server(s)
    y = None
    json_obj = json.loads(ret_data)
    if x + 1 == json_obj["x"]:
        y = json_obj["y"]
    else:
        print("error in three way handshake")
        pass
    new_y = y + 1

    s = send_to_server(s, {"y": new_y})
    #Begin data transfer
    return x, y, s

def transfer_data(x, y, s):
    file_name = "./upload.txt"
    file_data = read_file(file_name)
    handle_transfer(s, x, y, file_data)

def handle_transfer(s, x, y, file_data):
    new_seq = x
    s.settimeout(4)
    for line in file_data:
        new_seq = new_seq + len(line.encode("utf8"))
        count = 0
        while count < 5:
            try:
                ack = send_receive_data(s, new_seq, line, x)
                print("Received ack(" + str(ack) + ") from the server.")
                break
            except Exception as e:
                count += 1
    handle_fin(s, new_seq, y)

def handle_fin(s, x, y):
    fin = random.randint(0, 999999)
    send_to_server(s, {"fin": x})
    ret_data = receive_from_server(s)
    ack = json.loads(ret_data[0])["ack"]
    fin = json.loads(ret_data[0])["fin"]
    if (x + 1) != ack:
        print("fin error")
    else:
        send_to_server(s, {"ack": fin + 1})
    print("File upload successfully completed.")

def send_receive_data(s, new_seq, line, x):
    send_to_server(s, {"line": line, "seq": new_seq})
    ret_data = receive_from_server(s)
    ack = json.loads(ret_data[0])["ack"]
    return ack

def read_file(file_name):
    file_contents = None
    file_path = os.path.join(sys.path[0], file_name)
    with open(file_path, "r") as f:
        file_contents = f.readlines()
    return file_contents

def send(id=0):
    try:
        x, y, s = three_way_handshake()
        print("Connected to the server.")
        print("Starting a file (upload.txt) upload...")
        transfer_data(x, y, s)
    except socket.error:
        print("Error! {}".format(socket.error))
        exit()

send()