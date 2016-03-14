# -*- coding:utf-8 -*-
from flask import Flask, url_for
from werkzeug import secure_filename
from werkzeug.datastructures import ImmutableMultiDict 

from config import UPLOAD_FOLDER, ICT_DATABASE_URI, ICT_SECRET_KEY

app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI']   = ICT_DATABASE_URI
#app.config['SECRET_KEY']                = ICT_SECRET_KEY
#app.config['UPLOAD_FOLDER']             = UPLOAD_FOLDER

from models import db
#db.init_app(app)

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from datetime import datetime, timedelta

import json
import utils
import os
import time

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='1.226.82.204',debug=True)
