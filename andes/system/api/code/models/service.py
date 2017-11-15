import re

from db import db

class ServiceModel(db.Model):
  __tablename__ = 'services'

  # TODO: Implement tag
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(32))
  description = db.Column(db.String(256))
  image = db.Column(db.String(64))
  exposed_ports = db.Column(db.String(128))
  volumes = db.Column(db.String(512))
  env = db.Column(db.String(512))

  # TODO: Link up with StackModel

  def __init__(self, name, image, exposed_ports, description=None, volumes=None, env=None):
    self.name = name
    self.description = description
    self.image = image
    self.exposed_ports = exposed_ports
    self.volumes = volumes
    self.env = env

  def json(self):
    if self.volumes:
      volumes = self.volumes.split(',')
    else:
      volumes = None

    if self.env:
      env = self.env.split(',')
    else:
      env = None

    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'image': self.image,
      'stacks': [x.id for x in self.stacks],
      'exposed_ports': self.exposed_ports.split(','),
      'volumes': volumes,
      'env': env
    }

  # TODO: validate if image exists

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
        if not re.compile("^(/[\w.]*/?)*$").match(volume):
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
        port = int(port)
        if port < 0 or port > 65535:
          return False
    except:
      return False

    return True

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
