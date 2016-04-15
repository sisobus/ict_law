#-*- coding:utf-8 -*-
from flask.ext.wtf import Form,widgets
from wtforms import widgets,TextField,TextAreaField, SubmitField, validators, ValidationError, PasswordField, FileField, RadioField, SelectField, SelectMultipleField, BooleanField
from models import db, User, Board_category
import utils
from flask.ext.sqlalchemy import SQLAlchemy
from flask import Flask, current_app

class SignupForm(Form):
    username    = TextField('username', [validators.Required(u'닉네임 혹은 이름을 적어주세요')])
    email       = TextField('email', [validators.Required(u'이메일을 입력해주세요'), validators.Email(u'꼭 이메일 주소로 입력해주세요')])
    password    = PasswordField('password', [validators.Required(u'비밀번호를 입력해주세요')])
    agree_check = BooleanField('agree_check', [validators.Required(u'동의하셔야 회원가입이 됩니다.')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user:
            self.email.errors.append(u'해당이메일이 이미 존재합니다.')
            return False
        else :
            return True

class SigninForm(Form):
    email       = TextField('email', [validators.Required('please enter your email')])
    password    = PasswordField('password', [validators.Required('please enter your password')])
    auto_login  = BooleanField('auto_login')

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(email = self.email.data.lower()).first()
        if user and user.check_password(self.password.data):
            return True
        else:
            self.email.errors.append(u'이메일 혹은 비밀번호가 틀렸습니다.')
            return False

class NonValidatingSelectMultipleField(SelectMultipleField):
    """
    Attempt to make an open ended select multiple field that can accept dynamic
    choices added by the browser.
    """
    def pre_validate(self, form):
        pass

class NonValidatingSelectField(SelectField):
    def pre_validate(self, form):
        pass

class WriteBoardForm(Form):
    title       = TextField('title', [validators.Required(u'글 제목은 필수입니다.')]) 
    category    = SelectField('category',coerce=int)

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True

class CommentForm(Form):
    body        = TextField('body', [validators.Required(u'댓글 입력은 필수입니다.')])

    def __init__(self, *args, **kargs):
        Form.__init__(self, *args, **kargs)

    def validate(self):
        if not Form.validate(self):
            return False
        return True
