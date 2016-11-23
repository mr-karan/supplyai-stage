from sqlalchemy import (Table, Column, Integer, String, Boolean, TIMESTAMP)

def create_tables(con,meta, csvdata):

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
        Column('weight', Integer)
        )
    result = Table('result', meta,
        Column('order_id', String, primary_key=True),
        Column('buyer_city', String),
        Column('seller_city', String),
        Column('product_category', String),
        Column('shipper_name', String),
        Column('order_created_date', TIMESTAMP)
    )
    meta.create_all(con)
    so = con.raw_connection()
    cursor = so.cursor()
    cmd = 'COPY fulldata FROM STDIN WITH (FORMAT CSV, HEADER TRUE)'
    cursor.copy_expert(cmd, csvdata)
    so.commit()
