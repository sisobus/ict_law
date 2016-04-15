# -*- coding:utf-8 -*-
from flask import Flask, url_for
from flask.ext.paginate import Pagination
from werkzeug import secure_filename
from werkzeug.datastructures import ImmutableMultiDict 
from sqlalchemy import func

from config import UPLOAD_FOLDER, ICT_DATABASE_URI, ICT_SECRET_KEY

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']   = ICT_DATABASE_URI
app.config['SECRET_KEY']                = ICT_SECRET_KEY
app.config['UPLOAD_FOLDER']             = UPLOAD_FOLDER

from models import db, User, Image, Board_category, Board, Comment
from forms import SignupForm, SigninForm, WriteBoardForm, CommentForm
db.init_app(app)

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
    session['nav_page_id'] = 0
    return render_template('home.html')

@app.route('/register',methods=['GET'])
def register():
    session['nav_page_id'] = -1
    with app.app_context():
        signinForm = SigninForm()
        signupForm = SignupForm()

    ret = {
            'signinForm': signinForm,
            'signupForm': signupForm
            }
    return render_template('register.html',ret=ret)

@app.route('/signup',methods=['POST'])
def signup():
    session['nav_page_id'] = -1
    with app.app_context():
        signinForm = SigninForm()
        signupForm = SignupForm()
    ret = {
            'signinForm': signinForm,
            'signupForm': signupForm
            }
    if request.method == 'POST':
        if not signupForm.validate():
            return render_template('register.html',ret=ret)
        else :
            username    = signupForm.username.data
            email       = signupForm.email.data
            password    = signupForm.password.data
            newuser     = User(username, email, password)
            db.session.add(newuser)
            db.session.commit()

            session['username'] = username
            session['email']    = email
            session['user_id']  = newuser.id
            session['logged_in']= True

            return redirect(url_for('home'))

@app.route('/signin',methods=['POST'])
def signin():
    session['nav_page_id'] = -1
    with app.app_context():
        signinForm = SigninForm()
        signupForm = SignupForm()
    ret = {
            'signinForm': signinForm,
            'signupForm': signupForm
            }
    if request.method == 'POST':
        if not signinForm.validate():
            return render_template('register.html',ret=ret)
        else :
            email       = signinForm.email.data
            password    = signinForm.password.data
            auto_login  = signinForm.auto_login.data
            user        = User.query.filter_by(email=email.lower()).first()
            session['username'] = user.username
            session['email']    = user.email
            session['user_id']  = user.id
            session['logged_in']= True

            return redirect(url_for('home'))


@app.route('/signout')
def signout():
    session['nav_page_id'] = -1
    if 'logged_in' not in session:
        return redirect(url_for('main'))
    session.pop('username', None)
    session.pop('email', None)
    session.pop('user_id', None)
    session.pop('logged_in', None)

    return redirect(url_for('home'))

def get_board_category_list():
    ret = []
    with app.app_context():
        board_categories = Board_category.query.order_by(Board_category.id.asc()).all()
        for board_category in board_categories:
            d = {
                    'id': board_category.id,
                    'category_name': board_category.category_name
                    }
            ret.append(d)
    return ret

def get_board_category_list_for_select_form():
    ret = []
    with app.app_context():
        board_categories = Board_category.query.order_by(Board_category.id.asc()).all()
        for board_category in board_categories:
            if board_category.id == 0:
                category_name = u'카테고리'
            else :
                category_name = board_category.category_name
            ret.append((board_category.id, category_name))
    return ret

def get_board_information(boards):
    ret = []
    for board in boards:
        user = User.query.filter_by(id=board.user_id).first()
        comments = Comment.query.filter_by(board_id=board.id).all()
        d = {
                'user': user,
                'board': board,
                'comments': comments
                }
        ret.append(d)
    return ret

def get_comment_by_board_id(board_id):
    comments = Comment.query.filter_by(board_id=board_id).order_by(Comment.created_at.asc()).all()
    return comments

def get_comment_information(comments):
    ret = []
    for comment in comments:
        user = User.query.filter_by(id=comment.user_id).first()
        d = {
                'comment': comment,
                'user': user
                }
        ret.append(d)
    return ret

@app.route('/board_detail/<int:board_id>')
def board_detail(board_id):
    session['nav_page_id'] = 4
    with app.app_context():
        commentForm = CommentForm()
    board_category_list = get_board_category_list()
    board = Board.query.filter_by(id=board_id).first()
    user  = User.query.filter_by(id=board.user_id).first()
    board_category = Board_category.query.filter_by(id=board.category_id).first()
    comments = get_comment_by_board_id(board_id)
    comments = get_comment_information(comments)

    ret = {
            'commentForm': commentForm,
            'board_category_list': board_category_list,
            'board': board,
            'user' : user,
            'board_category': board_category,
            'comments': comments
            }
    return render_template('board_detail.html',ret=ret)

@app.route('/save_comment',methods=['POST'])
def save_comment():
    with app.app_context():
        commentForm = CommentForm()
    board_id = int(request.args.get('board_id'))
    if request.method =='POST':
        if not commentForm.validate():
            board_category_list = get_board_category_list()
            board = Board.query.filter_by(id=board_id).first()
            user  = User.query.filter_by(id=board.user_id).first()
            board_category = Board_category.query.filter_by(id=board.category_id).first()

            ret = {
                    'commentForm': commentForm,
                    'board_category_list': board_category_list,
                    'board': board,
                    'user' : user,
                    'board_category': board_category
                    }
            return render_template('board_detail.html',ret=ret)
        else :
            body = commentForm.body.data
            user_id = session['user_id']
            comment = Comment(body, user_id, board_id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('board_detail',board_id=board_id))

# free_board
@app.route('/board/<int:category_id>')
def board(category_id):
    session['nav_page_id'] = 4
    board_category_list = get_board_category_list()
    cur_board_category  = board_category_list[int(category_id)]

    search = False
    per_page = 20
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    if category_id == 0:
        boards = Board.query.order_by(Board.created_at.desc()).limit(per_page).offset((page-1)*per_page)
        total_count = Board.query.count()
    else :
        boards = Board.query.filter_by(category_id=category_id).order_by(Board.created_at.desc()).limit(per_page).offset((page-1)*per_page)
        total_count = Board.query.filter_by(category_id=category_id).count()
    pagination = Pagination(page=page, total=total_count, search=search, record_name='board', per_page=per_page)
    boards = get_board_information(boards)


    ret = {
            'board_category_list': board_category_list,
            'board_category': cur_board_category,
            'boards': boards,
            'pagination': pagination
            }
    return render_template('board.html',ret=ret)

@app.route('/write_board',methods=['GET'])
def write_board():
    session['nav_page_id'] = 4
    with app.app_context():
        writeBoardForm = WriteBoardForm()
        writeBoardForm.category.choices = get_board_category_list_for_select_form()

    board_category_list = get_board_category_list()
    ret = {
            'writeBoardForm': writeBoardForm,
            'board_category_list': board_category_list
            }
    return render_template('write_board.html',ret=ret)

@app.route('/save_board',methods=['POST'])
def save_board():
    with app.app_context():
        writeBoardForm = WriteBoardForm()
        writeBoardForm.category.choices = get_board_category_list_for_select_form()
    board_category_list = get_board_category_list()
    ret = {
            'writeBoardForm': writeBoardForm,
            'board_category_list': board_category_list
            }
    if request.method == 'POST':
        if not writeBoardForm.validate_on_submit():
            print writeBoardForm.category.data
            return render_template('write_board.html',ret=ret)
        else :
            title       = writeBoardForm.title.data
            category_id = writeBoardForm.category.data
            user_id     = session['user_id']
            body        = request.form['board_body']
            new_board   = Board(title, body, category_id, user_id)
            db.session.add(new_board)
            db.session.commit()
            return redirect(url_for('board_detail',board_id=new_board.id))



@app.route('/post_image_save',methods=['POST'])
def post_image_save():
    file = request.files['file']
    filename = secure_filename(file.filename)
    if utils.allowedFile(filename):
        directory_name = utils.convert_email_to_directory_name(session['email'])
        directory_url = os.path.join(app.config['UPLOAD_FOLDER'],directory_name)
        utils.createDirectory(directory_url)
        file_path = os.path.join(directory_url,filename)
        file.save(file_path)
        image = Image(file_path, session['user_id'])
        db.session.add(image)
        db.session.commit()
    else:
        return json.dumps({'status':'error','message':'extention error'})
    print file.filename
    print file_path
    d = {
        'status': 'OK',
        'url': utils.get_image_path(image.image_path)
            }
    return json.dumps(d)

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='58.227.42.161',debug=True)
