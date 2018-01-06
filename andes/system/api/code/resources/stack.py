from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from datetime import datetime
from os import path, makedirs, remove
from shutil import rmtree
from traceback import print_exc
import subprocess

from models.blueprint import BlueprintModel
from models.service import ServiceModel
from models.stack import StackModel
from util.response import response, container_data
from util.confgen import get_compose, create_file, get_compose_data, get_caddyconf
from util.managedocker import get_container, container_is_up


class StackList(Resource):
  """API resource to to display list of saved stacks."""

  @jwt_required()
  def get(self):
    """GET method to retrieve list of saved stacks."""

    return response(200, "Stacks have been retrieved.", None, [stack.json() for stack in StackModel.query.all()]), 200


class StackCreate(Resource):
  """API resource to create or update stacks."""

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
  parser.add_argument('email',
                      type = str,
                      help = "The email for TLS certificate generation is optional.")
  parser.add_argument('proxy_port',
                      type = int,
                      help = "The proxy_port so Caddy can forward requests to the service.")
  parser.add_argument('proxy_service',
                      type = int,
                      help = "The proxy_service for Caddy to forward requests to")

  def check_args(self, data):
    """Helper method to check various passed payload arguments

    Note:
      This does not check if the proxy_port is part of the published ports ports

    Args:
      data (:obj:`dict`): Request payload with parsed arguments. Arguments to be checked:
        data['name'] (str): Name of the stack.
        data['description'] (str): Description for the stack.
        data['subdomain'] (str): Subdomain of the stack.
        data['email'] (str): The email needed for Caddy to grab a TLS certificate.
        data['proxy_port'] (int): The main port Caddy will forward requests to for this stack.

    Returns:
      dict: If all checks pass, dict of type {'code': 200}. 
        If one check fails, dict of type {'code': <error code>, 'error' <error message>}, where the code and
        message will be directly fed into a response.

    """ 

    # Regex check for valid name
    if not StackModel.valid_name(data['name']):
      return {'code': 400, 'error': f"Invalid stack name {data['name']}."}

    # Regex check for valid proxy_port
    if data['proxy_port'] and not ServiceModel.valid_ports([data['proxy_port']]):
      return {'code': 400, 'error': f"Invalid proxy_port {data['proxy_port']}"}

    # Regex check for valid subdomain
    if data['subdomain'] and not StackModel.valid_subdomain(data['subdomain']):
      return {'code': 400, 'error': f"Invalid subdomain {data['subdomain']}."}

    # Regex check for valid email
    if data['email'] and not StackModel.valid_email(data['email']):
      return {'code': 400, 'error': f"Email {data['email']} is invalid."}

    return {'code': 200}

  @jwt_required()
  def post(self):
    """POST method to create a new stack."""

    data = self.parser.parse_args()

    if StackModel.find_by_name(data['name']):
      return response(400, None, f"Stack with name {data['name']} already exists.", None), 400

    # Argument check
    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    stack = StackModel(name = data['name'],
                       description = data['description'],
                       subdomain = data['subdomain'] if data['subdomain'] else 'localhost',
                       email = data['email'],
                       proxy_port = data['proxy_port'])

    if data['services'] and data['services'] != [None]:
      for x in data['services']:
          service = ServiceModel.find_by_id(x)
          if service:
            stack.services.append(service)
          else:
            return response(400, None, f"Service with ID {x} cannot be found.", None), 400

    # Check if proxy_serve is part of stack.services
    if data['proxy_service']:
      try:
        if data['proxy_service'] not in [x.id for x in stack.services]:
          return response(400, None, f"Service with ID {data['proxy_service']} is not part of Stack {stack.name}'s services.", None), 400
        else:
          stack.proxy_service = data['proxy_service']
      except:
        print_exc()
        return response(500, None, f"An internal error occured while checking the proxy_service.", None), 500

    try:
      stack.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update stack {data['name']}.", None), 500

    return response(201, f"Stack {data['name']} has been updated.", None, stack.json()), 201

  @jwt_required()
  def put(self):
    """PUT method to create or update a stack."""

    data = self.parser.parse_args()

    # Argument check
    args = self.check_args(data)
    if args['code'] is not 200:
      return response(args['code'], None, args['error'], None), args['code']

    stack = StackModel.find_by_name(data['name'])



    if stack:
      stack.name = data['name']
      stack.description = data['description']
      stack.subdomain = data['subdomain'] if data['subdomain'] else 'localhost',
      stack.email = data['email']
      stack.proxy_port = data['proxy_port']
      stack.proxy_service = data['proxy_service']
      stack.last_changed = datetime.now()

      # Update m:n-Table for stacks:services
      if data['services'] and data['services'] != [None]:
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
                         subdomain = data['subdomain'] if data['subdomain'] else 'localhost',
                         email = data['email'],
                         proxy_port = data['proxy_port'])

      if data['services'] and data['services'] != [None]:
        for x in data['services']:
          service = ServiceModel.find_by_id(x)
          if service:
            stack.services.append(service)
          else:
            return response(400, None, f"Service with ID {x} cannot be found.", None), 400
    
    # Check if proxy_service is part of stack.services
    if data['proxy_service']:
      try:
        if data['proxy_service'] not in [x.id for x in stack.services]:
          return response(400, None, f"Service with ID {data['proxy_service']} is not part of Stack {stack.name}'s services.", None), 400
        else:
          pass
      except:
        print_exc()
        return response(500, None, f"An internal error occured while checking the proxy_service.", None), 500

    try:
      stack.save_to_db()
    except:
      print_exc()
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
      print_exc()
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

    # Check if services are running first
    for service in stack.services:
      if container_is_up(f"{stack.name}_{service.name}"):
        return response(400, None, f"Stack {stack.name} has services running or in exited status. Please remove them first.", None), 400

    if stack:
      try:
        stack.delete_from_db()
      except:
        print_exc()
        return response(500, None, f"An error occured while trying to delete stack {stack.name}.", None), 500
        
      return response(200, f"Stack {stack.name} has been deleted.", None, None), 200

    return response(404, None, f"Stack with id {_id} does not exist.", None), 404


class StackApply(Resource):
  """API resource to create or update the stack's project files."""

  @jwt_required()
  def post(self, _id):
    """POST method to save the project files to the file system."""

    if not StackModel.find_by_id(_id):
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404

    stack = StackModel.find_by_id(_id)

    if not stack.proxy_service:
      return response(400, None, f"Stack {stack.name} has no proxy_service defined.", None), 400

    if not stack.proxy_port:
      return response(400, None, f"Stack {stack.name} has no proxy_port defined.", None), 400

    # Creating necessary folders
    stacks_folder = StackModel.get_stacks_folder()
    caddyconf_folder = stacks_folder + "/conf.d"
    project_folder = stack.get_project_folder()

    compose_location = project_folder + "/docker-compose.yml"
    caddyconf_location = caddyconf_folder + f"/{stack.name}.conf"

    if not path.exists(project_folder):
      makedirs(project_folder)

    if not path.exists(caddyconf_folder):
      makedirs(caddyconf_folder)

    data_compose = get_compose_data(services=stack.services, stack_name=stack.name)
    data_caddyconf = {
      'subdomain': stack.subdomain,
      'email': stack.email,
      'proxy_service': ServiceModel.find_by_id(stack.proxy_service).name,
      'proxy_port': stack.proxy_port
    }

    if data_compose:
      compose_string = get_compose(data_compose)
      caddyconf_string = get_caddyconf(data_caddyconf)

      if create_file(compose_location, compose_string) and create_file(caddyconf_location, caddyconf_string):
        return response(200, f"Stack {stack.name} has been applied.", None, None), 200
      else:
        return response(500, None, f"An error has occured while trying to save compose file.", None), 500

    else:
      return response(500, None, f"An error has occured while trying to assemble data for compose file", None), 500

  @jwt_required()
  def delete(self, _id):
    """DELETE method to remove project files of stack

    purge=true will delete project folder as well.

    """

    parser = reqparse.RequestParser()
    parser.add_argument('purge',
                        type = str)

    data = parser.parse_args()

    if not StackModel.find_by_id(_id):
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404

    stack = StackModel.find_by_id(_id)

    stacks_folder = StackModel.get_stacks_folder()
    project_folder = stack.get_project_folder()
    compose_location = f"{project_folder}/docker-compose.yml"
    caddyconf_location = f"{StackModel.get_stacks_folder()}/conf.d/{stack.name}.conf"

    # Check if services are running first
    for service in stack.services:
      if container_is_up(f"{stack.name}_{service.name}"):
        return response(400, None, f"Stack {stack.name} has services running or in exited status. Please remove them first.", None), 400

    # If purge = True, delete whole stack folder
    if data['purge']:
      if data['purge'].lower() == 'true':
        if path.exists(project_folder):
          try:
            rmtree(project_folder)
          except:
            print_exc()
            return response(500, None, f"An error occured while trying to purge project files for stack {stack.name}", None), 500
    
    # Else just docker-compose file
    else:
      if path.isfile(compose_location):
        try:
          remove(compose_location)
        except:
          print_exc()
          return response(500, None, f"An error occured while trying to delete project files for stack {stack.name}", None), 500

    # Remove Caddyfile
    if path.isfile(caddyconf_location):
      try:
        remove(caddyconf_location)
      except:
        print_exc()
        return response(500, None, f"An error occured while trying to delete project files for stack {stack.name}", None), 500

    return response(201, f"Project files for stack {stack.name} have been successfully removed.", None, None), 201

class StackUp(Resource):
  """API resource to `docker-compose up` a specific stack configuration."""

  @jwt_required()
  def post(self, _id):
    """Brings up a specific stack configuration

    Runs `docker-compose up -d`

    Args:
      _id (int): The stack ID of the stack to be started.

    """

    stack = StackModel.find_by_id(_id)

    if not stack:
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404      

    project_folder = stack.get_project_folder()

    if not stack.services:
      return response(400, f"Stack {stack.name} has no services assigned.", None, None), 400      

    # Check if folders exist
    if not path.exists(project_folder):
      return response(404, None, f"Project folder for stack {stack.name} doesn't exist.", None), 404

    # Check if containers are already up
    for service in stack.services:
      container = get_container(f"{stack.name}_{service.name}")
      if container and container.status is 'running':
        return response(400, None, f"Service {service.name} is already running.", container_data(container)), 400

    try:
      cmd = subprocess.run(["docker-compose", "up", "-d"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=project_folder)

      # Reload Caddy
      caddy = get_container("andes_web_1")
      if caddy:
        try:
          caddy.exec_run("kill -USR1 1")
          print("Caddy has been reloaded.")
        except:
          print_exc()

      return response(200, f"Stack {stack.name} has been started.", None, {'stdout': cmd.stdout.decode("utf-8")}), 200
    except subprocess.CalledProcessError as e:
      print_exc()
      return response(500, None, f"An error occured while trying to start {stack.name}", {'stdout': e.stdout.decode("utf-8")}), 500


class StackDown(Resource):
  """API resource to `docker-compose down` a specific stack configuration."""
  
  @jwt_required()
  def post(self, _id):
    """Shuts down a specific stack configurations

    Runs `docker-compose down`

    Args:
      _id (int): The stack ID of the stack to be shut down.

    """

    stack = StackModel.find_by_id(_id)

    if not stack:
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404      

    project_folder = stack.get_project_folder()

    # Check if folders exist
    if not path.exists(project_folder):
      return response(404, None, f"Project folder for stack {stack.name} doesn't exist.", None), 404

    try:
      cmd = subprocess.run(["docker-compose", "down"], check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=project_folder)
      return response(200, f"Stack {stack.name} has been shut down.", None, {'stdout': cmd.stdout.decode("utf-8")}), 200
    except subprocess.CalledProcessError as e:
      print_exc()
      return response(500, None, f"An error occured while trying to stop {stack.name}", {'stdout': e.stdout.decode("utf-8")}), 500


class StackStatus(Resource):
  """API resource to retrieve information about a specific stack.

  Checks if containers of a specific stack are running and returns information about them.
  """

  @jwt_required()
  def get(self, _id):
    """Shows information about a stack

    Args:
      _id (int): The stack ID.

    """
    stack = StackModel.find_by_id(_id)

    if not stack:
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404      

    # Check if folders exist
    project_folder = stack.get_project_folder()
    if not path.exists(project_folder):
      return response(404, None, f"Project folder for stack {stack.name} doesn't exist.", None), 404    

    # Loop through assigned services and add container to list it's running
    if stack.services:
      container_list = []
      for service in stack.services:
        container = get_container(f"{stack.name}_{service.name}")
        if container:
          container_list.append(container)
    else:
      return response(400, f"Stack {stack.name} has no services assigned.", None, None), 400

    # If containers are running, output information
    if len(container_list) > 0:
      info = {
        'id': stack.id,
        'name': stack.name,
        'subdomain': stack.subdomain,
        'port': stack.proxy_port,
        'services': [container_data(x) for x in container_list]
      }
      return response(200, f"Data for services in stack {stack.name} has been retrieved.", None, info), 200

    # Else output that nothing is up
    else:
      return response(200, f"No service is in running or exited status.", None, None), 200


class StackLogs(Resource):
  """API resource to retrieve logs of services in stack"""

  @jwt_required()
  def get(self, _id):
    """Displays STDOUT and STDERR of each container/service in a stack."""
    stack = StackModel.find_by_id(_id)

    if not stack:
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404

    # Check if folders exist
    project_folder = stack.get_project_folder()
    if not path.exists(project_folder):
      return response(404, None, f"Project folder for stack {stack.name} doesn't exist.", None), 404

    # Loop through assigned services and add container to list if possible
    if stack.services:
      container_list = []
      for service in stack.services:
        container = get_container(f"{stack.name}_{service.name}")
        if container:
          container_list.append(container)
    else:
      return response(400, f"Stack {stack.name} has no services assigned.", None, None), 400

    if len(container_list) > 0:
      logs = []
      for container in container_list:
        try:
          tmp = None
          try:
            tmp = [x for x in container.logs().decode("utf-8").split('\n') if x]
          except:
            print_exc()

          logs.append({
                        'id': container.short_id,
                        'name': container.name,
                        'logs': tmp
                      })
        except:
          print_exc()
          return response(500, None, f"An error occured while trying to fetch container data.", None), 500

      return response(200, f"Data for services in stack {stack.name} has been retrieved.", None, logs), 200

    # Else output that nothing is up
    else:
      return response(200, f"No service is in running or exited status.", None, None), 200


class StackRemove(Resource):
  """API resource to remove running or exited containers"""

  @jwt_required()
  def delete(self, _id):
    stack = StackModel.find_by_id(_id)

    if not stack:
      return response(404, None, f"Stack with ID {_id} does not exist.", None), 404

    for service in stack.services:
      container = get_container(f"{stack.name}_{service.name}")

      if container and container.status in ['running', 'exited']:
        try:
          container.remove(force=True)
        except:
          print_exc()
          return response(500, None, f"An error occured while trying to remove container of service {service.name}.", None), 500

    return response(200, f"Containers for stack {stack.name} have been removed successfully.", None, None), 200