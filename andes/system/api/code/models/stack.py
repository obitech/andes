import re
from datetime import datetime
from traceback import print_exc

from db import db


stack_service_table = db.Table('stack_service_table',
  db.Column('stack_id', db.Integer, db.ForeignKey('stacks.id'), primary_key=True),
  db.Column('service_id', db.Integer, db.ForeignKey('services.id'), primary_key=True))

class StackModel(db.Model):
  """Class representing a stack

  A is basically a group of services in a docker-compose file.

  Attributes:
    id (int): The ID of the stack (primary key).
    name (str): The name of the stack.
    description (str): The description of the stack.
    subdomain (str): The subdomain a stack is reachable under.
    email (str): The email needed for Caddy to create TLS certificates for this subdomain.
    proxy_service (int): The service ID to which Caddy forwards requests.
    proxy_port (int): The port needed for Caddy's proxy statement.
    created_at (str): Indicating the creation of the stack.
    last_changed (str): Indictaion when this stack has been last modified.
    services (:obj:`list` of :obj:`services`): List of services defined as this stack.
    stacks_folder (str): The location on the file system where stacks are saved.

  """
  __tablename__ = 'stacks'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(32), nullable=False)
  description = db.Column(db.String(256))
  subdomain = db.Column(db.String(128))
  email = db.Column(db.String(64))
  proxy_service = db.Column(db.Integer)
  proxy_port = db.Column(db.Integer)
  created_at = db.Column(db.DateTime, default=datetime.now())
  last_changed = db.Column(db.DateTime, default=datetime.now())
  services = db.relationship('ServiceModel', secondary=stack_service_table, backref="stacks", lazy=True)

  def __init__(self, name, proxy_port=None, proxy_service=None, email=None, description=None, subdomain=None):
    """Stack initializiation method

    Args:
      name (str): Name of the stack.
      proxy_service (int, optional): The service for Caddy to forward requests to. Defaults to None.
      proxy_port (int, optional): The port needed for Caddy's proxy statement. Defaults to None.
      description (str, optional): Description of the stack, defaults to None.
      subdomain (str, optional): Subdomain for this services, defaults to None.
      email (str, optional): The Email required for TLS certifications. Defaults to None.

    """
    self.name = name
    self.active = False
    self.description = description
    self.email = email
    self.proxy_service = proxy_service
    self.proxy_port = proxy_port
    self.subdomain = subdomain
    self.created_at = datetime.now()
    self.last_changed = self.created_at

  def json(self):
    """Returns dictionary of the specific stack 
    
    Returns:
      A dictionary of the attributes of the specific stack.

    """
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'subdomain': self.subdomain,
      'email': self.email,
      'proxy_service': self.proxy_service,
      'proxy_port': self.proxy_port,
      'services': [x.id for x in self.services],
      'created_at': self.format_date(self.created_at),
      'last_changed': self.format_date(self.last_changed),
    }

  def get_project_folder(self):
    return self.get_stacks_folder() + f"/{self.name}"

  # TODO: remove this dirty hack
  @classmethod
  def get_stacks_folder(cls):
    return "../../../stacks"

  @classmethod
  def valid_email(cls, email):
    """Checks with regex if provided email is valid

    Args:
      email (str): The email to be checked.

    Returns:
      bool: True if correct, False if not.

    """

    try:
      if re.compile("^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}$").match(email):
        return True
    except:
      print_exc()
      pass

    return False

  @classmethod
  def valid_subdomain(cls, domain):
    """Checks if passed subdomain has the correct syntax.

    Note:
      Regex has been grabbed from here:
      https://stackoverflow.com/questions/10306690/domain-name-validation-with-regex

    Args:
      domain (str): Subdomain to check as string.

    Returns:
      bool: True if correct, False if not.

    """

    try:
      # old: ^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,6}$
      if re.compile("((^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,6})|(([a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.)?localhost))$").match(domain):
        return True
    except:
      print_exc()
      pass

    return False

  @classmethod
  def valid_name(cls, name):
    """Checks if the passed name is valid.

    This needs to be done since the stack name is also the folder name for the later created docker-compose.yml.
    
    Args:
      name (str): Name of stack as string.

    Returns:
      bool: True if name is valid, False if not.

    """
    try:
      if re.compile("^\w+$").match(name):
        return True
    except:
      print_exc()
      pass

    return False

  @classmethod
  def format_date(cls, date):
    """Transforms a date object into a valid ISO format string.

    Args:
      date (:obj:`datetime`): Python datetime object

    Returns:
      str: Date string in ISO format.

    """
    try:
      return date.isoformat()
    except:
      print_exc()
      pass

    return None

  @classmethod
  def find_by_name(cls, name):
    """Returns a stack object from database according to passed name

    Args:
      name (str): Name of stack to be found

    Returns:
      :obj:`stack`: A stack object according to name, None if not found.
    """    
    return cls.query.filter_by(name=name).first()

  @classmethod
  def find_by_id(cls, _id):
    """Returns a stack object from database according to passed ID

    Args:
      _id (int): ID of stack to be found

    Returns:
      :obj:`stack`: A stack object according to ID, None if not found.
    """     
    return cls.query.filter_by(id=_id).first()

  def save_to_db(self):
    """Saves stack to database"""
    db.session.add(self)
    db.session.commit()

  def delete_from_db(self):
    """Deletes stack from database"""
    db.session.delete(self)
    db.session.commit()