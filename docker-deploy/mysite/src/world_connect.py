import world_ups_pb2
import amazon_ups_pb2
import sys
import socket
import threading
from google.protobuf.internal.encoder import _VarintEncoder
from google.protobuf.internal.decoder import _DecodeVarint32
import time
from .common import *

server_host = "vcm-18172.vm.duke.edu"
server_port = "12345"



