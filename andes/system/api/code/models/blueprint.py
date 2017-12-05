from db import db

class BlueprintModel(db.Model):
  __tablename__ = 'bluebpints'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(32), nullable=False)
  description = db.Column(db.String(256))
  image = db.Column(db.String(64))
  exposed_ports = db.Column(db.String(512))
  # TODO: relationship services

  def __init__(self, name, exposed_ports, image, description=None):
    self.name = name
    self.description = description
    self.image = image
    self.exposed_ports = exposed_ports    

  def json(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'image': self.image,
      'exposed_ports': [int(x) for x in self.exposed_ports.split(',')]
    }

  # TODO: validate if image exists

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
  def join_port_string(cls, data):
    try:
      if data['exposed_ports'] in [None, [""], [], [None]]:
        pass
      else:
        return ','.join([str(x) for x in data['exposed_ports']])
    except:
      pass

    return None

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
