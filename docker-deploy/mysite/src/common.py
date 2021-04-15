import world_ups_pb2
import amazon_ups_pb2
import sys
import socket
import threading
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint32
import time

def encode_varint(value):
    """ Encode an int as a protobuf varint """
    data = []
    _VarintEncoder()(data.append, value, None)
    return b''.join(data)

def decode_varint(data):
    """ Decode a protobuf varint to an int """
    return _DecodeVarint32(data, 0)[0]

def send_data(socket_fd, message):
        print('Sending data...')
        data=message.SerializeToString()
        size = encode_varint(len(data))
        socket_fd.sendall(size+data)
    
def recv_data(socket_fd, message):
    print('Recieving data...')
    data = b''
    while True:
        try:
            data += socket_fd.recv(1)
            size = decode_varint(data)    
            break
        except IndexError:
            pass
    # Receive the message data
    data = socket_fd.recv(size)
    # Decode the message
    message.ParseFromString(data)

class MySocket:
    def __init__(self):
        self.world_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def make_connection(self, host, port):
        print('Connecting to {} on port {}...'.format(host, port))
        self.world_socket.connect((host, port))

    def server_setup(self, port):
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        host = socket.gethostname()
        print('Starting server on {} on port {}...'.format(host, port))
        self.server_socket.bind((host, port))
        self.server_socket.listen()
    
    def accept_request(self):
        print("Waiting connections...")
        amazon_socket, client_address = self.server_socket.accept()
        trd = threading.Thread(target=process_request(world_socket, amazon_socket, client_address))
        trd.start()

    def close_connection(self):
        print('Closing connection...')
        self.world_socket.close()
        self.amazon_socket.close()
    