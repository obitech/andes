from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
#app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.secret_key = "superSecretKey"

#@app.before_first_request
#def create_tables():
#  db.create_all()

api = Api(app)

if __name__ == "__main__":
  #from db import db
  #db.init_app(app)
  app.run(port=5000, debug=True)