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

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

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
    body                = db.Column(db.Text)
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

class Blog_post(db.Model):
    __tablename__       = 'blog_post'
    id                  = db.Column(db.Integer, primary_key=True)
    title               = db.Column(db.String(500))
    body                = db.Column(db.Text)
    created_at          = db.Column(db.DateTime)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, user_id):
        self.title      = title
        self.body       = body
        self.created_at = datetime.now()
        self.user_id    = user_id

class Blog_comment(db.Model):
    __tablename__       = 'blog_comment'
    id                  = db.Column(db.Integer, primary_key=True)
    body                = db.Column(db.String(1000))
    created_at          = db.Column(db.DateTime)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'))
    blog_post_id        = db.Column(db.Integer, db.ForeignKey('blog_post.id'))

    def __init__(self, body, user_id, blog_post_id):
        self.body       = body
        self.created_at = datetime.now()
        self.user_id    = user_id
        self.blog_post_id = blog_post_id 

class Blog_tag(db.Model):
    __tablename__       = 'blog_tag'
    id                  = db.Column(db.Integer, primary_key=True)
    tag_name            = db.Column(db.String(200))

    def __init__(self, tag_name):
        self.tag_name   = tag_name

class Blog_post_has_blog_tag(db.Model):
    __tablename__       = 'blog_post_has_blog_tag'
    blog_post_id        = db.Column(db.Integer, primary_key=True)
    blog_tag_id         = db.Column(db.Integer, primary_key=True)

    def __init__(self, blog_post_id, blog_tag_id):
        self.blog_post_id   = blog_post_id
        self.blog_tag_id    = blog_tag_id

class Event(db.Model):
    __tablename__       = 'event'
    id                  = db.Column(db.Integer, primary_key=True)
    title               = db.Column(db.String(500))
    body                = db.Column(db.Text)
    created_at          = db.Column(db.DateTime)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id            = db.Column(db.Integer, db.ForeignKey('image.id'))

    def __init__(self, title, body, user_id, image_id):
        self.title      = title
        self.body       = body
        self.created_at = datetime.now()
        self.user_id    = user_id
        self.image_id   = image_id

class Publication(db.Model):
    __tablename__       = 'publication'
    id                  = db.Column(db.Integer, primary_key=True)
    title               = db.Column(db.String(500))
    body                = db.Column(db.Text)
    created_at          = db.Column(db.DateTime)
    user_id             = db.Column(db.Integer, db.ForeignKey('user.id'))
    image_id            = db.Column(db.Integer, db.ForeignKey('image.id'))

    def __init__(self, title, body, user_id, image_id):
        self.title      = title
        self.body       = body
        self.created_at = datetime.now()
        self.user_id    = user_id
        self.image_id   = image_id
