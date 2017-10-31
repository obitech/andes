from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.service import ServiceModel

class ServiceList(Resource):
  @jwt_required()
  def get(self):
    return {
      'services': [service.json() for service in ServiceModel.query.all()]
    }

class ServiceCreate(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
    type=str,
    required=True,
    help="The name of your service (required)."
  )
  parser.add_argument('image',
    type=str,
    required=True,
    help="The image name is required.",
  )
  # TODO: Fix this as list
  parser.add_argument('exposed_ports',
    type=str,
    required=True,
    help="The exposed ports are required."
  )
  parser.add_argument('volumes',
    type=str,
    help="The volumes your service needs mounted."
  )

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()

    if ServiceModel.find_by_name(data['name']):
      return {
        'message': f"Service with name {data['name']} already exists."
      }, 400

    if not ServiceModel.valid_ports(data['exposed_ports']):
      return {
        'message': "Invalid exposed_ports.", 
        'exposed_ports': data['exposed_ports']
      }, 400

    if not ServiceModel.valid_volumes(data['volumes']):
      return {
        'message': "Invalid volumes.", 
        'volumes': data['volumes']
      }, 400

    service = ServiceModel(**data)

    try:
      service.save_to_db()
    except:
      return {
        'error': f"An error occured while trying to save new service."
      }, 500

    return service.json(), 201

  @jwt_required()
  def put(self):
    data = self.parser.parse_args()
    service = ServiceModel.find_by_name(data['name'])

    if not ServiceModel.valid_ports(data['exposed_ports']):
      return {
        'message': "Invalid exposed_ports."
      }, 400

    if not ServiceModel.valid_volumes(data['volumes']):
      return {
        'message': "Invalid volumes."
      }, 400

    if service:
      service.name = data['name']
      service.image = data['image']
      service.exposed_ports = data['exposed_ports']
      service.volumes = data['volumes']
    else:
      service = ServiceModel(**data)

    try:
      service.save_to_db()
    except:
      return {
        'error': f"An error occured while trying to save new service."
      }, 500

    return service.json(), 201

class Service(Resource):
  pass