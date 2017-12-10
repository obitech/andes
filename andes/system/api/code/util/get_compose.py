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
  env = Environment(loader=FileSystemLoader('../templates'),
                    trim_blocks=True)
  template = env.get_template('docker-compose.yml')

  return template.render(services=data)