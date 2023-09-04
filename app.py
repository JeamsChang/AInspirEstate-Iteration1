import os
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for, jsonify,
                   Response)

app = Flask(__name__)

# Set password
PASSWORD = "seamTA07"

@app.before_request
def require_basic_auth():
    auth = request.authorization
    if not auth or auth.password != PASSWORD:
        return Response(
            "Unauthorized", 401,
            {'WWW-Authenticate': 'Basic realm="Login Required"'}
        )

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
    car = db.Column(db.Integer)


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
   properties_info = [(property.latitude, property.longitude, property.rooms, property.bathroom, property.car, property.price) for property in properties]

   return jsonify(properties_info)
   
@app.route('/avg', methods=['POST'])
def avg():
   data = request.json
   suburb = data['suburb']
   avg_bedrooms = db.session.query(db.func.avg(MelbourneHousingData.rooms)).filter(MelbourneHousingData.suburb == suburb).scalar()
   avg_bathrooms = db.session.query(db.func.avg(MelbourneHousingData.bathroom)).filter(MelbourneHousingData.suburb == suburb).scalar()
   avg_price = db.session.query(db.func.avg(MelbourneHousingData.price)).filter(MelbourneHousingData.suburb == suburb).scalar()
   avg_car = db.session.query(db.func.avg(MelbourneHousingData.car)).filter(MelbourneHousingData.suburb == suburb).scalar()
   return jsonify(
      [round(avg_bedrooms), round(avg_bathrooms), round(avg_car), round(avg_price, 2)]
      )

if __name__ == '__main__':
   app.run(debug=True)
