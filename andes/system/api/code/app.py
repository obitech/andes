from flask import Flask
from flask_restful import Resource, Api
from flask_jwt import JWT
from datetime import timedelta

from security import authenticate, identity
from resources.user import UserRegister
from resources.blueprint import BlueprintList, BlueprintCreate, Blueprint
from resources.service import ServiceList, ServiceCreate, Service
from resources.stack import StackList, StackCreate, Stack, StackApply, StackUp, StackDown, StackStatus, StackLogs, StackRemove


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../data/data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=3000)
app.secret_key = "DEVELOPMENT_KEY"
api = Api(app)
jwt = JWT(app, authenticate, identity)

api.add_resource(UserRegister, '/register')

api.add_resource(BlueprintList, '/blueprints')
api.add_resource(BlueprintCreate, '/blueprints/create')
api.add_resource(Blueprint, '/blueprints/<int:_id>')

api.add_resource(ServiceList, '/services')
api.add_resource(ServiceCreate, '/services/create')
api.add_resource(Service, '/services/<int:_id>')

api.add_resource(StackList, '/stacks')
api.add_resource(StackCreate, '/stacks/create')
api.add_resource(Stack, '/stacks/<int:_id>')
api.add_resource(StackApply, '/stacks/<int:_id>/apply')

api.add_resource(StackUp, '/stacks/<int:_id>/manage/up')
api.add_resource(StackDown, '/stacks/<int:_id>/manage/down')
api.add_resource(StackStatus, '/stacks/<int:_id>/manage/status')
api.add_resource(StackLogs, '/stacks/<int:_id>/manage/logs')
api.add_resource(StackRemove, '/stacks/<int:_id>/manage/remove')

if __name__ == "__main__":
  from db import db
  db.init_app(app)
  app.run(host='127.0.0.1', port=5000, debug=True)
