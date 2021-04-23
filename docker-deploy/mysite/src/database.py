import psycopg2
import sys
import threading
import time
import smtplib
import amazon_ups_pb2
import world_ups_pb2
# from . import amazon_ups_pb2
# from . import world_ups_pb2

class Database():
    #connect with the database
    def __init__(self):
        try:
            self.conn = psycopg2.connect(database='postgres', user='postgres', password='postgres', host='db', port='5432')
            print("Connected to database successfully.")
        except:
            print("Failed to connect to database ")

    def __del__(self):
        self.conn.close()

    #find a truck that can be sent to a warehouse to pick up a package
    def find_truck(self):
        cur = self.conn.cursor()
        cur.execute("SELECT truck_id FROM ups_truck WHERE status = 'idle' OR status = 'arrive warehouse' OR status = 'delivering';")
        result = cur.fetchone()
        cur.execute("UPDATE ups_truck SET status = 'travelling' WHERE truck_id = %s;", result)
        self.conn.commit()
        return result[0]

    #create trucks 
    def create_truck(self):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO ups_truck (x, y, status) VALUES (1, 1, 'idle') returning truck_id;")
        result = cur.fetchone()
        self.conn.commit()
        return result[0]

    #update truck status
    def update_truck(self, cur_x, cur_y, cur_status, truck_id):
        cur = self.conn.cursor()
        cur.execute("UPDATE ups_truck SET x = %s, y = %s, status = %s WHERE truck_id = %s;", (cur_x, cur_y, cur_status, truck_id,))
        self.conn.commit()
        
    #get package in truck
    def get_package(self, truck_id):
        cur = self.conn.cursor()
        cur.execute("SELECT package_id FROM ups_package WHERE truck_id = %s;", (truck_id,))
        result = cur.fetchone()
        self.conn.commit()
        return result[0]

    #add tracking number to package
    def add_trackingNum(self, package_id, tracking_num):
        cur = self.conn.cursor()
        cur.execute("UPDATE ups_package SET tracking_num = %s WHERE package_id = %s;", (tracking_num, package_id,))
        self.conn.commit()

    #update package status
    def update_packageStat(self, package_id, status):
        cur = self.conn.cursor()
        cur.execute("UPDATE ups_package SET package_status = %s WHERE package_id = %s;", (status, package_id,))
        self.conn.commit()
        
    #get package destination
    def get_packageDest(self, package_id):
        cur = self.conn.cursor()
        cur.execute("SELECT dest_x, dest_y FROM ups_package WHERE package_id = %s;", (package_id,))
        result = cur.fetchone()
        self.conn.commit()
        return result[0], result[1]

    #get user id
    def get_userId(self, username):
        cur = self.conn.cursor()
        cur.execute("SELECT id FROM ups_user WHERE username = %s", (username,))
        result = cur.fetchone()
        self.conn.commit()
        return result[0]


    #create a package
    def create_package(self, package_id, wh_id, truck_id, user_id, x, y, products):
        cur = self.conn.cursor()
        status = 'packing'
        if user_id == -1:
            cur.execute("INSERT INTO ups_package (package_id, wh_id, dest_x, dest_y, truck_id, package_status) \
                    VALUES (%s, %s, %s, %s, %s, %s);", (package_id, wh_id, x, y, truck_id, status, ))
        else:
            cur.execute("INSERT INTO ups_package (package_id, wh_id, dest_x, dest_y, truck_id, user_id, package_status) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s);", (package_id, wh_id, x, y, truck_id, user_id, status, ))
        self.conn.commit()
        for prod in products:
            self.create_product(prod.id, prod.description, prod.count, package_id)


    #create a product
    def create_product(self, prod_id, prod_desc, prod_cnt, package_id):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO ups_product (product_id, product_description, product_count, product_package_id) \
                    VALUES (%s, %s, %s, %s);", (prod_id, prod_desc, prod_cnt, package_id, ))
        self.conn.commit()


# #connect with the database
# def db_connect():
#     try:
#         conn = psycopg2.connect(database='postgres', user='postgres', password="passw0rd", host='127.0.0.1', port='5432')
#         # print("Connected to database successfully.")
#         return conn
#     except:
#         print("Failed to connect to database ")


# #find a truck that can be sent to a warehouse to pick up a package
# def find_truck():
#     conn = db_connect()
#     cur = conn.cursor()
#     cur.execute("SELECT truck_id FROM ups_truck WHERE status = 'idle' OR status = 'arrive warehouse' OR status = 'delivering';")
#     result = cur.fetchone()
#     cur.execute("UPDATE ups_truck SET status = 'travelling' WHERE truck_id = %s;", result)
#     conn.commit()
#     conn.close()
#     return result[0]


# #create trucks 
# def create_truck():
#     conn=db_connect()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO ups_truck (x, y, status) VALUES (1, 1, 'idle') returning truck_id;")
#     result = cur.fetchone()
#     conn.commit()
#     conn.close()
#     return result[0]


# #update truck status
# def update_truck(cur_x, cur_y, cur_status, truck_id):
#     conn=db_connect()
#     cur = conn.cursor()
#     cur.execute("UPDATE ups_truck SET x = %s, y = %s, status = %s WHERE truck_id = %s;", (cur_x, cur_y, cur_status, truck_id,))
#     conn.commit()
#     conn.close()


# #get package in truck
# def get_package(truck_id):
#     conn=db_connect()
#     cur = conn.cursor()
#     cur.execute("SELECT package_id FROM ups_package WHERE truck_id = %s;", (truck_id,))
#     result = cur.fetchone()
#     conn.commit()
#     conn.close()
#     return result[0]


# #add tracking number to package
# def add_trackingNum(package_id, tracking_num):
#     conn=db_connect()
#     cur = conn.cursor()
#     cur.execute("UPDATE ups_package SET tracking_num = %s WHERE package_id = %s;", (tracking_num, package_id,))
#     conn.commit()
#     conn.close()


# #update package status
# def update_packageStat(package_id, status):
#     conn=db_connect()
#     cur = conn.cursor()
#     cur.execute("UPDATE ups_package SET package_status = %s WHERE package_id = %s;", (status, package_id,))
#     conn.commit()
#     conn.close()


# #get package destination
# def get_packageDest(package_id):
#     conn=db_connect()
#     cur = conn.cursor()
#     cur.execute("SELECT dest_x, dest_y FROM ups_package WHERE package_id = %s;", (package_id,))
#     result = cur.fetchone()
#     conn.commit()
#     conn.close()
#     return result[0], result[1]


# #get user id
# def get_userId(username):
#     conn = db.connect()
#     cur = conn.cursor()
#     cur.execute("SELECT id FROM ups_user WHERE username = %s", (username,))
#     result = cur.fetchone()
#     cur.commit()
#     cur.close()
#     return result[0]


# #create a package
# def create_package(package_id, wh_id, truck_id, user_id, x, y):
#     conn = db_connect()
#     cur = conn.cursor()
#     status = 'packing'
#     if user_id == -1:
#         cur.execute("INSERT INTO ups_package (package_id, wh_id, dest_x, dest_y, truck_id, package_status) \
#                 VALUES (%s, %s, %s, %s, %s, %s);", (package_id, wh_id, x, y, truck_id, status, ))
#     else:
#         cur.execute("INSERT INTO ups_package (package_id, wh_id, dest_x, dest_y, truck_id, user_id, package_status) \
#                 VALUES (%s, %s, %s, %s, %s, %s, %s);", (package_id, wh_id, x, y, truck_id, user_id, status, ))
    
#     conn.commit()
#     conn.close()

# #create a product
# def create_product(prod_id, prod_desc, prod_cnt, package_id):
#     conn = db_connect()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO ups_product (product_id, product_description, product_count, product_package_id) \
#                 VALUES (%s, %s, %s, %s);", (prod_id, prod_desc, prod_cnt, package_id, ))
#     conn.commit()
#     conn.close()



##might not be useful
#get the status of a truck
# def get_status(truck_id):
#     conn = db.connect()
#     cur = conn.cursor()
#     cur.execute("SELECT status FROM ups_truck WHERE truck_id = %s", (truck_id, ))
#     result = cur.fetchone()
#     cur.commit()
#     cur.close()
#     return result[0]


# #get the status of a package
# def get_package_status(package_id):
#     conn = db.connect()
#     cur = conn.cursor()
#     cur.execute("SELECT package_status FROM ups_package WHERE package_id = %s", (package_id,))
#     result = cur.fetchone()
#     cur.commit()
#     cur.close()
#     return result[0]

