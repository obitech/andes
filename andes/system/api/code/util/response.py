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