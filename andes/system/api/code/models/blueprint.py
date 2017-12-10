from db import db

class BlueprintModel(db.Model):
  __tablename__ = 'blueprints'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(32), nullable=False)
  description = db.Column(db.String(256))
  image = db.Column(db.String(64))
  services = db.relationship('ServiceModel', backref='blueprints', lazy=True)

  def __init__(self, name, image, description=None):
    self.name = name
    self.description = description
    self.image = image

  def json(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'image': self.image,
      'services': [x.id for x in self.services]
    }

  # TODO: validate if image exists

  @classmethod
  def find_by_name(cls, name):
    return cls.query.filter_by(name=name).first()

  @classmethod
  def find_by_image(cls, image):
    return cls.query.filter_by(image=image).first()  

  @classmethod
  def find_by_id(cls, _id):
    return cls.query.filter_by(id=_id).first()

  def save_to_db(self):
    db.session.add(self)
    db.session.commit()

  def delete_from_db(self):
    db.session.delete(self)
    db.session.commit()
