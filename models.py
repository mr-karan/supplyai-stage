from sqlalchemy import (Table, Column, Integer, String, Boolean, TIMESTAMP)
import pandas as pd
from sqlalchemy.exc import IntegrityError


def Load_Data(path):
    df = pd.read_csv(path, sep=',')
    df = df.where((pd.notnull(df)), None)

    return df.as_matrix().tolist()

def create_tables(con,meta, session, path,lower_limit,upper_limit):
    fulldata = Table('fulldata', meta,
        Column('id', Integer, autoincrement=True), 
        Column('awb', Integer),
        Column('breadth', Integer),
        Column('buyer_city', String),
        Column('buyer_pin', Integer),
        Column('cancelled_date', TIMESTAMP),
        Column('current_status', String),
        Column('delivered_date', TIMESTAMP),
        Column('delivery_attempt_count', Integer),
        Column('dispatch_date', TIMESTAMP),
        Column('heavy', Boolean),
        Column('height', Integer),
        Column('last_mile_arrival_date', TIMESTAMP),
        Column('last_modified', TIMESTAMP),
        Column('length', Integer),
        Column('order_created_date', TIMESTAMP),
        Column('order_id', String, primary_key=True),
        Column('price', Integer),
        Column('product_category', String),
        Column('product_id', String),
        Column('product_name', String),
        Column('product_price', Integer),
        Column('product_qty', Integer),
        Column('promised_date', TIMESTAMP),
        Column('return_cause', String),
        Column('reverse_logistics_booked_date', TIMESTAMP),
        Column('reverse_logistics_date', TIMESTAMP),
        Column('reverse_logistics_delivered_date', TIMESTAMP),
        Column('rto_date', TIMESTAMP),
        Column('rto_delivered_date', TIMESTAMP),
        Column('seller_city', String),
        Column('seller_pin', Integer),
        Column('shipper_confirmation_date', TIMESTAMP),
        Column('shipper_name', String),
        Column('shipping_cost', Integer),
        Column('weight', Integer),
        extend_existing=True
        )
    result = Table('result', meta,
        Column('order_id', String, primary_key=True),
        Column('buyer_city', String),
        Column('seller_city', String),
        Column('product_category', String),
        Column('shipper_name', String),
        Column('order_created_date', TIMESTAMP),
        extend_existing=True
    )
    meta.create_all(con)
    result  = meta.tables['result']
    fulldata = meta.tables['fulldata']
    so = con.raw_connection()
    cursor = so.cursor()
    data = Load_Data(path) 

    api_result =[]
    for i in data[lower_limit:upper_limit]:
        record = {
                    'id' : i[0],
                    'awb' : i[1],
                    'breadth' : i[2],
                    'buyer_city' : i[3],
                    'buyer_pin' : i[4],
                    'cancelled_date' : i[5],
                    'current_status' : i[6],
                    'delivered_date' : i[7],
                    'delivery_attempt_count' : i[8],
                    'dispatch_date' : i[9],
                    'heavy' : i[10],
                    'height' : i[11],
                    'last_mile_arrival_date' : i[12],
                    'last_modified' : i[13],
                    'length' : i[14],
                    'order_created_date' : i[15],
                    'order_id' : i[16],
                    'price' : i[17],
                    'product_category' : i[18],
                    'product_id' : i[19],
                    'product_name' : i[20],
                    'product_price' : i[21],
                    'product_qty' : i[22],
                    'promised_date' : i[23],
                    'return_cause' : i[24],
                    'reverse_logistics_booked_date' : i[25],
                    'reverse_logistics_date' : i[26],
                    'reverse_logistics_delivered_date' : i[27],
                    'rto_date' : i[28],
                    'rto_delivered_date' : i[29],
                    'seller_city' : i[30],
                    'seller_pin' : i[31],
                    'shipper_confirmation_date' : i[32],
                    'shipper_name' : i[33],
                    'shipping_cost' : i[34],
                    'weight' : i[35]
                }
        api_result.append(record)
        try:
            con.execute(fulldata.insert(), record)
        except IntegrityError:
            pass
        smallertable =  'INSERT into result (order_id, buyer_city, seller_city, product_category,'\
                    'shipper_name,order_created_date)\nSELECT order_id, buyer_city, seller_city,product_category,'\
                    'shipper_name,order_created_date\nFROM fulldata'
    
        try:
            cursor.execute(smallertable)

        except:
                pass
    so.commit()


        
    return api_result

