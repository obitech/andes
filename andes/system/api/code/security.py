from models.user import UserModel

def authenticate(username, password):
  """Function handling user authentication

  Args:
    username (str): The user to authenticate
    password (str): The password of the user

  Returns:
    A user object if authentication was successful, None if not.

  """
  user = UserModel.find_by_username(username)
  if user and user.check_password(password):
    return user

def identity(payload):
  """Function retrieving user ID during authentication

  Args:
    payload (:obj:`dict`): A dictionary with authentication details

  Returns:
    A user ID or None if user wasn't found.
    
  """
  user_id = payload['identity']
  return UserModel.find_by_id(user_id)