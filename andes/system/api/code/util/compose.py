def get_compose(data):
  """
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
  from traceback import print_exc
  try:
    with open(path, 'w') as data_file:
      data_file.write(text)
  except:
    print_exc()
    return False

  return True

