import os
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify)

app = Flask(__name__)

# Azure Database for MySQL connection string
DATABASE_CONFIG = {
    'host': 'seam-server.mysql.database.azure.com',
    'user': 'ainspireestate',
    'password': 'seamTA07',
    'database': 'housing'
}

# MySQL connection string
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://ainspireestate:seamTA07@seam-server.mysql.database.azure.com:3306/housing"
db = SQLAlchemy(app)

# SQLAlchemy ORM definition for Melbourne Housing Data
class MelbourneHousingData(db.Model):
    __tablename__ = "melbourne_housing_data"
    my_row_id = db.Column(db.Integer, primary_key=True)
    suburb = db.Column(db.String)
    rooms = db.Column(db.Integer)
    bathroom = db.Column(db.Integer)
    price = db.Column(db.Double)
    latitude = db.Column(db.Double)
    longitude = db.Column(db.Double)


@app.route('/', methods=['GET'])
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/browsing', methods=['GET'])
def browsing():
   print('Request for browsing page received')
   
   # Get all suburbs from database
   suburbs = db.session.query(MelbourneHousingData.suburb).distinct().order_by(MelbourneHousingData.suburb).all()
   
   # Get max number of rooms from database
   max_rooms = db.session.query(db.func.max(MelbourneHousingData.rooms)).scalar()
   
   # Get max number of bathrooms from database
   max_bathroom = db.session.query(db.func.max(MelbourneHousingData.bathroom)).scalar()
   
   # Get max price of properties from database
   max_price = db.session.query(db.func.max(MelbourneHousingData.price)).scalar()
   
   # Get min price of properties from database
   min_price = db.session.query(db.func.min(MelbourneHousingData.price)).scalar()
   
   # Get latitude and longitude of properties from the database
   coordinates = db.session.query(MelbourneHousingData.latitude, MelbourneHousingData.longitude).all()
   return render_template('browsing.html', 
                          suburbs=suburbs, 
                           max_rooms=max_rooms, 
                           max_price=max_price, 
                           max_bathroom=max_bathroom, 
                           min_price=min_price, 
                           coordinates=coordinates)

@app.route('/browsing_post', methods=['POST'])
def browsing_post():
   # accept the request data from the client
   data = request.json
   suburb = data['suburb']
   bedrooms = data['bedrooms']
   bathrooms = data['bathrooms']
   maxPrice = data['maxPrice']

   # search the database for properties that match the search criteria
   properties = db.session.query(MelbourneHousingData).filter(MelbourneHousingData.suburb == suburb, 
                                                               MelbourneHousingData.rooms == bedrooms, 
                                                               MelbourneHousingData.bathroom == bathrooms, 
                                                               MelbourneHousingData.price <= maxPrice).all()
   
   # get the coordinates of the properties
   coordinates = [(property.latitude, property.longitude) for property in properties]

   return jsonify(coordinates)
   
@app.route('/test')
def test():
   print('Request for test page received')
   conn = mysql.connector.connect(**DATABASE_CONFIG)
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM melbourne_housing_data")
   results = cursor.fetchall()
   cursor.close()
   conn.close()
   return render_template('test.html', results=results)

if __name__ == '__main__':
   app.run(debug=True)
