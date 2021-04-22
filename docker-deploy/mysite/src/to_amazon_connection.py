from .base_connect import MySocket
from . import amazon_ups_pb2
from . import world_ups_pb2
from ups.models import Truck, Package, Product, User
from .database import *
import threading

class Amazon(MySocket):

    def init(self):
        # Resend mechanism
        th_resend = threading.Thread(target=self.resend_data_amazon, args=())
        th_resend.setDaemon(True)
        th_resend.start()

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
                truck_id = find_truck()# Some function in database.py to find a available truck
                user_name = pic.upsaccount
                wh_id = pic.whnum
                package_id = pic.shipid
                truck = Truck.objects.get(truck_id=truck_id)
                try:
                    usr = User.objects.get(username=user_name)
                    package_db = Package(package_id=package_id, wh_id=wh_id, truck=truck, user=usr, dest_x=pic.x, dest_y=pic.y)
                except:
                    package_db = Package(package_id=package_id, wh_id=wh_id, truck=truck, dest_x=pic.x, dest_y=pic.y)
                
                package_db.save()
                for prod in pic.products:
                    prod_id = prod.id
                    prod_desc = prod.description
                    prod_cnt = prod.count
                    prod_db = Product(product_id=prod_id, product_description=prod_desc, product_count=prod_cnt, product_package=package_db)
                    prod_db.save()
                package_db.save()
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
                #self.file_handle.write()
                #truck = Truck.objects.get(truck_id=truck_id)
                packageInfo = Package.objects.get(package_id=package_id)#, truck=truck)
                packageInfo.package_status = 'loaded'
                #packageInfo.dest_x = dest_x
                #packageInfo.dest_y = dest_y
                packageInfo.save()
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

        

    
