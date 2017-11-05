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
    type = str,
    required = True,
    help = "The name of your service (required)."
  )
  parser.add_argument('image',
    type = str,
    required = True,
    help = "The image name is required.",
  )
  parser.add_argument('exposed_ports',
    type = str,
    required = True,
    action = 'append',
    help = "The exposed ports are required."
  )
  parser.add_argument('volumes',
    type = str,
    action = 'append',
    help = "The volumes your service needs mounted."
  )

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()
    if not data['volumes']:
      data['volumes'] = ""

    if ServiceModel.find_by_name(data['name']):
      return {
        'message': f"Service with name {data['name']} already exists."
      }, 400

    if not ServiceModel.valid_volumes(data['volumes']) or not ServiceModel.valid_ports(data['exposed_ports']):
      return {
        'message': "Invalid arguments."
      }, 400

    service = ServiceModel(data['name'],
      data['image'],
      ",".join(data['exposed_ports']),
      ",".join(data['volumes'])
    )

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
    if not data['volumes']:
      data['volumes'] = ""

    if not ServiceModel.valid_volumes(data['volumes']) or not ServiceModel.valid_ports(data['exposed_ports']):
      return {
        'message': "Invalid arguments."
      }, 400

    service = ServiceModel.find_by_name(data['name'])

    if service:
      service.name = data['name']
      service.image = data['image']
      service.exposed_ports = ",".join(data['exposed_ports'])
      service.volumes = ",".join(data['volumes'])
    else:
      service = ServiceModel(data['name'],
        data['image'],
        ",".join(data['exposed_ports']),
        ",".join(data['volumes'])
      )

    try:
      service.save_to_db()
    except:
      return {
        'error': f"An error occured while trying to save new service."
      }, 500

    return service.json(), 201

class Service(Resource):
  @jwt_required()
  def get(self, _id):
    try:
      service = ServiceModel.find_by_id(_id)
    except:
      return {
        'error': f"An error occured while trying to retrieve service."
      }, 500

    if service:
      return service.json()

    return {
      'message': f"Service with ID {_id} does not exist."
    }

  @jwt_required()
  def delete(self, _id):
    try:
      service = ServiceModel.find_by_id(_id)
    except:
      return {
        'error': f"An error occured while trying to retrieve service."
      }, 500

    if service:
      service.delete_from_db()
      return {
        'message': f"Item with id {_id} has been deleted."
      }

    return {
      'message': f"Service with ID {_id} does not exist."
    }