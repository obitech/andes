import re
from ipaddress import ip_address, ip_network, IPv4Network

from db import db

class NetworkModel(db.Model):
  __tablename__ = "networks"

  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(32), nullable=False)
  description = db.Column(db.String(256))
  driver = db.Column(db.String(12))
  subnet = db.Column(db.String(18))
  iprange = db.Column(db.String(18))
  stack_id = db.Column(db.Integer, db.ForeignKey('stacks.id'), unique=True)

  def __init__(self, name, stack_id, description=None, subnet=None, iprange=None):
    self.name = name
    self.driver = 'bridge'
    self.description = description
    self.subnet = subnet
    self.iprange = iprange
    self.stack_id = stack_id

  def json(self):
    return {
      'id': self.id,
      'name': self.name,
      'description': self.description,
      'driver': self.driver,
      'subnet': self.subnet,
      'iprange': self.iprange,
      'stack_id': self.stack_id
    }

  # TODO: cannot be 172.42.0.2 - x.x.x.10
  @classmethod
  def valid_ip(cls, ip):
    try:
      ip_address(ip)

      # ip_list = ip.split('.')
      # if 2 <= int(ip_list[0]) <= 10:
      #   return False

    except:
      return False

    return True

  @classmethod
  def valid_network(cls, network):
    try: 
      IPv4Network(network)
    except:
      return False
    
    return True

  @classmethod
  def network_overlap(cls, net1, net2):
    return IPv4Network(net1).overlaps(IPv4Network(net2))

  @classmethod
  def find_by_name(cls, name):
    return cls.query.filter_by(name=name).first()

  @classmethod
  def find_by_id(cls, _id):
    return cls.query.filter_by(id=_id).first()

  @classmethod
  def assigned_to_stack(cls, _id):
    """
    Checks if a network is already assigned to a stack
    """
    try:
      if cls.query.filter_by(stack_id=_id).first():
        return True
    except:
      pass

    return False

  def save_to_db(self):
    db.session.add(self)
    db.session.commit()

  def delete_from_db(self):
    db.session.delete(self)
    db.session.commit()
