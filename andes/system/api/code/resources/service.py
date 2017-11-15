from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.stack import StackModel
from models.service import ServiceModel
from util.response import response

class ServiceList(Resource):
  @jwt_required()
  def get(self):
    return response(200, "Services have been retrieved.", None, [service.json() for service in ServiceModel.query.all()]), 200


class ServiceCreate(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
    type = str,
    required = True,
    help = "The name of your service is required")
  parser.add_argument('image',
    type = str,
    required = True,
    help = "The image name is required.",)
  # TODO: pass ports as int
  parser.add_argument('exposed_ports',
    type = int,
    required = True,
    action = 'append',
    help = "The exposed ports are required.")
  parser.add_argument('volumes',
    type = str,
    action = 'append',
    help = "The volumes your service needs mounted are option")
  parser.add_argument('env',
    type= str,
    action= 'append',
    help = "Environment variables are optional.")
  parser.add_argument('stacks',
    type = int,
    action = 'append',
    help = "Stacks are optional.")  

  def check_args(self, data):
    if data['volumes']:
      if not ServiceModel.valid_volumes(data['volumes']):
        return {'code': 400, 'error': f"Invalid volumes"}

    if data['exposed_ports']:
      if not ServiceModel.valid_ports(data['exposed_ports']):
        return {'code': 400, 'error': f"Invalid exposed_ports."}    

    if data['env']:
      if not ServiceModel.valid_env(data['env']):
        return {'code': 400, 'error': f"Invalid environment variables."}

    if data['stacks'] and data['stacks'] != [None]:
      for x in data['stacks']:
        if not StackModel.find_by_id(x):
          return {'code': 400, 'error': f"Stack with ID {x} cannot be found."}   

    return {'code': 200}  

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()

    if ServiceModel.find_by_name(data['name']):
      return response(400, None, f"Service with name {data['name']} already exists.", None), 400

    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    volumes = ServiceModel.join_volume_string(data)
    env = ServiceModel.join_env_string(data)

    service = ServiceModel(data['name'],
      data['image'],
      ServiceModel.join_port_string(data['exposed_ports']),
      volumes,
      env)

    if data['stacks'] and data['stacks'] != [None]:
      for x in data['stacks']:
        stack = StackModel.find_by_id(x)
        service.stacks.append(stack)

    try:
      service.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update service {data['name']}.", None), 500

    return response(201, f"Service {data['name']} has been updated.", None, service.json()), 201

  @jwt_required()
  def put(self):
    data = self.parser.parse_args()

    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    service = ServiceModel.find_by_name(data['name'])

    volumes = ServiceModel.join_volume_string(data)
    env = ServiceModel.join_env_string(data)
    
    if service:
      service.name = data['name']
      service.image = data['image']
      service.exposed_ports = ServiceModel.join_port_string(data['exposed_ports'])
      service.volumes = volumes
      service.env = env

      if data['stacks'] and data['stacks'] != [None]:
        # Get sets of stacks which need to be updated or deleted
        old = {x.id for x in service.stacks}
        new = set(data['stacks'])
        to_update = new - old
        to_delete = old - new

        # Remove old stacks
        for x in to_delete:
          service.stacks.remove(StackModel.find_by_id(x))

        # Add new services
        for x in to_update:
          service.stacks.append(StackModel.find_by_id(x))
      else:
        for x in [y.id for y in service.stacks]:
          service.stacks.remove(StackModel.find_by_id(x))

    else:
      service = ServiceModel(data['name'],
                             data['image'],
                             ServiceModel.join_port_string(data['exposed_ports']),
                             volumes,
                             env)

      if data['stacks'] and data['stacks'] != [None]:
        for x in data['stacks']:
          stack = StackModel.find_by_id(x)
          service.stacks.append(stack)

    try:
      service.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update service {data['name']}.", None), 500

    return response(201, f"Service {data['name']} has been updated.", None, service.json()), 201


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
      return response(201, f"Service {service.name} has been retrieved.", None, service.json()), 201

    return {
      'error': f"Service with ID {_id} does not exist."
    }, 400

  @jwt_required()
  def delete(self, _id):
    try:
      service = ServiceModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to delete service {service.name}.", None), 500

    if service:
      try:
        service.delete_from_db()
      except:
        return response(500, None, f"An error occured while trying delete service {data['name']}.", None), 500
      return response(200, f"Service {service.name} has been deleted.", None, None), 200

    return response(404, None, f"Service with id {_id} does not exist.", None), 404