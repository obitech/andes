from db import db

class BlueprintModel(db.Model):
  """Class representing a blueprint

  This is effectively a docker image.

  Attributes:
    id (int): The ID of this blueprint (primary key)
    name (str): The name of this service.
    description (str): The description of this service.
    image (str): The image name for this blueprint.
    services (:obj:`list`): A list of services implementing this blueprint.
  """

  __tablename__ = 'blueprints'

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(32), nullable=False)
  description = db.Column(db.String(256))
  image = db.Column(db.String(64))
  services = db.relationship('ServiceModel', backref='blueprints', lazy=True)

  def __init__(self, name, image, description=None):
    """Blueprint initialization method

    Agrs:
      name (str): The name of this service.
      description (str): The description of this service.
      image (str): The image name for this blueprint.
    """
    self.name = name
    self.description = description
    self.image = image

  def json(self):
    """Returns a dictionary of the specific blueprint.

    Returns:
      A dictionary of the specific blueprint.

    """
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
    """Returns a blueprint object from database according to passed name

    Args:
      name (str): Name of blueprint to be found

    Returns:
      A blueprint object according to name, None if not found.
    """    
    return cls.query.filter_by(name=name).first()

  @classmethod
  def find_by_image(cls, image):
    """Returns a blueprint object from database according to passed image

    Args:
      image (str): image name of blueprint to be found

    Returns:
      A blueprint object according to image, None if not found.
    """    
    return cls.query.filter_by(image=image).first()  

  @classmethod
  def find_by_id(cls, _id):
    """Returns a blueprint object from database according to passed ID

    Args:
      _id (int): ID of blueprint to be found

    Returns:
      A blueprint object according to ID, None if not found.
    """        
    return cls.query.filter_by(id=_id).first()

  def save_to_db(self):
    """Saves blueprint to database"""
    db.session.add(self)
    db.session.commit()

  def delete_from_db(self):
    """Deletes blueprint from database"""
    db.session.delete(self)
    db.session.commit()
