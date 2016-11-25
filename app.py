import os
import json
import pandas as pd
from flask import (Flask, request, abort, make_response, redirect, url_for, 
                   jsonify)
from werkzeug import secure_filename

from sqlalchemy import create_engine, func, MetaData
from sqlalchemy.sql import and_, or_
from sqlalchemy.orm import sessionmaker
from models import create_tables

def connect(user, password, db, host='localhost', port=5432):
    '''Returns a connection and a metadata object
    We connect with the help of the PostgreSQL URL
    postgresql://karan:karan@localhost:5432/supplyai
    '''

    url = 'postgresql://{}:{}@{}:{}/{}'
    url = url.format(user, password, host, port, db)
    # con is a connection object
    con = create_engine(url, client_encoding='utf8')
    # meta is a MetaData object which is binded to con
    meta = MetaData(bind=con, reflect=True)

    return con, meta
# Establish connection with postgres
con, meta = connect('karan', 'karan', 'supplyai')
Session = sessionmaker(bind=con)
session = Session()

cwd = os.getcwd()
UPLOAD_FOLDER = cwd + '/upload/'
ALLOWED_EXTENSIONS = set(['csv'])
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/')
def hello():
    return jsonify('Success') , 200


@app.route('/query', methods=['GET','POST'])
def query():

    result = meta.tables['result']
    args = (request.args)
    conditions = []
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

    return jsonify({'Shipper Name':data})


@app.route('/count', methods=['GET'])
def count():
    result = meta.tables['result']
    if request.args.get('shipper_name') is None:
        abort(404)
    shipper_name = request.args.get('shipper_name')
    names = session.query(result.c.order_created_date, \
                      func.count(result.c.order_created_date)).filter(\
                      result.c.shipper_name== shipper_name).group_by(\
                      result.c.order_created_date).all()
    return jsonify({'Shipper Name': names})

@app.route("/fetch", methods=['GET'])
def fetch():

    if request.args.get('n') is None:
        abort(404)
    l  = list(map(int,request.args.get('n').split("-")))
    '''
    Case where n=single update
    Zero-indexing is taken care of.
    
    /fetch?n=1 should mean that row 0 is inserted. lowerLimit = 0, Upper = 1
    in case of l=[1], l[1] will throw an index error.
    upper_limit is L[0] which is 1.
    lower_limit is L[0] = which is l[0]-1 = 0
    so df.iloc[0:1] 

    for /fetch?n=3-10, lower_limit=3, upper_limit= 11
    so df.iloc[3:11]
    '''
    if len(l)>1:
        upper_limit = l[1]+1
        lower_limit = l[0]
    else:
        upper_limit = l[0]
        lower_limit = l[0] - 1
    filename ='data.csv'
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    print(lower_limit)
    print(upper_limit)
    api_result = create_tables(con,meta,session,path,lower_limit,upper_limit)
    return jsonify({'data':api_result})
    

@app.route("/upload", methods=['GET','POST'])
def create_data():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            if not os.path.exists(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('create_data'))
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
    app.run(debug=True)