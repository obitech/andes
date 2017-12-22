def get_compose_data(services, stack_name):
    from traceback import print_exc
    from models.blueprint import BlueprintModel
    from models.service import ServiceModel

    """Helper method to pass the necessary data to the function creating the string which ends up as the 
      docker-compose.yml.

    Args:
      services (:obj:`list` of :obj:`service`): A list with the services this stack is defined for.
      stack_name (str): The name of the stack defining the services.

    Returns:
      dict: A dictionary with the necessary information, None if exception is thrown.

    """

    data = []
    try:
      for service in services:
        tmp = {}

        tmp['stack_name'] = stack_name
        tmp['name'] = service.name
        tmp['image'] = BlueprintModel.find_by_id(service.blueprint_id).image
        tmp['exposed_ports'] = ServiceModel.port_list(service.exposed_ports)
        tmp['ip'] = service.ip
        tmp['restart'] = service.restart

        if service.volumes:
          tmp['volumes'] = ServiceModel.split_string(service.volumes)

        if service.env:
          tmp['environment'] = ServiceModel.split_string(service.env)

        if service.mapped_ports:
          tmp['mapped_ports'] = [x for x in service.mapped_ports.split(',')]

        data.append(tmp)

    except:
      print_exc()
      return None

    return data

def get_compose(data):
  """Function to render the docker-compose.yml for a specific stack.
  
  This will use the docker-compose.yml template specified in the loader path.

  Note:
    Data should look like this:
      data = [ 
        service_1 = {
          name: '...',
          image: '...',
          exposed_ports: [...],
          mapped_ports: [...],
          volumes: [...],
          environment: [...]
        },
        service_n = { ... }
      ]

  Args:
    data (:obj:`dict`): A dictionary with the necessary data in it.

  Returns:
    str: The a string containing the docker-compose information, according to the passed data.
      None if there has been an exception.
  """
  from jinja2 import Environment, FileSystemLoader
  from traceback import print_exc

  try:
    env = Environment(loader = FileSystemLoader('../templates', 
                                                followlinks = True),
                      trim_blocks = True,
                      lstrip_blocks = True)
    template = env.get_template('docker-compose.yml')

    return template.render(services=data)

  except:
    print_exc()
    return None

def get_caddyconf(data): 
  """Function render Caddy's .conf file for a specific stack.

  Will use the Caddyfile template in the loader path.

  Note:
    Data should look like this:
      data = {
        'subomain': '...',
        'email': '...' | null,
        'proxy_service': '...',
        'proxy_port': [\d]+
      }

  """
  from jinja2 import Environment, FileSystemLoader
  from traceback import print_exc 

  try:
    env = Environment(loader = FileSystemLoader('../templates',
                                              followlinks = True),
                      trim_blocks = True,
                      lstrip_blocks = True)
    template = env.get_template('Caddyfile')

    return template.render(data)

  except:
    print_exc()
    return None

def create_file(path, text):
  """Helper function to write the docker-compose or Caddy's .conf string to file.

  Args:
    path (str): The path where to save the file.
    text (str): The  information as a string.

  Returns:
    bool: True if writing was successful, None if not.

  """
  from traceback import print_exc
  try:
    with open(path, 'w') as data_file:
      data_file.write(text)
  except:
    print_exc()
    return False

  return True