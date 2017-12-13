import re

from db import db

class ServiceModel(db.Model):
  """Class representing a service

  A service represents an blueprint implementation in a specific stack.
  This a what will get inserted under `services` in the docker-compose file.

  Attributes:
    id (int): The ID of this service (primary key).
    name (str): The name of this service.
    blueprint_id (int): The ID of the blueprint this service is modelled after.
    description (str, optional): The description for this service
    exposed_ports (str, opptional): The ports which shall be exposed to other services linked to in the same stack.
      This will be assembled by resource.service from [80, 8080] t0 "80,8080".
    mapped_ports (str, optional) : The directive after which ports should be mapped from host to container.
      This will be assembled by resources.service from ["80:80", "8080:8080"] to "80:80,8080:8080".
    volumes (str, optional): Mapped volumes from Host to service.
      This will be assembled by resources.service from ["/srv/www:/etc", "/path/to:/folder"] to 
      "/srv/www:/etc,/path/to:/folder".
    env (str, optional): Passed environment variables.
      This will be assembled by resources.service from ["ENV_VAR=1", "ENV_VAR_2=2"] to 
      "ENV_VAR=1,ENV_VAR_2=2".
    ip (int): The IP assigned to this service. Will be assigned according to ID.

  """
  __tablename__ = 'services'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(32), nullable=False)
  description = db.Column(db.String(256))
  exposed_ports = db.Column(db.String(512))
  mapped_ports = db.Column(db.String(512))
  volumes = db.Column(db.String(512))
  env = db.Column(db.String(512))
  ip = db.Column(db.String(15))

  blueprint_id = db.Column(db.Integer, db.ForeignKey('blueprints.id'), nullable=False)

  def __init__(self, name, blueprint_id, exposed_ports, mapped_ports, description=None, volumes=None, env=None):
    """Service initialization method

    Args:
      name (str): The name of this service.
      blueprint_id (int): The ID of the blueprint this service is modelled after.
      description (str, optional): The description for this service
      exposed_ports (str, opptional): The ports which shall be exposed to other services linked to in the same stack.
        This will be assembled by resource.service from [80, 8080] t0 "80,8080".
      mapped_ports (str, optional) : The directive after which ports should be mapped from host to container.
        This will be assembled by resources.service from ["80:80", "8080:8080"] to "80:80,8080:8080".
      volumes (str, optional): Mapped volumes from Host to service.
        This will be assembled by resources.service from ["/srv/www:/etc", "/path/to:/folder"] to 
        "/srv/www:/etc,/path/to:/folder".
      env (str, optional): Passed environment variables.
        This will be assembled by resources.service from ["ENV_VAR=1", "ENV_VAR_2=2"] to 
        "ENV_VAR=1,ENV_VAR_2=2".
    """
    self.name = name
    self.description = description
    self.mapped_ports = mapped_ports
    self.exposed_ports = exposed_ports
    self.volumes = volumes
    self.env = env
    self.blueprint_id = blueprint_id
    self.ip = None
  
  def json(self):
    """Returns dictionary of the specific service 
    
    Returns:
      A dictionary of the attributes of the specific service.

    """
    return {
      'id': self.id,
      'blueprint': self.blueprint_id,
      'name': self.name,
      'description': self.description,
      'stacks': [x.id for x in self.stacks],
      'exposed_ports': [int(x) for x in self.exposed_ports.split(',')],
      'mapped_ports': self.split_string(self.mapped_ports),
      'volumes': self.split_string(self.volumes),
      'env': self.split_string(self.env),
      'ip': self.ip
    }

  @classmethod
  def port_list(cls, ports):
    """Transform a string of ports into a list of ports.

    Does not check if ports are valid.

    Args:
      ports (str): A string of ports.
        E.g. "80,8080,443"

    Returns:
      A list of ports, e.g. [80, 8080, 443].

      Returns None if string is in an incorrect format.
    """
    try:
      return [int(x) for x in ports.split(',')]
    except:
      pass

    return None

  @classmethod
  def split_string(self, stuff):
    """Splits a string at ','

    Args:
      stuff (str): The string to be split.

    Returns:
      A list of strings.

      Returns None if string is in incorrect format.
    """
    try:
      return stuff.split(',')
    except:
      return None

    return None

  @classmethod
  def valid_env(cls, env):
    """Checks if passed environment variables are in the correct format.

    Args:
      env (:obj:`list`): A list of environment variables as strings.

    Returns:
      True, if format is correct.

      False if format is incorrect.
    """
    if env in [None, [""], [], [None]]:
      return True

    if type(env) is not list:
      return False    

    try:
      for var in env:
        if not re.compile("^[\w_\.]+=[\w_\.]+$").match(var):
          return False
    except:
      return False

    return True

  @classmethod
  def join_env_string(cls, data):
    """Joins a list of environment variables into a string

    ["VAR=1", "FOO=BAR"] -> "VAR=1,FOO=BAR"

    Args:
      data (:obj:`dict`): The data dictionary with POST request parameters

    Returns:
      A String of environment variables if format is correct.

      None if format is incorrect.
    """
    try:
      if data['env'] in [None, [""], [], [None]]:
        pass
      else:
        return ','.join(data['env'])
    except:
      pass

    return None  


  @classmethod
  def valid_volumes(cls, volumes):
    """Checks if passed volumes are in the correct syntax.

    "/srv/www:/tmp" would pass.
    "$ test" would not pass.

    Args:
      volumes (:ob:`list`): List of volumes to be mapped.

    Returns:
      True if syntax is correct.
      False if syntax is incorrect.
    """
    if volumes in [None, [""], [], [None]]:
      return True

    if type(volumes) is not list:
      return False

    try:
      for volume in volumes:
        if not re.compile("^(/[\w.]*/?)+:(/[\w.]*/?)+$").match(volume):
          return False
        
    except:
      return False

    return True

  @classmethod
  def join_volume_string(cls, data):
    """Joins a list of volumes into a string.

    ["/srv/www:/tmp", "/foor:/bar"] -> "/srv/ww:/tmp,/foo:/bar"

    Args:
      data (:obj:`dict`): The data dictionary with POST request parameters.

    Returns:
      A String of volumes if syntax is correct.

      None if format is incorrect.
    """
    try:
      if data['volumes'] in [None, [""], [], [None]]:
        pass
      else:
        return ','.join(data['volumes'])
    except:
      pass

    return None

  @classmethod
  def valid_ports(cls, exposed_ports):
    """Checks if passed exposed_ports are valid

    Args:
      exposed_ports (:obj:`list`): A list of ports as int

    Returns:
      True if ports are valid
      False if ports are invalid
    """
    try:
      for port in exposed_ports:
        if port < 0 or port > 65535:
          return False
    except:
      return False

    return True

  @classmethod
  def valid_mapped_ports(cls, ports):
    """Checks if passed mapped_ports are valid
    
    Shoould pass almost all of the short syntax: https://docs.docker.com/compose/compose-file/#ports

    Args:
      ports (:obj:`list`): Ports passed as list of strings.
        e.g. ['80:80','123:456', "8000", "8000-8010:8000-8010"]

    Returns:
      True if ports are valid.

      False if ports are invalid.
    """
    for entry in ports:
      # Regex check if general form is correct
      if not re.compile("^((\d{1,5}:\d{1,5})|(\d{1,5})|(\d{1,5}-\d{1,5})|(\d{1,5}-\d{1,5}:\d{1,5}-\d{1,5}))(/udp|/tcp)?$").match(entry):
        return False

      # entry = ["80:80"]
      mapping = entry.split(':')
      # mapping = ['80', '80']
      for port in mapping:
        if port not in [":", "/udp", "/tcp"]:
          # Port range e.g. 8000-8010
          if '-' in port:
            port_range = port.split('-')
            try:
              if int(port_range[0]) >= int(port_range[1]):
                return False

              for x in port_range:
                if int(x) < 0 or int(x) > 65535:
                  return False
            except:
              return False

          else:
            try:
              if int(port) < 0 or int(port) > 65535:
                return False
            except:
              return False

    return True


  @classmethod
  def join_port_string(cls, exposed_ports):
    """Joins a list of exposed_ports into a string

    [80, 8080] -> "80,8080"

    Args:
      exposed_ports (:obj:`list`): A list of exposed ports

    Returns:
      String of exposed ports if list is valid

      None if list has invalid members
    """
    try:
      return ','.join([str(x) for x in exposed_ports])
    except:
      pass

    return None

  @classmethod
  def get_ip(self, _id):
    """Assigns an IP for the service according to its ID

    Subnet: 172.42.0.0/16
    IPs start at x.x.0.11

    Args:
      _id (int): ID of the service

    Returns:
      String of IP according to ID
    """
    tmp = _id + 10
    return f"172.42.{tmp // 255}.{tmp % 255}"

  @classmethod
  def find_by_name(cls, name):
    """Returns a service object from database according to passed name

    Args:
      name (str): Name of service to be found

    Returns:
      A service object according to name, None if not found.
    """
    return cls.query.filter_by(name=name).first()

  @classmethod
  def find_by_id(cls, _id):
    """Returns a service object from database according to passed ID

    Args:
      _id (int): ID of service to be found

    Returns:
      A service object according to ID, None if not found.
    """    
    return cls.query.filter_by(id=_id).first()

  def save_to_db(self):
    """Saves service to database"""
    db.session.add(self)
    db.session.commit()

  def delete_from_db(self):
    """Deletes service from database"""
    db.session.delete(self)
    db.session.commit()
