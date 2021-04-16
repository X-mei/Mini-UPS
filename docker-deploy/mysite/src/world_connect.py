import world_ups_pb2
import amazon_ups_pb2
import sys
import socket
import threading
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint32
import time
from .common import *

# Local host address and port used to connect to world
server_host = "vcm-18172.vm.duke.edu"
server_port = "12345"
# Init the socket object
AllSocket = MySocket()
# Connect to world
AllSocket.make_connection(server_host, server_port)
# Init connect message and create truck
connect = world_ups_pb2.UConnect
connect.isAmazon = False
truck1 = connect.trucks.add()
truck1.id = 1
truck1.x = 5
truck1.y = 5
truck2 = connect.trucks.add()
truck2.id = 2
truck2.x = 10
truck2.y = 10
# Send the message to world to get world id
send_data(AllSocket.world_socket, connect)
# Init connected message and recieve it from world
connected = world_ups_pb2.UConnected
recv_data(AllSocket.world_socket, connected)
print(connected.worldid)
print(connected.result)

# Setup server and wait for amazon to connect
AllSocket.server_setup(8888)
# Accept request from amazon
while True:
    AllSocket.accept_request()





