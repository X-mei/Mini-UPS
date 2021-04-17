from .base_connect import MySocket
import world_ups_pb2
import amazon_ups_pb2
from ups.models import Truck, Package, Product
import threading

class Amazon(Base):

    def init(self):
        sendworld = amazon_ups_pb2.USendWorldId()
        sendworld = self.world.generate_world(sendworld)
        sendworld.seqnum = self.seq_num
        self.seq_dict[self.seq_num] = res_to_world
        self.seq_num += 1
        self.send_data(sendworld)
        self.make_sure_world_send()
        th_handler = threading.Thread(target=self.handler, args=())
        th_handler.setDaemon(True)
        th_handler.start()


    def make_sure_world_send(self):
        gotworld = amazon_ups_pb2.AGotWorldId()
        self.recv_data(gotworld)
        self.seq_dict.pop(gotworld.acks, None)


    def set_world(self, world):
        self.world = world


    def handler(self):
        print("Handling request...")
        while True:
            request = amazon_ups_pb2.AMessage()
            self.recv_data(request)
            self.parse_request(request)

    
    # Generate UMessage
    def generate_message(self):
        message = amazon_ups_pb2.UMessage()
        return message


    ## Receive from amazon
    def parse_request(self, request):
        print("Received: ", request)
        self.parse_pickup(request)
        self.parse_loaded(request)
        self.parse_acks(request)
        self.parse_error(request)


    # Parse ARequirePickup
    def parse_pickup(self, request):
        res_to_amazon = self.generate_message()
        for pic in request.reqPickup:
            if pic.seqnum not in self.recv_msg:
                self.recv_msg.add(pic.seqnum)
                # Update package info and info of item within it
                truck_id = # Some function in database.py to find a available truck
                user_name = pic.upsaccount
                wh_id = pic.whnum
                package_id = pic.shipid
                package_db = Package(user=user_name, package_id=package_id, wh_id=wh_id, truck=truck_id)
                for prod in pic.products:
                    prod_id = prod.id
                    prod_desc = prod.description
                    prod_cnt = prod.count
                    prod_db = Product(product_id=prod_id, product_description=prod_desc, product_count=prod_cnt, product_package=package_id)
                    prod_db.save()
                package_db.save()
                res_to_amazon.acks.append(pic.seqnum)
                # Send the truck to do pick up
                self.world.generate_pickup(truck_id, wh_id)
        self.send_data(res_to_amazon)


    # Parse APackloaded
    def parse_loaded(self, request):
        res_to_amazon = self.generate_message()
        for loa in request.reqPackLoaded:
            if loa.seqnum not in self.recv_msg:
                self.recv_msg.add(loa.seqnum)
                # Update the destination info of package
                truck_id = loa.truckid
                package_id = loa.truckid
                dest_x = loa.x
                dest_y = loa.y
                packageInfo = Package.objects.get(package_id=package_id, truck=truck_id)
                packageInfo.dest_x = dest_x
                packageInfo.dest_y = dest_y
                packageInfo.save()
                # Send the truck to do delivery
                self.world.generate_delivery(truck_id, package_id)
                res_to_amazon.acks.append(loa.seqnum)
                self.generate_pack_load(package_id)
        self.send_data(res_to_amazon)


    # Parse acks
    def parse_ack(self, request):
        for a in request.acks:
            self.seq_dict.pop(a, None)
        
    
    # Parse error
    def parse_error(self, request):
        res_to_amazon = self.generate_message()
        for er in request.error:
            print(er.err)
            if er.seqnum not in self.recv_msg:
                self.recv_msg.add(er.seqnum)
                res_to_amazon.acks.append(er.seqnum)
        self.send_data(res_to_amazon)


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
        self.send_data(res_to_amazon)
    

    # Populate UPackLoaded
    def generate_pack_load(self, package_id):
        res_to_amazon = self.generate_message()
        
        load = res_to_amazon.resPackLoaded.add()
        load.shipid = package_id
        pickup.seqnum = self.seq_num
        
        self.seq_dict[self.seq_num] = res_to_amazon
        self.seq_num += 1
        self.send_data(res_to_amazon)


    # Populate UPackDelivered
    def generate_pack_delv(self, package_id):
        res_to_amazon = self.generate_message()
        
        load = res_to_amazon.reqPackDelivered.add()
        load.shipid = package_id
        pickup.seqnum = self.seq_num
        
        self.seq_dict[self.seq_num] = res_to_amazon
        self.seq_num += 1
        self.send_data(res_to_amazon)

        

    