import os
import json
from flask import Flask, request, redirect, url_for, jsonify
from werkzeug import secure_filename

import sqlalchemy
from models import create_tables
from sqlalchemy.sql import and_
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
Session = sessionmaker(bind=con)
session = Session()
cwd = os.getcwd()
UPLOAD_FOLDER = cwd + '/upload/'
ALLOWED_EXTENSIONS = set(['csv'])
app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
print(os.environ['APP_SETTINGS'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/')
def hello():
    return "Hello World!"

@app.route('/query', methods=['GET'])
def query():
    result = meta.tables['result']
    args = (request.args)
    conditions = []
    if request.args.get('order_id') is not None:
        conditions.append(result.c.order_id == args['order_id'])
    if request.args.get('seller_city') is not None:
        conditions.append(result.c.seller_city == args['seller_city'])
    if request.args.get('buyer_city') is not None:
        conditions.append(result.c.buyer_city == args['buyer_city'])
    if request.args.get('product_category') is not None:
        conditions.append(result.c.product_category == args['product_category'])

    clause = result.select().where(and_(*conditions))
    data = {}
    for row in con.execute(clause):
        data.setdefault("Shipper Name",[]).append(row['shipper_name'])

    return jsonify(data)

@app.route('/count', methods=['GET'])
def count():
    result = meta.tables['result']
    shipper_name = request.args.get('shipper_name')
    m = session.query(result.c.order_created_date, func.count(result.c.order_created_date)).filter(result.c.shipper_name== shipper_name).group_by(result.c.order_created_date).all()
    return jsonify(m)



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
            create_tables(con,meta,path)
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