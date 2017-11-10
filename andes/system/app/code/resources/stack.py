from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from datetime import datetime

from models.stack import StackModel
from models.response import response

class StackList(Resource):
  @jwt_required()
  def get(self):
    return response(200, "Stacks have been retrieved.", None, [stack.json() for stack in StackModel.query.all()]), 200

class StackCreate(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
    type = str,
    required = True,
    help = "The name of the stack is required.")
  parser.add_argument('description',
    type = str,
    help = "The description of the stack.")
  parser.add_argument('subdomain',
    type = str,
    help = "The subdomain this stack should reside under.")

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()

    if StackModel.find_by_name(data['name']):
      return response(400, None, f"Stack with name {data['name']} already exists.", None), 400

    if data['subdomain'] and not StackModel.valid_subdomain(data['subdomain']):
      return response(400, None, f"Invalid subdomain {data['subdomain']}", None), 400

    stack = StackModel(**data)

    try:
      stack.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update stack {data['name']}.", None), 500

    return response(201, f"Stack {data['name']} has been updated.", None, stack.json()), 201

  @jwt_required()
  def put(self):
    data = self.parser.parse_args()

    if data['subdomain'] and not StackModel.valid_subdomain(data['subdomain']):
      return response(400, None, f"Invalid subdomain {data['subdomain']}", None), 400

    stack = StackModel.find_by_name(data['name'])

    if stack:
      stack.name = data['name']
      stack.description = data['description']
      stack.subdomain = data['subdomain']
      stack.last_changed = datetime.now()
    else:
      stack = StackModel(**data)

    print(f"Stack: {stack.json()}")
    try:
      stack.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to update stack {data['name']}.", None), 500

    return response(201, f"Stack {data['name']} has been updated.", None, stack.json()), 201

class Stack(Resource):
  @jwt_required()
  def get(sef, _id):
    try:
      stack = StackModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to retrieve stack {stack.name}.", None), 500
    if stack:
      return response(200, f"Stack {stack.name} has been retrieved.", None, stack.json()), 200

    return response(404, None, f"Stack with id {_id} does not exist.", None), 404

  @jwt_required()
  def delete(self, _id):
    try:
      stack = StackModel.find_by_id(_id)
    except:
      return response(500, None, f"An error occured while trying to save stack {stack.name}.", None), 500

    if stack:
      try:
        stack.delete_from_db()
      except:
        return response(500, None, f"An error occured while trying to delete stack {stack.name}.", None), 500
        
      return response(200, f"Stack {stack.name} has been deleted.", None, None), 200

    return response(404, None, f"Stack with id {_id} does not exist.", None), 404