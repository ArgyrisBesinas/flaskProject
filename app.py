from flask import Flask
from routes import define_routes
from database import init_db

import os

app = Flask(__name__)

# print('os.environ')
# print(os.environ['MYSQL_URL'])

define_routes(app)
init_db()

if __name__ == '__main__':
    app.run()
