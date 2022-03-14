from uuid import uuid4

from flask import Blueprint, request
from flask_restful import Resource, Api

from werkzeug.security import generate_password_hash

from .auth_middleware import admin_required
from .models import User, Admin

from . import db


auth = Blueprint('auth', __name__)
api = Api(auth)


def insert_admin():
    admin = Admin(
        username='admin',
        password=generate_password_hash('0024444103', method='sha256'),
        token='root-test',
        email='amiwrpremium@gmail.com',
        is_admin=True
    )

    db.session.add(admin)
    db.session.commit()


class Auth(Resource):
    @staticmethod
    @admin_required
    def get(user):
        # insert_admin()
        return {'message': 'Hello World!'}

    @staticmethod
    @admin_required
    def post(user):
        json_data: dict = request.get_json()
        username = json_data.get('username')
        password = json_data.get('password')
        email = json_data.get('email')

        if all([username, password, email]):
            if User.query.filter_by(username=username).first():
                return {'message': 'User already exists'}, 400
            else:
                hashed_password = generate_password_hash(password, method='sha256')
                token = str(uuid4())
                user = User(
                    username=username, password=hashed_password, email=email, token=token, is_admin=False
                )

                try:
                    print('here1')
                    db.session.add(user)
                    print('here2')
                    db.session.commit()
                    print('here3')
                    return {'message': 'User created successfully', 'data': {'token': token}}, 201
                except Exception as e:
                    print('here4')
                    return {'message': str(e)}, 500
        else:
            return {'message': 'Missing data'}, 400


api.add_resource(Auth, '/signup')
