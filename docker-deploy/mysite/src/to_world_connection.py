from .base_connect import MySocket
import world_ups_pb2
import amazon_ups_pb2
from ups.models import Truck, Package
import threading

class World(MySocket):
    def handler(self):
        while True:
            response = world_ups_pb2.UResponses()
            self.recv_data(response)
            self.parse_responses(response)


    ### Handle communication with world
    # Generate Ucommands
    def generate_command(self):
        command = world_ups_pb2.UCommands()
        command.simspeed = simspeed
        return command

    ## To Parse UResponses
    def parse_responses(self, response):
        print("Received: ", response)
        # Parse each field in the message
        parse_finished(response)
        parse_delivered(response)
        parse_truckInfo(response)
        parse_error(response)
        parse_ack(response)
        #parse_disconnected(response)


    # Parse UFinished
    def parse_finished(self, response):
        res_to_world = self.generate_command()
        # Update status of all trucks
        for fin in response.completions:
            if fin.seqnum not in self.recv_msg:
                self.recv_msg.add(fin.seqnum)
                truck_id = fin.truckid
                coor_x = fin.x
                coor_y = fin.y
                stat = fin.status
                curr_truck = Truck.objects.get(truck_id=truck_id)
                curr_truck.x = coor_x
                curr_truck.y = coor_y
                curr_truck.status = stat
                curr_truck.save()
                res_to_world.acks.append(fin.seqnum)
        self.send_data(res_to_world)


    # Parse UDeliveryMade
    def parse_delivered(self, response):
        res_to_world = self.generate_command()
        # Update status of all package
        for delv in response.delivered:
            if delv.seqnum not in self.recv_msg:
                self.recv_msg.add(delv.seqnum)
                truck_id = delv.truckid
                package_id = delv.packageid
                stat = 'delivered'
                curr_package = Package.objects.get(truck_id=truck_id, package_id=package_id)
                curr_package.package_status = stat
                curr_package.save()
                res_to_world.acks.append(delv.seqnum)
        self.send_data(res_to_world)
    

    # Parse UTruck
    def parse_truckInfo(self, response):
        res_to_world = self.generate_command()
        # Update status of all package
        for ti in response.truckstatus:
            if ti.seqnum not in self.recv_msg:
                self.recv_msg.add(ti.seqnum)
                truck_id = ti.truckid
                coor_x = ti.x
                coor_y = ti.y
                stat = ti.status
                curr_truck = Truck.objects.get(truck_id=truck_id)
                curr_truck.x = coor_x
                curr_truck.y = coor_y
                curr_truck.status = stat
                curr_truck.save()
                res_to_world.acks.append(ti.seqnum)
        self.send_data(res_to_world)


    # Parse acks
    def parse_ack(self, response):
        for a in response.acks:
            self.seq_dict.pop(a, None)
        
    
    # Parse error
    def parse_error(self, response):
        res_to_world = self.generate_command()
        for er in response.error:
            print(er.err)
            if er.seqnum not in self.recv_msg:
                self.recv_msg.add(er.seqnum)
                res_to_world.acks.append(er.seqnum)
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
        self.send_data(res_to_world)
    

    # Populate UGoDeliver
    def generate_delivery(self, truck_id, package_id):
        res_to_world = self.generate_command()
        # Get info of given package id
        packageInfo = Package.objects.get(package_id=package_id)

        delivery = res_to_world.deliveries.add()
        delivery.truckid = truck_id
        delivery.seqnum = self.seq_num

        package = delivery.packages.add()
        package.packageid = package_id
        package.x = packageInfo.dest_x
        package.y = packageInfo.dest_y

        self.seq_dict[self.seq_num] = res_to_world
        self.seq_num += 1
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
        self.send_data(res_to_world)




