from flask_restful import Resource, reqparse
from models.user import UserModel

class UserRegister(Resource):
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
    data = UserRegister.parser.parse_args()

    # Check if user exists
    if UserModel.find_by_username(data['username']):
      return {'message': f"Error: User {data['username']} already exists."}, 400

    user = UserModel(**data)
    user.save_to_db()

    return {'message': f"User {data['username']} has been created."}, 201