def get_compose(data):
  """Function to render the docker-compose.yml for a specific stack.
  
  This will use the docker-compose.yml template specified in the loader path.

  Note:
    Data should look like this::
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
  from os import path, getcwd
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

def create_compose(path, text):
  """Helper function to write the docker-compose string to file.

  Args:
    text (str): The docker-compose information as a string.

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

