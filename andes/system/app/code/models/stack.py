from db import db
from datetime import datetime
import re

class StackModel(db.Model):
  __tablename__ = 'stacks'

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(32))
  active = db.Column(db.Integer())
  description = db.Column(db.String(1024))
  subdomain = db.Column(db.String(512))
  created_at = db.Column(db.DateTime())
  last_changed = db.Column(db.DateTime())
  built_at = db.Column(db.DateTime())

  def __init__(self, name, description=None, subdomain=None):
    self.name = name
    self.active = 0
    self.description = description
    self.subdomain = subdomain
    self.created_at = datetime.now()
    self.last_changed = self.created_at
    self.built_at = None

  def json(self):
    if not self.built_at:
      built = None
    else:
      built = self.format_date(self.built_at)

    return {
      'id': self.id,
      'name': self.name,
      'active': self.active,
      'description': self.description,
      'created_at': self.format_date(self.created_at),
      'last_changed': self.format_date(self.last_changed),
      'built_at': built
    }

  @classmethod
  def validate_subdomain(cls, domain):
    """
    Stole this regex from here:
    https://stackoverflow.com/questions/10306690/domain-name-validation-with-regex
    """
    try:
      if re.compile("^[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,6}$").match(domain):
        return True
    except:
      pass

    return False

  def format_date(self, date):
    try:
      return date.isoformat()
    except:
      print (f"Exception caught with {date}")
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