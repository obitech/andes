from flask_restful import Resource, reqparse
from models.user import UserModel
from util.response import response


class UserRegister(Resource):
  """API resource handling user registration.

  Note:
    The majority of the user management is handled by Flask's JWT module.

  Todo:
    * Proper response header + body

  """
  parser = reqparse.RequestParser()
  parser.add_argument('username',
    type=str,
    required=True,
    help="The username field cannot be left blank."
  )
  parser.add_argument('password',
    type=str,
    required=True,
    help="The password field cannot be left blank."
  )

  def post(self):
    """POST method to register a user."""
    
    data = UserRegister.parser.parse_args()

    if UserModel.find_by_username(data['username']):
      return response(400, None, f"User {data['username']} already exists.", None), 400

    user = UserModel(**data)
    try:
      user.save_to_db()
    except:
      return response(500, None, f"An error occured while trying to create user {data['username']}.", None), 500

    return response(201, f"User {data['username']} has been created.", None, None), 201