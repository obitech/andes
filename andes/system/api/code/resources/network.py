from flask_restful import Resource, reqparse
from flask_jwt import jwt_required

from models.stack import StackModel
from models.network import NetworkModel
from util.response import response

class NetworkList(Resource):
  @jwt_required()
  def get(self):
    return response(200, "Networks have been retrieved.", None, [net.json() for net in NetworkModel.query.all()]), 200

class NetworkCreate(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
    type = str,
    required = True,
    help = "The network name is required.")
  parser.add_argument('stack_id',
    type = int,
    required = True,
    help = "The stack id is required")
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
        return {'code': 400,
                'error': f"Invalid network {data['subnet']}, needs to be valid CIDR address without host bits."}

    if data['iprange']:
      if not NetworkModel.valid_network(data['iprange']):
        return {'code': 400,
                'error': f"Invalid IP range {data['iprange']}, needs to be valid CIDR address without host bits."}    

    if data['iprange'] and data['subnet']:
      if not NetworkModel.network_overlap(data['iprange'], data['subnet']):
        return {'code': 400,
                'error': f"IP range {data['iprange']} does not overlapt subnet {data['subnet']}"}

    return {'code': 200,
            'subnet': data['subnet'],
            'iprange': data['iprange']}

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()

    if data['stack_id']:
      if not StackModel.find_by_id(data['stack_id']):
        return response(400, None, f"Stack {data['stack_id']} doesn't exist.", None), 400

      if NetworkModel.assigned_to_stack(data['stack_id']):
        return response(400, None, f"ID {data['stack_id']} already assigned to stack {StackModel.find_by_id(data['stack_id']).name}", None), 400

    if NetworkModel.find_by_name(data['name']):
      return response(400, None, f"Network with name {data['name']} already exitst.", None), 400

    sub = self.check_subnet(data)
    if sub['code'] is not 200:
      return response(sub['code'], None, sub['error'], None), sub['code']

    network = NetworkModel(**data)
    try:
      network.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update network {data['name']}.", None), 500

    return response(201, f"Netowrk {data['name']} has been updated.", None, network.json()), 201

  @jwt_required()
  def put(self):
    data = self.parser.parse_args()
    sub = self.check_subnet(data)

    if data['stack_id']:
      if not StackModel.find_by_id(data['stack_id']):
        return response(400, None, f"Stack {data['stack_id']} doesn't exist.", None), 400

      if NetworkModel.assigned_to_stack(data['stack_id']):
        return response(400, None, f"ID {data['stack_id']} already assigned to stack {StackModel.find_by_id(data['stack_id']).name}", None), 400

    if sub['code'] is not 200:
      return response (sub['code'], None, sub['error'], None), sub['code']

    network = NetworkModel.find_by_name(data['name'])
    if network:
      network.name = data['name']
      network.description = data['description']
      network.subnet = sub['subnet']
      network.iprange = sub['iprange']
      network.stack_id = data['stack_id']
    else:
      network = NetworkModel(data['name'], data['stack_id'], data['description'],
                             sub['subnet'], sub['iprange'])

    try:
      network.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update network. {data['name']}.", None), 500

    return network.json(), 201


class Network(Resource):
  @jwt_required()
  def get(self, _id):
    try:
      network = NetworkModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to retrieve network {network.name}."), 500

    if network:
      return response(200, f"Network {network.name} has been retrieved.", None, network.json()), 200

    return response(404, None, f"Network with ID {_id} does not exist.", None), 404


  @jwt_required()
  def delete(self, _id):
    try:
      network = NetworkModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to retrieve network {network.name}.", None), 500

    if network:
      try:
        network.delete_from_db()
      except:
        return response(500, None, f"An error occured while trying to delete {network.name}.", None), 500
      
      return response(200, f"Network {network.name} has been deleted.", None, None), 200

    return response(404, None, f"Network with ID {_id} does not exist.", None), 404