from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.stack import StackModel
from models.service import ServiceModel
from models.blueprint import BlueprintModel
from util.response import response


class ServiceList(Resource):
  """API resource to to display list of saved services."""
  
  @jwt_required()
  def get(self):
    """GET method to retrieve list of saved services."""

    return response(200, "Services have been retrieved.", None, [service.json() for service in ServiceModel.query.all()]), 200


class ServiceCreate(Resource):
  """API resource to create or update services."""  

  parser = reqparse.RequestParser()
  parser.add_argument('name',
                      type = str,
                      required = True,
                      help = "The name of your service is required")
  parser.add_argument('description',
                      type = str,
                      help = "The description is optional.")
  parser.add_argument('blueprint',
                      type = int,
                      required = True,
                      help = "The blueprint id is required.",)
  parser.add_argument('exposed_ports',
                      type = int,
                      action = 'append',
                      help = "The exposed ports are required.")
  parser.add_argument('mapped_ports',
                      type = str,
                      action = 'append',
                      help = "The mapped ports are optional.")
  parser.add_argument('volumes',
                      type = str,
                      action = 'append',
                      help = "The volumes your service needs mounted are option")
  parser.add_argument('env',
                      type= str,
                      action = 'append',
                      help = "Environment variables are optional.")
  parser.add_argument('restart',
                      type = str,
                      help = "The restart flag for this service is optional.")
  parser.add_argument('stacks',
                      type = int,
                      help = "Stacks are optional.")  

  def check_args(self, data):
    """Helper method to check various passed payload arguments

    Args:
      data (:obj:`dict`): Request payload with parsed arguments.
        data['blueprint'] (int): Blueprint ID which service will be derived from.
        data['description'] (string): The service description.
        data['name'] (str): Name of service.
        data['exposed_ports'] (list of int): Ports to be exposed.
        data['mapped_ports'] (list of str): Ports to be mapped between host and container.
        data['volumes'](list of str): Volumes to be mapped between host and container.
        data['env'] (list of str): Environment variables for container.
        data['restart'] (str): The restart flag for the container.
        data['stacks'] (list of int): Stack this service should be a part of.

    Returns:
      dict: If all checks pass, dict of type {'code': 200}. 
        If one check fails, dict of type {'code': <error code>, 'error' <error message>}, where the code and
        message will be directly fed into a response.

    """
    # Check if blueprint exists
    if not BlueprintModel.find_by_id(data['blueprint']):
      return {'code': 400, 'error': f"Blueprint with ID {data['blueprint']} hasn't been found."}

    # Regex check for name
    if not StackModel.valid_name(data['name']):
      return {'code': 400, 'error': f"Invalid service name {data['name']}."}
    
    if data['exposed_ports']:
      # Regex check if passed exposed_ports are correct
      if not ServiceModel.valid_ports(data['exposed_ports']):
        return {'code': 400, 'error': f"Invalid exposed_ports."}

    if data['mapped_ports']:
      # Regex check if mapped_ports are correct, those are passed as string like '80:80,8080:8080'
      if not ServiceModel.valid_mapped_ports(data['mapped_ports']):
        return {'code': 400, 'error': f"Invalid mapped_ports."}

    # Regex check if volumes are correct
    if data['volumes']:
      if not ServiceModel.valid_volumes(data['volumes']):
        return {'code': 400, 'error': f"Invalid volumes"} 

    # Regex check if environment variables are correct
    if data['env']:
      if not ServiceModel.valid_env(data['env']):
        return {'code': 400, 'error': f"Invalid environment variables."}

    # Check if restart flag is part of allowed options:
    if data['restart']:
      if data['restart'].lower() not in ["no", "always"]:
        return {'code': 400, 'error': f"Invalid restart flag."}

    # Check if passed stack exists.
    if data['stacks'] and data['stacks'] != [None]:
      for x in data['stacks']:
        if not StackModel.find_by_id(x):
          return {'code': 400, 'error': f"Stack with ID {x} cannot be found."}   

    return {'code': 200}  

  @jwt_required()
  def post(self):
    """POST method to create a new service."""

    data = self.parser.parse_args()

    if ServiceModel.find_by_name(data['name']):
      return response(400, None, f"Service with name {data['name']} already exists.", None), 400

    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    volumes = ServiceModel.join_volume_string(data)
    env = ServiceModel.join_env_string(data)
    exposed_ports = ServiceModel.join_port_string(data['exposed_ports'])
    mapped_ports = ServiceModel.join_port_string(data['mapped_ports'])

    service = ServiceModel(name = data['name'],
                           blueprint_id = data['blueprint'],
                           description = data['description'],
                           exposed_ports = exposed_ports,
                           mapped_ports = mapped_ports,
                           volumes = volumes,
                           restart = data['restart'],
                           env = env)

    # Add stack to service table
    if data['stacks'] and data['stacks'] != [None]:
      for x in data['stacks']:
        stack = StackModel.find_by_id(x)
        service.stacks.append(stack)

    try:
      service.save_to_db()
      service.ip = service.get_ip(service.id)
      service.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update service {data['name']}.", None), 500

    return response(201, f"Service {data['name']} has been updated.", None, service.json()), 201

  @jwt_required()
  def put(self):
    """PUT method to create or update a service."""    

    data = self.parser.parse_args()

    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    service = ServiceModel.find_by_name(data['name'])

    volumes = ServiceModel.join_volume_string(data)
    env = ServiceModel.join_env_string(data)
    exposed_ports = ServiceModel.join_port_string(data['exposed_ports'])
    mapped_ports = ServiceModel.join_port_string(data['mapped_ports'])
    
    if service:
      service.name = data['name']
      service.description = data['description']
      service.exposed_ports = exposed_ports
      service.mapped_ports = mapped_ports
      service.volumes = volumes
      service.env = env
      service.restart = data['restart']
      service.blueprint_id = data['blueprint']

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
      service = ServiceModel(name = data['name'],
                             description = data['description'],
                             exposed_ports = exposed_ports,
                             mapped_ports = mapped_ports,
                             volumes = volumes,
                             env = env,
                             restart = data['restart'],
                             blueprint_id = data['blueprint'])

      if data['stacks'] and data['stacks'] != [None]:
        for x in data['stacks']:
          stack = StackModel.find_by_id(x)
          service.stacks.append(stack)

    try:
      service.save_to_db()
      service.ip = service.get_ip(service.id)
      service.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update service {data['name']}.", None), 500

    return response(201, f"Service {data['name']} has been updated.", None, service.json()), 201


class Service(Resource):
  """API resource to retrieve or delete a specific service."""  

  @jwt_required()
  def get(self, _id):
    """GET method to retrieve a service by ID."""    

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
    """DELETE method to delete service by ID."""    

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