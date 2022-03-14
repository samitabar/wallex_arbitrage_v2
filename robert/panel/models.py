from . import db


class BaseUser(db.Model):
    __abstract__ = True

    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    token = db.Column(db.String(120), unique=True, nullable=False)

    active = db.Column(db.Boolean(), default=True, nullable=False)
    is_admin = db.Column(db.Boolean(), default=False, nullable=False)

    def __init__(self, username, password, email, token, is_admin=False):
        self.username = username
        self.password = password
        self.email = email
        self.token = token
        self.is_admin = is_admin


class User(BaseUser):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)


class Admin(BaseUser):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
