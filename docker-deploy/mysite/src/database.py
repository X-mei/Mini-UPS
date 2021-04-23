import psycopg2
import sys
import threading
import time
import smtplib

#connect with the database
def db_connect():
    try:
        conn = psycopg2.connect(database='postgres', user='postgres', password="passw0rd", host='127.0.0.1', port='5432')
        # print("Connected to database successfully.")
        return conn
    except:
        print("Failed to connect to database ")

#find a truck that can be sent to a warehouse to pick up a package
def find_truck():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT truck_id FROM ups_truck WHERE status = 'idle' OR status = 'arrive warehouse' OR status = 'delivering';")
    result = cur.fetchone()
    cur.execute("UPDATE ups_truck SET status = 'travelling' WHERE truck_id = %s;", result)
    conn.commit()
    conn.close()
    return result[0]

#create trucks 
def create_truck():
    conn=db_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO ups_truck (x, y, status) VALUES (1, 1, 'idle') returning truck_id;")
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result[0]

#update truck status
def update_truck(cur_x, cur_y, cur_status, truck_id):
    conn=db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE ups_truck SET x = %s, y = %s, status = %s WHERE truck_id = %s;", (cur_x, cur_y, cur_status, truck_id, ))
    conn.commit()
    conn.close()


def get_package(truck_id):
    conn=db_connect()
    cur = conn.cursor()
    cur.execute("SELECT package_id FROM ups_package WHERE truck_id = %s;", (truck_id,))
    result = cur.fetchone()
    conn.commit()
    conn.close()
    return result[0]



#add tracking number to package
def add_trackingNum(package_id, tracking_num):
    conn=db_connect()
    cur = conn.cursor()
    cur.execute("UPDATE ups_package SET tracking_num = %s WHERE package_id = %s;", (tracking_num, package_id, ))
    conn.commit()
    conn.close()

#create a package
def create_package(packageInfo, truck_id):
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO ups_package (package_id, wh_id, w_x, w_y, d_x, d_y, truck_id, acc_id, status) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", package_id, wh_id, w_x, w_y, d_x, d_y, truck_id, acc_id, status)
    conn.commit()
    conn.close()

#get the status of a truck
def get_status(truck_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT status FROM ups_truck WHERE truck_id = %s", truck_id)
    result = cur.fetchone()
    cur.commit()
    cur.close()
    return result[0]

#get the status of a package
def get_package_status(package_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT package_status FROM ups_package WHERE package_id = %s", package_id)
    result = cur.fetchone()
    cur.commit()
    cur.close()
    return result[0]


def truck_from_idle_to_travelling(truck_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT status FROM ups_truck WHERE truck_id = %s", truck_id)
    result = cur.fetchone()
    if result[0] == 'idle':
        cur.execute("UPDATE ups_truck SET status = 'travelling' WHERE truck_id = %s", truck_id)
        cur.commit()
        cur.close()


def truck_from_travelling_to_arrive(truck_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT status FROM ups_truck WHERE truck_id = %s", truck_id)
    result = cur.fetchone()
    if result[0] == 'travelling':
        cur.execute("UPDATE ups_truck SET status = 'arrive warehouse' WHERE truck_id = %s", truck_id)
        cur.commit()
        cur.close()


def truck_from_arrive_to_loading(truck_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT status FROM ups_truck WHERE truck_id = %s", truck_id)
    result = cur.fetchone()
    if result[0] == 'arrive':
        cur.execute("UPDATE ups_truck SET status = 'loading' WHERE truck_id = %s", truck_id)
        cur.commit()
        cur.close()


def truck_from_loading_to_delivering(truck_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT status FROM ups_truck WHERE truck_id = %s", truck_id)
    result = cur.fetchone()
    if result[0] == 'loading':
        cur.execute("UPDATE ups_truck SET status = 'delivering' WHERE truck_id = %s", truck_id)
        cur.commit()
        cur.close()


def truck_from_delivering_to_idle(truck_id):
    conn = db.connect()
    cur = conn.cursor()
    cur.execute("SELECT status FROM ups_truck WHERE truck_id = %s", truck_id)
    result = cur.fetchone()
    if result[0] == 'delivering':
        cur.execute("UPDATE ups_truck SET status = 'idle' WHERE truck_id = %s", truck_id)
        cur.commit()
        cur.close()
