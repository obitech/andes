from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from datetime import datetime
from models.stack import StackModel

class StackList(Resource):
  @jwt_required()
  def get(self):
    return {
      'stacks': [stack.json() for stack in StackModel.query.all()]
    }

class StackCreate(Resource):
  parser = reqparse.RequestParser()
  parser.add_argument('name',
    type = str,
    required = True,
    help = "The name of the stack is required."
  )
  parser.add_argument('description',
    type = str,
    help = "The description of the stack."
  )
  parser.add_argument('subdomain',
    type = str,
    help = "The subdomain this stack should reside under."
  )

  @jwt_required()
  def post(self):
    data = self.parser.parse_args()

    if StackModel.find_by_name(data['name']):
      return {
        'message': f"Stack with name {data['name']} already exists."
      }, 400

    stack = StackModel(**data)

    try:
      stack.save_to_db()
    except:
      return {
        'error': f"An error occured while trying to save new stack."
      }, 500

    return stack.json()

  @jwt_required()
  def put(self):
    pass

class Stack(Resource):
  @jwt_required()
  def get(sef):
    pass

  @jwt_required()
  def delete(self):
    pass
