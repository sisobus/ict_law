#!/usr/bin/python
#-*- coding:utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__   = 'user'
    id              = db.Column(db.Integer, primary_key=True)
    username        = db.Column(db.String(200))
    email           = db.Column(db.String(200), unique=True)
    password        = db.Column(db.String(54))
    created_at      = db.Column(db.DateTime)
    level           = db.Column(db.Integer, default=0)

    def __init__(self, username, email, password, level=0):
        self.username   = username
        self.email      = email
        self.set_password(password)
        self.created_at = datetime.now()
        self.level      = level

    def set_password(self, password):
        self.password   = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Image(db.Model):
    __tablename__       = 'image'
    id                  = db.Column(db.Integer, primary_key=True)
    image_path          = db.Column(db.String(300))
    created_at          = db.Column(db.DateTime)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, image_path, user_id):
        self.image_path = image_path
        self.created_at = datetime.now()
        self.user_id    = user_id

class Board_category(db.Model):
    __tablename__       = 'board_category'
    id                  = db.Column(db.Integer, primary_key=True)
    category_name       = db.Column(db.String(200))

    def __init__(self, category_name):
        self.category_name = category_name

class Board(db.Model):
    __tablename__       = 'board'
    id                  = db.Column(db.Integer, primary_key=True)
    title               = db.Column(db.String(200))
    body                = db.Column(db.String(3000))
    created_at          = db.Column(db.DateTime)
    category_id         = db.Column(db.Integer, db.ForeignKey('board_category.id'))
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, category_id, user_id):
        self.title      = title
        self.body       = body
        self.created_at = datetime.now()
        self.category_id= category_id
        self.user_id    = user_id

class Comment(db.Model):
    __tablename__       = 'comment'
    id                  = db.Column(db.Integer, primary_key=True)
    body                = db.Column(db.String(200))
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at          = db.Column(db.DateTime)
    board_id            = db.Column(db.Integer, db.ForeignKey('board.id'))

    def __init__(self, body, user_id, board_id):
        self.body       = body
        self.user_id    = user_id 
        self.created_at = datetime.now()
        self.board_id   = board_id
