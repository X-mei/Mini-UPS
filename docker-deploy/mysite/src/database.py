import psycopg2
import sys
import threading
import time
import smtplib

def db_connect():
    try:
        conn = psycopg2.connect(database='postgres', user='postgres', password="passw0rd", host='127.0.0.1', port='5432')
        print("Opened database successfully.")
        return conn
    except:
        print("Failed to connect to database ")

def find_truck():
    conn = db_connect()
    cur = conn.cursor()
    cur.execute("SELECT truck_id FROM ups_truck WHERE truck_status = 'idle' OR truck_status = 'arrive warehouse' OR truck_status = 'delivering';")
    result = cur.fetchone()
    cur.execute("UPDATE ups_truck SET truck_status = 'travelling' WHERE truck_id = %s;", result[0])
    conn.commit()
    conn.close()
    return result[0]


def create_package(package, truck_id):
    conn = db_connect()
    cur = conn.cursor()
    
