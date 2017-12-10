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

  # TODO: Remove
  env = Environment(loader = FileSystemLoader('../templates', 
                                              followlinks = True),
                    trim_blocks = True,
                    lstrip_blocks = True)

  template = env.get_template('docker-compose.yml')

  return template.render(services=data)

def create_compose(path, text):
  try:
    with open(path, 'w') as data_file:
      data_file.write(text)
  except Exception as e:
    print(e)
    return False

  return True

