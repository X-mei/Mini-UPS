import socket
import io
import time
import threading
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.encoder import _EncodeVarint

class MySocket():
    def __init__(self, simspeed=100):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.simspeed = simspeed
        self.seq_num = 0
        self.seq_dict = dict()
        self.recv_msg = set()

        
    def setup_server(self, host, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('starting up on {} port {}'.format(host, port))
        self.sock.bind((host, port))
        self.sock.listen()


    def accept_connection(self):
        self.amazon_sock, self.amazon_address = self.sock.accept()
        print(self.amazon_address)


    def make_connection(self, host, port):
        print('connecting to {} port {}'.format(host, port))
        self.sock.connect((host, port))


    def encode_varint(self, value):
        """ Encode an int as a protobuf varint """
        data = []
        _EncodeVarint()(data.append, value, None)
        return b''.join(data)


    def decode_varint(self, data):
        """ Decode a protobuf varint to an int """
        return _DecodeVarint32(data, 0)[0]


    def recv_data_amazon(self, message):
        var_int_buff = []
        while True:
            buf = self.amazon_sock.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        whole_message = self.amazon_sock.recv(msg_len)
        # Decode the message
        message.ParseFromString(whole_message)
        ##return size


    def recv_data(self, message):
        var_int_buff = []
        while True:
            buf = self.sock.recv(1)
            var_int_buff += buf
            msg_len, new_pos = _DecodeVarint32(var_int_buff, 0)
            if new_pos != 0:
                break
        whole_message = self.sock.recv(msg_len)
        # Decode the message
        message.ParseFromString(whole_message)
        ##return size
        

    def send_data(self, message):
        data = message.SerializeToString()
        _EncodeVarint(self.sock.send, len(data), None)
        self.sock.send(data)  


    def send_data_amazon(self, message):
        data = message.SerializeToString()
        _EncodeVarint(self.amazon_sock.send, len(data), None)
        self.amazon_sock.send(data)


    def resend_data(self):
        while True:
            time.sleep(500)
            for k in self.seq_dict:
                self.send_data(self.seq_dict[k])

    def resend_data_amazon(self):
        while True:
            time.sleep(500)
            for k in self.seq_dict:
                self.send_data_amazon(self.seq_dict[k])


    def __del__(self):
        print("Closing connection from...")
        self.sock.close()