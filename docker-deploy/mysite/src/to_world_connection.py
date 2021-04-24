# from base_connect import MySocket
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
# from ups.models import Truck, Package, Product
# from .database import Database
# import threading

class World():
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


    def init(self, count):
        # Resend mechanism
        th_resend = threading.Thread(target=self.resend_data, args=())
        th_resend.setDaemon(True)
        th_resend.start()

        connect = world_ups_pb2.UConnect()
        connected = world_ups_pb2.UConnected()
        # self.database = database
        # Add truck to database with default settings
        for i in range(count):
            truck_id = create_truck()
            newtruck = connect.trucks.add()
            newtruck.id = truck_id
            newtruck.x = 1
            newtruck.y = 1
            # truck = Truck()
            # truck.save()
            # newtruck = connect.trucks.add()
            # newtruck.id = truck.truck_id
            # newtruck.x = truck.x
            # newtruck.y = truck.y
        connect.isAmazon = False
        self.send_data(connect)
        self.recv_data(connected)
        #self.file_handle.write(connected.result)
        self.world_id = connected.worldid
        th_handler = threading.Thread(target=self.handler, args=())
        th_handler.setDaemon(True)
        th_handler.start()

    
    def generate_world(self, sendworld):
        sendworld.worldid = self.world_id
        return sendworld
        

    def set_amazon(self, amazon):
        self.amazon = amazon


    def handler(self):
        #self.file_handle.write()
        print("Handling response...")
        while True:
            response = world_ups_pb2.UResponses()
            self.recv_data(response)
            self.parse_responses(response)


    ### Handle communication with world
    # Generate Ucommands
    def generate_command(self):
        command = world_ups_pb2.UCommands()
        return command


    ## To Parse UResponses
    def parse_responses(self, response):
        #self.file_handle.write()
        print("Received from world: ", response)
        # Parse each field in the message
        self.parse_finished(response)
        self.parse_delivered(response)
        self.parse_truckInfo(response)
        self.parse_error(response)
        self.parse_ack(response)
        #parse_disconnected(response)


    # Parse UFinished
    def parse_finished(self, response):
        res_to_world = self.generate_command()
        send = False
        for fin in response.completions:
            if fin.seqnum not in self.recv_msg:
                self.recv_msg.add(fin.seqnum)
                # Update status of all trucks
                truck_id = fin.truckid
                coor_x = fin.x
                coor_y = fin.y
                stat = fin.status

                update_truck(coor_x, coor_y, stat, truck_id)
                # curr_truck = Truck.objects.get(truck_id=truck_id)
                # curr_truck.x = coor_x
                # curr_truck.y = coor_y
                # curr_truck.status = stat
                # curr_truck.save()
                res_to_world.acks.append(fin.seqnum)
                send = True
                # Send pick up received if status is "arrive warehouse"

                package_id = get_package(truck_id)
                # curr_pack = Package.objects.get(truck=truck_id)
                if stat == 'ARRIVE WAREHOUSE':

                    tracking_num = str(package_id)
                    add_trackingNum(package_id, tracking_num)
                    self.amazon.generate_pick_recv(package_id, tracking_num, truck_id)
                    # p_id = curr_pack.package_id
                    # curr_pack.tracking_num = str(p_id)
                    # curr_pack.save()
                    # self.amazon.generate_pick_recv(curr_pack.package_id, curr_pack.tracking_num, curr_pack.truck.truck_id)
                # Do nothing if its a completion of all deliveries
                else:
                    pass
                    #print("Error with status.")
        if send:
            print("Sending to world: ", res_to_world)
            self.send_data(res_to_world)


    # Parse UDeliveryMade
    def parse_delivered(self, response):
        res_to_world = self.generate_command()
        send = False
        # Update status of all package
        for delv in response.delivered:
            if delv.seqnum not in self.recv_msg:
                self.recv_msg.add(delv.seqnum)
                truck_id = delv.truckid
                package_id = delv.packageid
                stat = 'delivered'

                update_packageStat(package_id, stat)
                # curr_package = Package.objects.get(truck_id=truck_id, package_id=package_id)
                # curr_package.package_status = stat
                # curr_package.save()
                res_to_world.acks.append(delv.seqnum)
                # Send package delivered message

                self.amazon.generate_pack_delv(package_id)
                # self.amazon.generate_pack_delv(curr_package.package_id)
                send = True
        if send:
            print("Sending to world: ", res_to_world)
            self.send_data(res_to_world)
    

    # Parse UTruck
    def parse_truckInfo(self, response):
        res_to_world = self.generate_command()
        send = False
        # Update status of all package
        for ti in response.truckstatus:
            if ti.seqnum not in self.recv_msg:
                self.recv_msg.add(ti.seqnum)
                truck_id = ti.truckid
                coor_x = ti.x
                coor_y = ti.y
                stat = ti.status

                update_truck(coor_x, coor_y, stat, truck_id)
                # curr_truck = Truck.objects.get(truck_id=truck_id)
                # curr_truck.x = coor_x
                # curr_truck.y = coor_y
                # curr_truck.status = stat
                # curr_truck.save()
                res_to_world.acks.append(ti.seqnum)
                send = True
        if send:
            print("Sending to world: ", res_to_world)
            self.send_data(res_to_world)


    # Parse acks
    def parse_ack(self, response):
        for a in response.acks:
            self.seq_dict.pop(a, None)
        
    
    # Parse error
    def parse_error(self, response):
        res_to_world = self.generate_command()
        send = False
        for er in response.error:
            #self.file_handle.write()
            #print(er.err)
            if er.seqnum not in self.recv_msg:
                self.recv_msg.add(er.seqnum)
                res_to_world.acks.append(er.seqnum)
                send = True
        if send:
            print("Sending to world: ", res_to_world)
            self.send_data(res_to_world)
        
    

    ## To generate UCommands
    # Populate UGoPickup
    # might need to make a query before this function call to get the available truck id #
    def generate_pickup(self, truck_id, wh_id):
        res_to_world = self.generate_command()
        
        pickup = res_to_world.pickups.add()
        pickup.whid = wh_id
        pickup.truckid = truck_id
        pickup.seqnum = self.seq_num
        
        self.seq_dict[self.seq_num] = res_to_world
        self.seq_num += 1
        print("Sending to world: ", res_to_world)
        self.send_data(res_to_world)
    

    # Populate UGoDeliver
    def generate_delivery(self, truck_id, package_id):
        res_to_world = self.generate_command()
        # Get info of given package id

        dest_x, dest_y = get_packageDest(package_id)
        # packageInfo = Package.objects.get(package_id=package_id)
        
        delivery = res_to_world.deliveries.add()
        delivery.truckid = truck_id
        delivery.seqnum = self.seq_num

        package = delivery.packages.add()
        package.packageid = package_id
        
        package.x = dest_x
        package.y = dest_y
        # package.x = packageInfo.dest_x
        # package.y = packageInfo.dest_y

        self.seq_dict[self.seq_num] = res_to_world
        self.seq_num += 1
        print("Sending to world: ", res_to_world)
        self.send_data(res_to_world)


    # Populate UQuery
    def generate_query(self, truck_id):
        res_to_world = self.generate_command()
        # Get info of given truck id
        query = res_to_world.queries.add()
        query.truckid = truck_id
        query.seqnum = self.seq_num

        self.seq_dict[self.seq_num] = res_to_world
        self.seq_num += 1
        print("Sending to world: ", res_to_world)
        self.send_data(res_to_world)




