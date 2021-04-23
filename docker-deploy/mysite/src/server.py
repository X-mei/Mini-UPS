# from .to_world_connection import World
# from .to_amazon_connection import Amazon
# from .database import Database
from to_world_connection import World
from to_amazon_connection import Amazon
from database import Database
import threading

world_host = 'vcm-18172.vm.duke.edu'
#world_host = 'vcm-19617.vm.duke.edu'
world_port = 12345

#amazon_host = 'vcm-18235.vm.duke.edu'
amazon_port = 33334

class Server():
    def __init__(self):
        self.database = Database()
        self.world = World()
        self.amazon = Amazon()
        self.world.make_connection(world_host, world_port)
        self.world.init(5, self.database)
        self.amazon.setup_server(world_host, amazon_port)
        self.amazon.accept_connection()
        self.world.set_amazon(self.amazon)
        self.amazon.set_world(self.world)
        self.amazon.init(self.database)

if __name__=='__main__':
    print("Initiating server...")
    server = Server()


