from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from datetime import datetime
from os import path, makedirs

from models.blueprint import BlueprintModel
from models.service import ServiceModel
from models.stack import StackModel
from util.response import response
from util.compose import get_compose, create_compose


class StackList(Resource):
  """API resource to to display list of saved stacks."""

  @jwt_required()
  def get(self):
    """GET method to retrieve list of saved stacks."""

    return response(200, "Stacks have been retrieved.", None, [stack.json() for stack in StackModel.query.all()]), 200


class StackCreate(Resource):
  """API resource to create or update stacks.

  The passed subdomain will be checked with regex if it's valid.

  """

  parser = reqparse.RequestParser()
  parser.add_argument('name',
    type = str,
    required = True,
    help = "The name of the stack is required.")
  parser.add_argument('description',
    type = str,
    help = "The description of the stack.")
  parser.add_argument('subdomain',
    type = str,
    help = "The subdomain this stack should reside under.")
  parser.add_argument('services',
    type = int,
    action = 'append',
    help = "Service IDs are optional.")

  def check_args(self, data):
    """Helper method to check various passed payload arguments

    Args:
      data (:obj:`dict`): Request payload with parsed arguments.
        data['name'] (str): Name of the stack.
        data['description'] (str): Description for the stack.
        data['subdomain'] (str): Subdomain of the stack.

    Returns:
      dict: If all checks pass, dict of type {'code': 200}. 
        If one check fails, dict of type {'code': <error code>, 'error' <error message>}, where the code and
        message will be directly fed into a response.

    """    
    # Regex check for subdomain
    if data['subdomain'] and not StackModel.valid_subdomain(data['subdomain']):
      return {'code': 400, 'error': f"Invalid subdomain {data['subdomain']}"}

    # Regex check for name
    if not StackModel.valid_name(data['name']):
      return {'code': 400, 'error': f"Invalid stack name {data['name']}."}

    return {'code': 200}

  @jwt_required()
  def post(self):
    """POST method to create a new service."""

    data = self.parser.parse_args()

    if StackModel.find_by_name(data['name']):
      return response(400, None, f"Stack with name {data['name']} already exists.", None), 400

    # Argument check
    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    stack = StackModel(name = data['name'],
                       description = data['description'],
                       subdomain = data['subdomain'])

    if data['services'] and data['services'] != [None]:
      for x in data['services']:
          service = ServiceModel.find_by_id(x)
          if service:
            stack.services.append(service)
          else:
            return response(400, None, f"Service with ID {x} cannot be found.", None), 400

    try:
      stack.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update stack {data['name']}.", None), 500

    return response(201, f"Stack {data['name']} has been updated.", None, stack.json()), 201

  @jwt_required()
  def put(self):
    """PUT method to create or update a service."""

    data = self.parser.parse_args()

    # Argument check
    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    stack = StackModel.find_by_name(data['name'])

    if stack:
      stack.name = data['name']
      stack.description = data['description']
      stack.subdomain = data['subdomain']
      stack.last_changed = datetime.now()

      
      if data['services'] and data['services'] != [None]:
        print(data['services'])
        # Get sets of services which need to be updated and deleted
        old = {x.id for x in stack.services}
        new = set(data['services'])
        to_update = new - old
        to_delete = old - new
        
        # Remove old services
        for x in to_delete:
          stack.services.remove(ServiceModel.find_by_id(x))

        # Add new services
        for x in to_update:
          service = ServiceModel.find_by_id(x)
          if service:
            stack.services.append(service)
          else:
            return response(400, None, f"Service with ID {x} cannot be found.", None), 400
      else:
        for x in [y.id for y in stack.services]:
          stack.services.remove(ServiceModel.find_by_id(x))

    else:
      stack = StackModel(name = data['name'],
                         description = data['description'],
                         subdomain = data['subdomain'])

      if data['services'] and data['services'] != [None]:
        for x in data['services']:
          service = ServiceModel.find_by_id(x)
          if service:
            stack.services.append(service)
          else:
            return response(400, None, f"Service with ID {x} cannot be found.", None), 400

    try:
      stack.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update stack {data['name']}.", None), 500

    return response(201, f"Stack {data['name']} has been updated.", None, stack.json()), 201


class Stack(Resource):
  """API resource to retrieve or delete a specific stack."""

  @jwt_required()
  def get(sef, _id):
    """GET method to retrieve a stack by ID."""

    try:
      stack = StackModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to retrieve stack {stack.name}.", None), 500
    if stack:
      return response(200, f"Stack {stack.name} has been retrieved.", None, stack.json()), 200

    return response(404, None, f"Stack with id {_id} does not exist.", None), 404

  @jwt_required()
  def delete(self, _id):
    """DELETE method to delete a stack by ID."""

    try:
      stack = StackModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to save stack {stack.name}.", None), 500

    if stack:
      try:
        stack.delete_from_db()
      except:
        return response(500, None, f"An error occured while trying to delete stack {stack.name}.", None), 500
        
      return response(200, f"Stack {stack.name} has been deleted.", None, None), 200

    return response(404, None, f"Stack with id {_id} does not exist.", None), 404


class StackApply(Resource):
  """API resource to create or update the stack's project files

  Attributes:
    stacks_folder (str): The location of where to save the project files.

  """

  stacks_folder = "../../stacks"

  def get_compose_data(self, services):
    """Helper method to pass the necessary data to the function creating the string which ends up as the 
      docker-compose.yml.

    Args:
      services (:obj:`list` of :obj:`service`): A list with the services this stack is defined for.

    Returns:
      dict: A dictionary with the necessary information, None if exception is thrown.

    """

    data = []
    try:
      for service in services:
        tmp = {}

        tmp['name'] = service.name
        tmp['image'] = BlueprintModel.find_by_id(service.blueprint_id).image
        tmp['exposed_ports'] = ServiceModel.port_list(service.exposed_ports)
        tmp['ip'] = service.ip

        if service.volumes:
          tmp['volumes'] = ServiceModel.split_string(service.volumes)

        if service.env:
          tmp['environment'] = ServiceModel.split_string(service.env)

        if service.mapped_ports:
          tmp['mapped_ports'] = [x for x in service.mapped_ports.split(',')]

        data.append(tmp)

    except:
      return None

    return data

  @jwt_required()
  def post(self, _id):
    """POST method to save the project files to the file system."""

    if not StackModel.find_by_id(_id):
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404

    stack = StackModel.find_by_id(_id)
    project_folder = self.stacks_folder + f"/{stack.name}"
    compose_file = project_folder + "/docker-compose.yml"

    if not path.exists(project_folder):
      makedirs(project_folder)

    data = self.get_compose_data(stack.services)

    if data:
      compose_string = get_compose(data)

      if create_compose(compose_file, compose_string):
        return response(200, f"Stack {stack.name} has been applied.", None, None), 200
      else:
        return response(500, None, f"An error has occured while trying to save compose file.", None), 500

    else:
      return response(500, None, f"An error has occured while trying to assemble data for compose file"), 500




