import os
import mysql.connector
from flask_sqlalchemy import SQLAlchemy
from flask import (Flask, redirect, render_template, request,
                   send_from_directory, url_for)

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
    id = db.Column(db.Integer, primary_key=True)
    suburb = db.Column(db.String)

@app.route('/', methods=['GET'])
def index():
   print('Request for index page received')
   return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/browsing')
def browsing():
   suburbs = suburbs = db.session.query(MelbourneHousingData.suburb).distinct().order_by(MelbourneHousingData.suburb).all()
   print(suburbs)
   return render_template('browsing.html', suburbs=suburbs)

@app.route('/test')
def test():
   print('Request for test page received')
   conn = mysql.connector.connect(**DATABASE_CONFIG)
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM melbourne_housing_data")
   results = cursor.fetchall()
   cursor.close()
   conn.close()
   print(results)
   return render_template('test.html', results=results)

if __name__ == '__main__':
   app.run(debug=True)
