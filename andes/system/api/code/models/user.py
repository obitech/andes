from db import db
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel(db.Model):
  """Class representing an user for the api.

  Andes uses JWT authentication which needs to be sent as a header for every following request::
    ``Authorization JWT <TOKEN>``

  Attributes:
    id (int): The ID of a user (primary key)
    username (str): The username.
    password (string): The hashed and salted password of the user.

  """

  __tablename__ = 'users'

  id = db.Column(db.Integer, primary_key = True)
  username = db.Column(db.String(80))
  password = db.Column(db.String(512))

  def __init__(self, username, password):
    """User initialization method.

    Agrs:
      username (str): The username.
      password (string): The plain password of the user.

    """
    self.username = username
    self.password = self.set_password(password)

  def set_password(self, password):
    """Generates a secure hash for the user password

    Note:
      Uses PBKDF2 algorithm with random, 16 char salt and 2000 iterations.
      For more information see http://werkzeug.pocoo.org/docs/0.12/utils/#werkzeug.security.generate_password_hash

    Args:
      password (str): The plain password of the user.

    Returns:
      str: SHA256 hash of the password and salt.

    """
    return generate_password_hash(password, method='pbkdf2:sha256:2000', salt_length=16)

  def check_password(self, password):
    """Checks entered password against stored hash

    Args:
      password (str): The plain password of the user.

    Returns:
      bool: True if password matches, False if not.

    """
    return check_password_hash(self.password, password)  

  def save_to_db(self):
    """Saves the user to the database"""
    db.session.add(self)
    db.session.commit()

  @classmethod
  def find_by_username(cls, username):
    """Returns a user object from database according to passed name

    Args:
      name (str): Name of user to be found

    Returns:
      :obj:`user`: A user object according to name, None if not found.
    """    
    return cls.query.filter_by(username=username).first()

  @classmethod
  def find_by_id(cls, _id):
    """Returns a user object from database according to passed ID

    Args:
      _id (int): ID of user to be found

    Returns:
      :obj:`user`: A user object according to ID, None if not found.
    """ 
    return cls.query.filter_by(id=_id).first()