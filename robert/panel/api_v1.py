from flask import Blueprint
from flask_restful import Resource, Api

from .auth_middleware import token_required


from .services import read_generated_data


app = Blueprint('api', __name__)
api = Api(app)


class Index(Resource):
    @staticmethod
    def get():
        return {'message': 'Hello World!'}


class Data(Resource):
    @staticmethod
    @token_required
    def get(user):
        return read_generated_data()


api.add_resource(Index, '/')
api.add_resource(Data, '/data')
