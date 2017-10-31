from flask import Flask
from flask_restful import Resource, Api
from flask_jwt import JWT

from security import authenticate, identity

from resources.user import UserRegister
from resources.service import Service, ServiceCreate, ServiceList


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "DEVELOPMENT_KEY"
api = Api(app)
jwt = JWT(app, authenticate, identity)

@app.before_first_request
def create_tables():
  db.create_all()

api.add_resource(UserRegister, '/register')
api.add_resource(ServiceCreate, '/service/create')
api.add_resource(ServiceList, '/services')

if __name__ == "__main__":
  from db import db
  db.init_app(app)
  app.run(port=5000, debug=True)