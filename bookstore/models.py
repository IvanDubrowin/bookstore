from bookstore import db, views, login_manager
from sqlalchemy.orm import relationship, backref
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from whoosh.analysis import StemmingAnalyzer
import flask.ext.whooshalchemy as whooshalchemy
from bookstore import app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Association(db.Model):
    books = db.Column(db.String(30), db.ForeignKey('book.id', ondelete='cascade'),
    primary_key=True)
    authors = db.Column(db.String(30), db.ForeignKey('author.id', ondelete='cascade'), primary_key=True)

class Book(db.Model):
    __searchable__ = ['book']

    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(30))
    type = db.Column(db.String(30))
    description = db.Column(db.String(180))
    price = db.Column(db.String(30))
    image = db.Column(db.LargeBinary)
    authors = db.relationship('Author', secondary='association', back_populates='books')

    def __repr__(self):
        return '%r' % self.book

whooshalchemy.whoosh_index(app, Book)

class Author(db.Model):
    __searchable__ = ['name']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique = True)
    books = db.relationship('Book', secondary='association', back_populates='authors')

    def __repr__(self):
        return '%r' % self.name

whooshalchemy.whoosh_index(app, Author)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique = False, index = True)
    email = db.Column(db.String(100), unique = True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    number = db.Column(db.String(30))

    def __init__(self, username, email, password, number):
        self.username = username
        self.email = email
        self.password = password
        self.number = number

        if self.email == 'admin@admin.ru':
            self.role_id = 1
        else:
            self.role_id = 2

    def __repr__(self):
        return '<User %r>' % self.username



    def is_administrator(self):
        if self.role_id == 1:
            return True



    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique = True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name



class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(30))
    book = db.Column(db.String(128))
    email = db.Column(db.String(30))
    number = db.Column(db.String(30), unique=True)
    price = db.Column(db.String(30))
    status = db.Column(db.String(30))

    def __repr__(self):
        return 'Заказ %r' % self.id
