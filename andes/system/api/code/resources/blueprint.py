from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.blueprint import BlueprintModel
from util.response import response

class BlueprintList(Resource):
  @jwt_required()
  def get(self):
    return response(200, "Blueprints have been retrieved.", None, [blueprint.json() for blueprint in BlueprintModel.query.all()]), 200


class BlueprintCreate(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
                      type = str,
                      required = True,
                      help = "The name of the blueprint is required.")
  parser.add_argument('description',
                      type = str,
                      help = "The description of the blueprint is optional.")
  parser.add_argument('image',
                      type = str,
                      required = True,
                      help = "The image of the blueprint is required.")
  parser.add_argument('exposed_ports',
                      type = int,
                      action = 'append',
                      required = True,
                      help = "The exposed ports are required.")

  def check_args(self, data):
    if data['exposed_ports']:
      if not BlueprintModel.valid_ports(data['exposed_ports']):
        return {'code': 400, 'error': f"Invalid exposed_ports."}

    return {'code': 200}

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()

    if BlueprintModel.find_by_image(data['image']):
      return response(400, None, f"Blueprint with image {data['image']} already exists.", None), 400

    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    blueprint = BlueprintModel(name = data['name'],
                               description = data['description'],
                               image = data['image'],
                               exposed_ports = BlueprintModel.join_port_string(data['exposed_ports']))

    try:
      blueprint.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update blueprint {data['name']}.", None), 500

    return response(201, f"Blueprint {data['name']} has been updated.", None, blueprint.json()), 201

  @jwt_required()
  def put(self):
    data = self.parser.parse_args()

    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    blueprint = BlueprintModel.find_by_image(data['image'])
    if blueprint:
      blueprint.name = data['name']
      blueprint.image = data['image']
      blueprint.description = data['description']
      blueprint.exposed_ports = BlueprintModel.join_port_string(data['exposed_ports'])
    else:
      blueprint = BlueprintModel(name = data['name'],
                                 description = data['description'],
                                 image = data['image'],
                                 exposed_ports = BlueprintModel.join_port_string(data['exposed_ports']))

    try:
      blueprint.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update blueprint {data['name']}.", None), 500

    return response(201, f"Blueprint {data['name']} has been updated.", None, blueprint.json()), 201


class Blueprint(Resource):
  @jwt_required()
  def get(self, _id):
    try:
      blueprint = BlueprintModel.find_by_id(_id)
    except:
      return {
        'error': f"An error occured while trying to retrieve blueprint."
      }, 500

    if blueprint:
      return response(201, f"Blueprint {blueprint.name} has been retrieved.", None, blueprint.json()), 201

    return {
      'error': f"Blueprint with ID {_id} does not exist."
    }, 400

  @jwt_required()
  def delete(self, _id):
    try:
      blueprint = BlueprintModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to delete blueprint {blueprint.name}.", None), 500

    if blueprint:
      try:
        blueprint.delete_from_db()
      except:
        return response(500, None, f"An error occured while trying delete blueprint {data['name']}.", None), 500
      return response(200, f"Blueprint {blueprint.name} has been deleted.", None, None), 200

    return response(404, None, f"Blueprint with id {_id} does not exist.", None), 404
