from flask import Flask
from flask_restful import Resource, Api
from flask_jwt import JWT
from datetime import timedelta

from security import authenticate, identity

from resources.user import UserRegister
from resources.service import ServiceList, ServiceCreate, Service
from resources.stack import StackList, StackCreate, Stack
from resources.network import NetworkList, NetworkCreate, Network


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=3000)
app.secret_key = "DEVELOPMENT_KEY"
api = Api(app)
jwt = JWT(app, authenticate, identity)

@app.before_first_request
def create_tables():
  db.create_all()

api.add_resource(UserRegister, '/register')

api.add_resource(ServiceList, '/services')
api.add_resource(ServiceCreate, '/service/create')
api.add_resource(Service, '/service/<int:_id>')

api.add_resource(StackList, '/stacks')
api.add_resource(StackCreate, '/stack/create')
api.add_resource(Stack, '/stack/<int:_id>')

api.add_resource(NetworkList, '/networks')
#api.add_resource(NetworkCreate, '/network/create')
#api.add_resource(Network, '/network/<int:_id')

if __name__ == "__main__":
  from db import db
  db.init_app(app)
  app.run(port=5000, debug=True)