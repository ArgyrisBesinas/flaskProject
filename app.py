from flask import Flask
from routes import define_routes
from utility.database import init_db
from dotenv import load_dotenv

load_dotenv()  # load the .env file programmatically

app = Flask(__name__)

# print('os.environ')
# print(os.environ['MYSQL_URL'])

define_routes(app)
init_db()

if __name__ == '__main__':
    app.run()
