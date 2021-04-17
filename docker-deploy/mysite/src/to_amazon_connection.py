from .base_connect import MySocket
import world_ups_pb2
import amazon_ups_pb2
from ups.models import Truck, Package
import threading

class Amazon(Base):
    