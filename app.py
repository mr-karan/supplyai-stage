import os
import json
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug import secure_filename

import sqlalchemy
import ast
import pandas as pd
from models import create_tables
from sqlalchemy.sql import and_, or_
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
def connect(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object'''
    # We connect with the help of the PostgreSQL URL
    # postgresql://federer:grandestslam@localhost:5432/tennis
    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)

    # The return value of create_engine() is our connection object
    con = sqlalchemy.create_engine(url, client_encoding='utf8')

    # We then bind the connection to MetaData()
    meta = sqlalchemy.MetaData(bind=con, reflect=True)

    return con, meta

con, meta = connect('karan', 'karan', 'supplyai')
for i in (meta.tables):
    print(i)
Session = sessionmaker(bind=con)
session = Session()
cwd = os.getcwd()
UPLOAD_FOLDER = cwd + '/upload/'
ALLOWED_EXTENSIONS = set(['csv'])
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
filename = 'data.csv'

print(os.environ['APP_SETTINGS'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/query/', methods=['GET','POST'])
def query():
    result = meta.tables['fulldata']
    args = (request.args)
    conditions = []
    '''
In [320]: filter_group = [or_(full.c.seller_city == v for v in ['Winifredbury','Azariahshire']),or_(full.c.order_id == v for v in ['152ddd3f-4938-46bc-bdb2-44f18a044615'])]

In [321]: q = session.query(full.c.order_id).filter(and_(*filter_group))

In [322]: q.all()
Out[322]: [('152ddd3f-4938-46bc-bdb2-44f18a044615')]

In [323]: q = session.query(full.c.shipper_name).filter(and_(*filter_group))

In [324]: q.all()
Out[324]: [('SHPR7')]
    '''
    q = session.query(result.c.shipper_name)
    if request.args.get('order_id') is not None:
        conditions.append(result.c.order_id == args['order_id'])
    if request.args.get('seller_city') is not None:
        seller_cities = request.args.getlist('seller_city')[0].split(",")
        conditions.append(or_(result.c.seller_city == v for v in seller_cities))
    if request.args.get('buyer_city') is not None:
        buyer_cities = request.args.getlist('buyer_city')[0].split(",")
        conditions.append(or_(result.c.buyer_city == v for v in buyer_cities))
    if request.args.get('product_category') is not None:
        product_category = request.args.getlist('product_category')[0].split(",")
        conditions.append(or_(result.c.product_category == v for v in product_category))

    data = q.filter(and_(*conditions)).all()
    print(data)
    return jsonify(data)

@app.route('/count', methods=['GET'])
def count():
    result = meta.tables['fulldata']
    shipper_name = request.args.get('shipper_name')
    m = session.query(result.c.order_created_date, func.count(result.c.order_created_date)).filter(result.c.shipper_name== shipper_name).group_by(result.c.order_created_date).all()
    return jsonify(m)


@app.route("/fetch/")
def fetch():
    if request.args.get('n') is None:
        return "Range parameter n not specified."
    l  = list(map(int,request.args.get('n').split("-")))

    try:
        upper_limit = l[1]
    except IndexError:
        upper_limit = l[0]+1
    lower_limit = l[0]

    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    df = pd.read_csv(path, sep=',')
    df = df.where((pd.notnull(df)), None)
    data = df.iloc[lower_limit:upper_limit]

    data.to_sql('fulldata', con, if_exists='append')
    return "Success. {} to {} rows have been inserted in DB".format(lower_limit,upper_limit)
    
@app.route("/upload", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #create_tables(con,meta,path)
            return redirect(url_for('index'))
    return """
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    <p>%s</p>
    """ % "<br>".join(os.listdir(app.config['UPLOAD_FOLDER'],))

if __name__ == '__main__':
    app.run()