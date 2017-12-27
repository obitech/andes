def response(status, message, error, data):
  """A helper function to format a proper API response.

  Args:
    status (int): The HTTP status code.
    message (str): A message which should be displayed.
    error (str): An error message incase the status code is not 2xx.
    data (optional): The data payload. Should be null, a list or a dict.
  
  Returns:
    dict: A dictionary with the passed data.

  """
  return {
    'status': status,
    'message': message,
    'error': error,
    'data': data
  }

def container_data(container):
  """Returns a dictionary with information about a container

  Args:
    The name of the container

  Returns:
    Dictionary with various information about the container.
  """
  from traceback import print_exc

  try:
    return {
      'id': container.short_id,
      'name': container.name,
      'status': container.status,
      'labels': container.labels
    }

  except:
    print_exc()
    
  return None