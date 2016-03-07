#!/usr/bin/python
#-*- coding:utf-8 -*-
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash

db = SQLAlchemy()
