import socket
import io
import time
import threading
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.encoder import _EncodeVarint

class MySocket():
    def __init__(self, simspeed=100):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.simspeed = simspeed
        self.seq_num = 0
        self.seq_dict = dict()
        self.recv_msg = set()
        # Resend mechanism
        th_resend = threading.Thread(target=self.resend, args=())
        th_resend.setDaemon(True)
        th_resend.start()

        
    def setup_server(self, host, port):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('starting up on {} port {}'.format(host, port))
        self.socket.bind((host, port))
        self.socket.listen(1)


    def make_connection(self, host, port):
        print('starting up on {} port {}'.format(host, port))
        self.socket.connect((host, port))


    def encode_varint(self, value):
        """ Encode an int as a protobuf varint """
        data = []
        _VarintEncoder()(data.append, value, None)
        return b''.join(data)


    def decode_varint(self, data):
        """ Decode a protobuf varint to an int """
        return _DecodeVarint32(data, 0)[0]


    def recv_data(self, message):
        data = b''
        while True:
            try:
                data += socket.recv(1)
                size = decode_varint(data)
                break
            except IndexError:
                pass
        # Receive the message data
        data = socket.recv(size)
        # Decode the message
        message.ParseFromString(data)
        ##return size
        

    def send_data(self, message):
        data=message.SerializeToString()
        size = encode_varint(len(data))
        socket.sendall(size+data)  


    def resend_data(self):
        while True:
            time.sleep(1)
            for k in self.seq_dict:
                self.send_data(self.seq_dict[k])


    def __del__(self):
        print("Closing connection...")
        self.socket.close()