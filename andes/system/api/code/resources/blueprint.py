from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.blueprint import BlueprintModel
from util.response import response

class BlueprintList(Resource):
  @jwt_required()
  def get(self):
    return response(200, "Blueprints have been retrieved.", None, [blueprint.json() for blueprint in BlueprintModel.query.all()]), 200