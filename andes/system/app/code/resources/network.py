from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.network import NetworkModel

class NetworkList(Resource):
  @jwt_required()
  def get(self):
    return {
      'networks': [network.json() for network in NetworkModel.query.all()]
    }

class NetworkCreate(Resource):
  @jwt_required()
  def put(self):
    pass

  @jwt_required()
  def post(self):
    pass

class Network(Resource):
  @jwt_required()
  def get(self, _id):
    pass

  @jwt_required()
  def delete(self, _id):
    pass