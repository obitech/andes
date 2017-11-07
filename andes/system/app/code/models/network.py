import re
from ipaddress import ip_address, ip_network, IPv4Network

from db import db

class NetworkModel(db.Model):
  __tablename__ = "networks"

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(32))
  description = db.Column(db.String(512))
  driver = db.Column(db.String(12))
  subnet = db.Column(db.String(18))
  iprange = db.Column(db.String(18))

  # TODO: Link up with StackModel

  def __init__(self, name, description=None, subnet=None, iprange=None):
    self.name = name
    self.driver = 'bridge'
    self.description = description
    self.subnet = subnet
    self.iprange = iprange

  def json(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'driver': self.driver,
      'subnet': self.subnet,
      'iprange': self.iprange
    }

  @classmethod
  def valid_ip(cls, ip):
    """
    Regex from here: 
    https://stackoverflow.com/questions/4890789/regex-for-an-ip-address
    """
    try:
      if re.compile("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$").match(ip):
        return True
    except:
      pass

    return False

  @classmethod
  def valid_network(cls, network):
    try:
      if re.compile("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}0\/([\d]|[1-2]\d|3[012])$").match(network):
        return True
    except:
      pass

    return False

  @classmethod
  def network_overlap(cls, net1, net2):
    return IPv4Network(net1).overlaps(IPv4Network(net2))

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
