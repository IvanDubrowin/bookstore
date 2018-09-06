# coding: utf-8
from flask import request
from flask_wtf import FlaskForm
from wtforms import TextField, PasswordField, StringField, SubmitField, BooleanField, FileField, IntegerField
from wtforms.fields.html5 import TelField
from wtforms.validators import Email, Required, Length, Regexp, EqualTo, NumberRange
from wtforms import ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField, QuerySelectMultipleField
from .models import User, Book, Author, Association
from bookstore import db


class LoginForm(FlaskForm):
    name = StringField('Введите ваше имя', validators=[Required()])
    email = TextField('Введите почту', validators=[Required(), Email(), Length(1, 64)])
    password = PasswordField('Введите пароль', validators=[Required()])
    submit = SubmitField('Вход')
    remember_me = BooleanField('Не выходить из системы')

class RegistrationForm(FlaskForm):
    username = StringField('Введите ваше имя',
                            validators=[Required(),
                            Length(1, 64),
                            Regexp('^[A-Za-z][A-Za-z0-9_.]*$',
                            0, 'Имя должно состоять только из букв')])
    email = StringField('Введите почту', validators=[Required(),
                        Length(1, 64), Email()])
    password = PasswordField('Введите пароль', validators=[Required(),
                            EqualTo('password2',
                            message='Пароли должны совпадать.')])
    password2 = PasswordField('Подтвердите пароль', validators=[Required()])
    number = TelField('Введите телефон', validators=[Required()])
    submit = SubmitField('Регистрация')


    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email уже зарегистрирован')
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Такой пользователь уже существует')


class CreateBookForm(FlaskForm):
    name = StringField('Введите название книги', validators=[Required(),    Length(1, 64)])
    type = StringField('Введите жанр книги', validators=[Required(), Length(1, 64)])
    description = TextField('Введите описание книги', validators=[Required()])
    price = IntegerField('Укажите цену книги', validators=[Required(), NumberRange(min=0, max=1000000)])
    authors = QuerySelectField('Автор', query_factory=lambda: Author.query.all(), get_label='name')
    image = FileField('Обложка', validators=[Required()])
    submit_book = SubmitField('Добавить')


class CreateAuthorForm(FlaskForm):
    author = StringField('Автор', validators=[Required(), Length(1, 64)])
    submit_author = SubmitField('Добавить')

    def validate_author(self, field):
        if Author.query.filter_by(name=field.data).first():
            raise ValidationError('Такой автор уже есть')


class DeleteBookForm(FlaskForm):
    name = QuerySelectField('Книга', query_factory=lambda: Book.query.all(),
    get_label='book')
    submit_book = SubmitField('Удалить')


class DeleteAuthorForm(FlaskForm):
    name = QuerySelectField('Автор', query_factory=lambda: Author.query.all(),
    get_label='name')
    submit_author = SubmitField('Удалить')


class UpdateBookForm(FlaskForm):
    choose_book = QuerySelectField('Выберите книгу',query_factory=lambda: Book.query.all(),
    get_label='book')
    name = StringField('Изменить название книги', validators=[Required(),    Length(1, 64)])
    type = StringField('Изменить жанр книги', validators=[Required(), Length(1, 64)])
    description = TextField('Изменить описание книги', validators=[Required()])
    price = IntegerField('Изменить цену книги', validators=[Required(), NumberRange(min=0, max=1000000)])
    submit_book = SubmitField('Обновить')


class UpdateAuthorForm(FlaskForm):
    name = QuerySelectField('Автор', query_factory=lambda: Author.query.all(),
    get_label='name')
    author = StringField('Изменить автора', validators=[Required(), Length(1, 64)])
    submit_author = SubmitField('Обновить')


class AddAuthorForm(FlaskForm):
    book = QuerySelectField('Книга', query_factory=lambda: Book.query.all(),
    get_label='book')
    author = QuerySelectField('Автор',query_factory=lambda: Author.query.all(),
    get_label='name')
    submit_add = SubmitField('Добавить')

    def validate_author(self, form):
        if Association.query.filter_by(authors=request.form['author']).first() and Association.query.filter_by(books=request.form['book']).first():
            raise ValidationError('Такой автор уже есть')


class UploadUpdate(FlaskForm):
    book_name = QuerySelectField('Книга', query_factory=lambda: Book.query.all(), get_label='book')
    new_image = FileField('Добавьте файл', validators=[Required()])
    submit_image = SubmitField('Обновить')
