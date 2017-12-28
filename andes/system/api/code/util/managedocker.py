def get_container(name):
  """Retrieves a container via the docker-py library

  Args:
    name (str): The hash ID or name of the container

  Returns:
    The container object

  """
  import docker
  from traceback import print_exc

  client = docker.from_env()

  try:
    return client.containers.get(name)
  except docker.errors.NotFound:
    pass
  except docker.errors.APIError:
    print_exc()

  return None

def container_is_up(name):
  """Checks if a container is in running or exited status.

  Args:
    name (str): name of the service

  Returns:
    bool: True if container is running or in exited status, False if not.

  """

  container = get_container(name)

  if container:
    if container.status in ['running', 'exited']:
      return True

  return False
