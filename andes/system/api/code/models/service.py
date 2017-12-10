import re

from db import db

class ServiceModel(db.Model):
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
    self.name = name
    self.description = description
    self.mapped_ports = mapped_ports
    self.exposed_ports = exposed_ports
    self.volumes = volumes
    self.env = env
    self.blueprint_id = blueprint_id
    self.ip = None
  
  def json(self):
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
    try:
      return [int(x) for x in ports.split(',')]
    except:
      pass

    return None

  @classmethod
  def split_string(self, stuff):
    try:
      return stuff.split(',')
    except:
      return None

    return None

  @classmethod
  def valid_env(cls, env):
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
    try:
      for port in exposed_ports:
        if port < 0 or port > 65535:
          return False
    except:
      return False

    return True

  @classmethod
  def valid_mapped_ports(cls, ports):
    """
    Ports passed as list of strings: ['80:80','123:456']
    """
    for entry in ports:
      # Regex check if general form is correct
      # Shoould pass almost all of the short syntax: https://docs.docker.com/compose/compose-file/#ports
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
    try:
      return ','.join([str(x) for x in exposed_ports])
    except:
      pass

    return None

  @classmethod
  def get_ip(self, _id):
    # +10 because x.x.0.0 - 10 are reserved for andes containers
    tmp = _id + 10
    return f"172.42.{tmp // 255}.{tmp % 255}"

  @classmethod
  def find_by_name(cls, name):
    return cls.query.filter_by(name=name).first()

  @classmethod
  def find_by_id(cls, _id):
    return cls.query.filter_by(id=_id).first()

  def save_to_db(self):
    db.session.add(self)
    db.session.commit()

  def delete_from_db(self):
    db.session.delete(self)
    db.session.commit()
