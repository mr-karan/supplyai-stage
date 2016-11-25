from numpy import genfromtxt
from time import time
from datetime import datetime
from sqlalchemy import Column, Integer, Date, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

def Load_Data():
    df = pd.read_csv('data.csv', sep=',')
    df = df.where((pd.notnull(df)), None)

    return df.as_matrix().tolist()

Base = declarative_base()

class FullData(Base):
    #Tell SQLAlchemy what the table name is and if there's any table-specific arguments it should know about
    __tablename__ = 'result'
    #tell SQLAlchemy the name of column and its attributes:

    order_id = Column('order_id', String, primary_key=True, nullable= False)
    buyer_city = Column('buyer_city', String)
    seller_city = Column('seller_city', String)
    product_category = Column('product_category', String)
    shipper_name = Column('shipper_name', String)
    order_created_date = Column('order_created_date', TIMESTAMP)


def load(con,meta,session):
    print("hi")

    #try:
    file_name = "data.csv"
    data = Load_Data() 
    print("n")
    for i in data:
        record = FullData(**{
            'order_id' : i[16],
            'buyer_city' : i[3],
            'seller_city' : i[30],
            'product_category' : i[18],
            'shipper_name' : i[33],
            'order_created_date' : i[15]
        })
        print(record)
        session.add(record) #Add all the records

    session.commit() #Attempt to commit all the records
    '''
    except:
        print("no")
        session.rollback() #Rollback the changes on error
    finally:
        session.close() #Close the connection
    '''