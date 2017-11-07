from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.network import NetworkModel

class NetworkList(Resource):
  @jwt_required()
  def get(self):
    return {
      'networks': [network.json() for network in NetworkModel.query.all()]
    }

class NetworkCreate(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
    type = str,
    required = True,
    help = "The network name is required.")
  parser.add_argument('description',
    type = str,
    help = "Network description is optional")
  parser.add_argument('subnet',
    type = str,
    help = "The subnet is optional")
  parser.add_argument('iprange',
    type = str,
    help = "The iprange is optional")

  def check_subnet(self, data):
    if data['subnet']:
      if not NetworkModel.valid_network(data['subnet']):
        return {
          'code': 400,
          'error': f"Invalid network {data['subnet']}, needs to be valid CIDR address without host bits."}

    if data['iprange']:
      if not NetworkModel.valid_network(data['iprange']):
        return {
          'code': 400,
          'error': f"Invalid IP range {data['iprange']}, needs to be valid CIDR address without host bits."}    

    if data['iprange'] and data['subnet']:
      if not NetworkModel.network_overlap(data['iprange'], data['subnet']):
        return {
          'code': 400,
          'error': f"IP range {data['iprange']} does not overlapt subnet {data['subnet']}"}

    return {
      'code': 200,
      'subnet': data['subnet'],
      'iprange': data['iprange']}

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()

    if NetworkModel.find_by_name(data['name']):
      return {
        'error': f"Network with name {data['name']} already exitst."
      }, 400

    sub = self.check_subnet(data)
    if sub['code'] is not 200:
      return {
        'error': sub['error']
      }, sub['code']

    network = NetworkModel(**data)
    try:
      network.save_to_db()
    except:
      return {
        'error': f"An error occured while trying to save network."
      }, 500

    return network.json(), 201

  @jwt_required()
  def put(self):
    data = self.parser.parse_args()
    sub = self.check_subnet(data)
    if sub['code'] != 200:
      return {
        'error': sub['error']
      }, sub['code']

    network = NetworkModel.find_by_name(data['name'])
    if network:
      network.name = data['name']
      network.description = data['description']
      network.subnet = sub['subnet']
      network.iprange = sub['iprange']
    else:
      network = NetworkModel(data['name'], data['description'],
                             sub['subnet'], sub['iprange'])

    try:
      network.save_to_db()
    except:
      return {
        'error': f"An error occured while trying to save network."
      }, 500

    return network.json(), 201


class Network(Resource):
  @jwt_required()
  def get(self, _id):
    try:
      network = NetworkModel.find_by_id(_id)
    except:
      return {
        'error': f"An error occured while trying to retrieve network."
      }, 500

    if network:
      return network.json()

    return {
      'error': f"Network with ID {_id} does not exist."
    }, 400


  @jwt_required()
  def delete(self, _id):
    try:
      network = NetworkModel.find_by_id(_id)
    except:
      return {
        'error': f"An error occured while trying to retrieve network."
      }, 500

    if network:
      network.delete_from_db()
      return {
        'message': f"Network with id {_id} has been deleted."
      }

    return {
      'error': f"Network with ID {_id} does not exist."
    }, 400