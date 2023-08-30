import os
import mysql.connector
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


@app.route('/', methods=['GET'])
def index():
   print('Request for index page received')
   return render_template('homepage.html')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/hello', methods=['POST'])
def hello():
   name = request.form.get('name')

   if name:
       print('Request for hello page received with name=%s' % name)
       return render_template('hello.html', name = name)
   else:
       print('Request for hello page received with no name or blank name -- redirecting')
       return redirect(url_for('index'))

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
