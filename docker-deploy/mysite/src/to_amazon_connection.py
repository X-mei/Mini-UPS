#from base_connect import MySocket
from database import *
import amazon_ups_pb2
import world_ups_pb2
import threading
import google
import socket
import io
import time
import threading
import google
from google.protobuf.internal.decoder import _DecodeVarint32
from google.protobuf.internal.encoder import _VarintBytes
from google.protobuf.internal.encoder import _EncodeVarint

# from .base_connect import MySocket
# from . import amazon_ups_pb2
# from . import world_ups_pb2
# from ups.models import Truck, Package, Product, User
# from .database import Database
# import threading

class Amazon():
    def __init__(self, simspeed=10000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.simspeed = simspeed
        self.seq_num = 0
        self.seq_dict = dict()
        self.recv_msg = set()
        #self.file_handle = open('logfile.txt', mode='w')

        
    def setup_server(self, host, port):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        #self.file_handle.write('starting up on {} port {}'.format(host, port))
        print('starting up on {} port {}'.format(host, port))
        self.sock.bind((host, port))
        self.sock.listen()


    def accept_connection(self):
        self.amazon_sock, self.amazon_address = self.sock.accept()
        #self.file_handle.write('received connection from {} port {}'.format(self.amazon_address))
        print(self.amazon_address)


    def make_connection(self, host, port):
        #self.file_handle.write('connecting to {} port {}'.format(host, port))
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
            time.sleep(5)
            for k in sorted(self.seq_dict):
                print("Resending to world ", self.seq_dict[k])
                self.send_data(self.seq_dict[k])
                break

    def resend_data_amazon(self):
        while True:
            time.sleep(5)
            for k in sorted(self.seq_dict):
                print("Resending to amazon ", self.seq_dict[k])
                self.send_data_amazon(self.seq_dict[k])
                break


    def __del__(self):
        #self.file_handle.write("Closing connection from...")
        self.sock.close()


    def init(self, database):
        # Resend mechanism
        th_resend = threading.Thread(target=self.resend_data_amazon, args=())
        th_resend.setDaemon(True)
        th_resend.start()

        self.database = database
        sendworld = amazon_ups_pb2.USendWorldId()
        sendworld = self.world.generate_world(sendworld)
        sendworld.seqnum = self.seq_num
        self.seq_dict[self.seq_num] = sendworld
        self.seq_num += 1
        self.send_data_amazon(sendworld)
        self.make_sure_world_send()

        th_handler = threading.Thread(target=self.handler_amazon, args=())
        th_handler.setDaemon(True)
        th_handler.start()


    def make_sure_world_send(self):
        gotworId = amazon_ups_pb2.AGotWorldId()
        self.recv_data_amazon(gotworId)
        self.seq_dict.pop(gotworId.acks, None)


    def set_world(self, world):
        self.world = world


    def set_database(self, database):
        self.database = database


    def handler_amazon(self):
        print("Handling request...")
        while True:
            request = amazon_ups_pb2.AMessage()
            self.recv_data_amazon(request)
            self.parse_request(request)

    
    # Generate UMessage
    def generate_message(self):
        message = amazon_ups_pb2.UMessage()
        return message


    ## Receive from amazon
    def parse_request(self, request):
        #self.file_handle.write()
        print("Received from amazon: ", request)
        self.parse_pickup(request)
        self.parse_loaded(request)
        self.parse_acks(request)
        self.parse_error(request)


    # Parse ARequirePickup
    def parse_pickup(self, request):
        res_to_amazon = self.generate_message()
        send = False
        for pic in request.reqPickup:
            if pic.seqnum not in self.recv_msg:
                self.recv_msg.add(pic.seqnum)
                # Update package info and info of item within it
                truck_id = self.database.find_truck()
                user_name = pic.upsaccount
                wh_id = pic.whnum
                package_id = pic.shipid

                #truck = Truck.objects.get(truck_id=truck_id)
                try:

                    user_id = self.database.get_userId(user_name)
                    self.database.create_package(package_id, wh_id, truck_id, user_id, pic.x, pic.y, pic.products)
                    # usr = User.objects.get(username=user_name)
                    # package_db = Package(package_id=package_id, wh_id=wh_id, truck=truck, user=usr, dest_x=pic.x, dest_y=pic.y)
                except:

                    user_id = -1
                    self.database.create_package(package_id, wh_id, truck_id, user_id, pic.x, pic.y, pic.products)
                    # package_db = Package(package_id=package_id, wh_id=wh_id, truck=truck, dest_x=pic.x, dest_y=pic.y)

                # package_db.save()
                # for prod in pic.products:
                #     prod_id = prod.id
                #     prod_desc = prod.description
                #     prod_cnt = prod.count
                #     prod_db = Product(product_id=prod_id, product_description=prod_desc, product_count=prod_cnt, product_package=package_db)
                #     prod_db.save()

                #package_db.save()
                res_to_amazon.acks.append(pic.seqnum)
                send = True
                # Send the truck to do pick up
                self.world.generate_pickup(truck_id, wh_id)
        if send:
            print("Sending to amazon: ", res_to_amazon)
            self.send_data_amazon(res_to_amazon)
        


    # Parse APackloaded
    def parse_loaded(self, request):
        res_to_amazon = self.generate_message()
        send = False
        for loa in request.reqPackLoaded:
            if loa.seqnum not in self.recv_msg:
                self.recv_msg.add(loa.seqnum)
                # Update the destination info of package
                truck_id = loa.truckid
                package_id = loa.shipid
                dest_x = loa.x
                dest_y = loa.y

                status = 'loaded'
                self.database.update_packageStat(package_id, status)
                # packageInfo = Package.objects.get(package_id=package_id)
                # packageInfo.package_status = 'loaded'
                # packageInfo.save()
                # Send the truck to do delivery
                self.world.generate_delivery(truck_id, package_id)
                res_to_amazon.acks.append(loa.seqnum)
                send = True
                self.generate_pack_load(package_id)
        if send:
            print("Sending to amazon: ", res_to_amazon)
            self.send_data_amazon(res_to_amazon)


    # Parse acks
    def parse_acks(self, request):
        for a in request.acks:
            self.seq_dict.pop(a, None)
        
    
    # Parse error
    def parse_error(self, request):
        res_to_amazon = self.generate_message()
        send = False
        for er in request.error:
            #self.file_handle.write()
            print(er.err)
            if er.seqnum not in self.recv_msg:
                self.recv_msg.add(er.seqnum)
                res_to_amazon.acks.append(er.seqnum)
                send = True
        if send:
            print("Sending to amazon: ", res_to_amazon)
            self.send_data_amazon(res_to_amazon)


    ## Send to amazon
    # Populate UPickupReceived
    def generate_pick_recv(self, package_id, tracking_num, truck_id):
        res_to_amazon = self.generate_message()
        
        pickup = res_to_amazon.pickupReceived.add()
        pickup.shipid = package_id
        pickup.trackingnum = tracking_num
        pickup.truckid = truck_id
        pickup.seqnum = self.seq_num
        
        self.seq_dict[self.seq_num] = res_to_amazon
        self.seq_num += 1
        print("Sending to amazon: ", res_to_amazon)
        self.send_data_amazon(res_to_amazon)
    

    # Populate UPackLoaded
    def generate_pack_load(self, package_id):
        res_to_amazon = self.generate_message()
        
        load = res_to_amazon.resPackLoaded.add()
        load.shipid = package_id
        load.seqnum = self.seq_num
        
        self.seq_dict[self.seq_num] = res_to_amazon
        self.seq_num += 1
        print("Sending to amazon: ", res_to_amazon)
        self.send_data_amazon(res_to_amazon)


    # Populate UPackDelivered
    def generate_pack_delv(self, package_id):
        res_to_amazon = self.generate_message()
        
        load = res_to_amazon.reqPackDelivered.add()
        load.shipid = package_id
        load.seqnum = self.seq_num
        
        self.seq_dict[self.seq_num] = res_to_amazon
        self.seq_num += 1
        print("Sending to amazon: ", res_to_amazon)
        self.send_data_amazon(res_to_amazon)

        

    
