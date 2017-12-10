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

  def __init__(self, name, blueprint, exposed_ports, mapped_ports, description=None, volumes=None, env=None):
    self.name = name
    self.description = description
    self.mapped_ports = mapped_ports
    self.exposed_ports = exposed_ports
    self.volumes = volumes
    self.env = env
    self.blueprint_id = blueprint
    self.ip = None

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
  def valid_mapped_ports(cls, ports):
    """
    Ports passed as list of strings: ['80:80','123:456']
    """
    for entry in ports:
      # Regex check if general form is correct
      if not re.compile("^(\d+:\d+)$").match(entry):
        return False

      # tmp = ['80', ':', '80']
      tmp = entry.split(':')
      # Check if passed ports are valid ports
      for x in tmp:
        if x != ':':
          try:
            if int(x) < 0 or int(x) > 65535:
              return False
          except:
            return False

    return True

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
