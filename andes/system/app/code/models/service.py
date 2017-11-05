import re

from db import db

class ServiceModel(db.Model):
  __tablename__ = 'services'

  # TODO: Include tag ???
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(32))
  image = db.Column(db.String(64))
  exposed_ports = db.Column(db.String(255))
  volumes = db.Column(db.String(1024))

  def __init__(self, name, image, exposed_ports, volumes=None):
    self.name = name
    self.image = image
    self.exposed_ports = exposed_ports
    self.volumes = volumes

  def json(self):
    if self.volumes:
      volumes = self.volumes.split(',')
    else:
      volumes = self.volumes

    return {
      'id': self.id,
      'name': self.name,
      'image': self.image,
      'exposed_ports': self.exposed_ports.split(','),
      'volumes': volumes
    }

  # TODO: validate if image exists

  @classmethod
  def valid_volumes(cls, volumes):
    print(f"received {volumes}")

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
