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

from models import (
        db, 
        User, 
        Image, 
        Board_category, 
        Board, 
        Comment,
        Blog_post,
        Blog_comment,
        Blog_tag,
        Blog_post_has_blog_tag,
        Event,
        Publication
        )
from forms import (
        SignupForm, 
        SigninForm, 
        WriteBoardForm, 
        CommentForm,
        WriteBlogPostForm,
        BlogCommentForm,
        EventForm,
        PublicationForm
        )
db.init_app(app)

from flask import render_template, flash, redirect, session, url_for, request, g, jsonify
from flask import get_flashed_messages
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta

import json
import utils
import os
import time

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

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
            session['level']    = newuser.level

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
            session['level']    = user.level

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
    session.pop('level', None)

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

def get_comment_by_blog_post_id(blog_post_id):
    comments = Blog_comment.query.filter_by(blog_post_id=blog_post_id).order_by(Blog_comment.created_at.asc()).all()
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

def get_blog_post_information(blog_posts):
    ret = []
    for blog_post in blog_posts:
        user = User.query.filter_by(id=blog_post.user_id).first()
        comments = Blog_comment.query.filter_by(blog_post_id=blog_post.id).all()
        d = {
                'user': user,
                'blog_post': blog_post,
                'comments': comments
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
@login_required
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

@app.route('/edit_board/<int:board_id>')
@login_required
def edit_board(board_id):
    with app.app_context():
        writeBoardForm = WriteBoardForm()
        writeBoardForm.category.choices = get_board_category_list_for_select_form()
    board_category_list = get_board_category_list()
    board = Board.query.filter_by(id=board_id).first()
    writeBoardForm.title.data = board.title
    ret = {
            'writeBoardForm': writeBoardForm,
            'board_category_list': board_category_list,
            'board': board
            }
    return render_template('board_edit.html',ret=ret)

@app.route('/save_edit_board/<int:board_id>',methods=['POST'])
@login_required
def save_edit_board(board_id):
    with app.app_context():
        writeBoardForm = WriteBoardForm()
        writeBoardForm.category.choices = get_board_category_list_for_select_form()
    board_category_list = get_board_category_list()
    board = Board.query.filter_by(id=board_id).first()
    ret = {
            'writeBoardForm': writeBoardForm,
            'board_category_list': board_category_list,
            'board': board
            }
    if request.method == 'POST':
        if not writeBoardForm.validate_on_submit():
            return render_template('board_edit.html',ret=ret)
        else :
            board.title = writeBoardForm.title.data
            board.body  = request.form['board_body']
            board.category_id = writeBoardForm.category.data
            db.session.commit()
            return redirect(url_for('board_detail',board_id=board.id))

@app.route('/delete_board/<int:board_id>',methods=['POST'])
@login_required
def delete_board(board_id):
    comments = Comment.query.filter_by(board_id=board_id).all()
    for comment in comments:
        db.session.delete(comment)
        db.session.commit()
    board = Board.query.filter_by(id=board_id).first()
    db.session.delete(board)
    db.session.commit()
    return json.dumps({'message':'delete success'})

@app.route('/delete_comment/<int:comment_id>',methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return json.dumps({'message':'delete success'})

@app.route('/delete_blog_comment/<int:blog_comment_id>',methods=['POST'])
@login_required
def delete_blog_comment(blog_comment_id):
    comment = Blog_comment.query.filter_by(id=blog_comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return json.dumps({'message':'delete success'})

@app.route('/delete_blog_post/<int:blog_post_id>',methods=['POST'])
@login_required
def delete_blog_post(blog_post_id):
    blog_comments = Blog_comment.query.filter_by(blog_post_id=blog_post_id).all()
    for blog_comment in blog_comments:
        db.session.delete(blog_comment)
        db.session.commit()
    blog_post = Blog_post.query.filter_by(id=blog_post_id).first()
    db.session.delete(blog_post)
    db.session.commit()
    return json.dumps({'message':'delete success'})


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
            print body
            new_board   = Board(title, body, category_id, user_id)
            db.session.add(new_board)
            db.session.commit()
            return redirect(url_for('board_detail',board_id=new_board.id))

@app.route('/blog')
def blog():
    session['nav_page_id'] = 5

    search = False
    per_page = 5
    q = request.args.get('q')
    if q:
        search = True
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    blog_posts = Blog_post.query.order_by(Blog_post.created_at.desc()).limit(per_page).offset((page-1)*per_page)
    total_count = Blog_post.query.count()
    pagination = Pagination(page=page, total=total_count, search=search, record_name='blog_post', per_page=per_page)
    blog_posts = get_blog_post_information(blog_posts)

    blog_tags = Blog_tag.query.order_by(Blog_tag.id.desc()).all()
    recent_blog_posts = Blog_post.query.order_by(Blog_post.created_at.desc()).limit(5)
    recent_blog_comments = Blog_comment.query.order_by(Blog_comment.created_at.desc()).limit(5)

    ret = {
            'blog_posts': blog_posts,
            'pagination': pagination,
            'blog_tags': blog_tags,
            'recent_blog_posts': recent_blog_posts 
            }
    return render_template('blog.html',ret=ret)

@app.route('/blog_post/<int:blog_post_id>')
def blog_post(blog_post_id):
    session['nav_page_id'] = 5
    with app.app_context():
        commentForm = CommentForm()
    blog_post   = Blog_post.query.filter_by(id=blog_post_id).first()
    user        = User.query.filter_by(id=blog_post.user_id).first()
    comments = get_comment_by_blog_post_id(blog_post_id)
    comments = get_comment_information(comments)
    blog_post_has_blog_tags = Blog_post_has_blog_tag.query.filter_by(blog_post_id=blog_post_id).all()
    blog_tags = []
    for blog_post_has_blog_tag in blog_post_has_blog_tags:
        blog_tag = Blog_tag.query.filter_by(id=blog_post_has_blog_tag.blog_tag_id).first()
        blog_tags.append(blog_tag)

    all_blog_tags = Blog_tag.query.order_by(Blog_tag.id.desc()).all()
    recent_blog_posts = Blog_post.query.order_by(Blog_post.created_at.desc()).limit(5)
    recent_blog_comments = Blog_comment.query.order_by(Blog_comment.created_at.desc()).limit(5)

    ret = {
            'commentForm': commentForm,
            'blog_post': blog_post,
            'user' : user,
            'comments': comments,
            'blog_tags': blog_tags,
            'all_blog_tags': all_blog_tags,
            'recent_blog_posts': recent_blog_posts,
            'recent_blog_comments': recent_blog_comments 
            }
    return render_template('blog_post.html',ret=ret)

@app.route('/edit_blog_post/<int:blog_post_id>')
@login_required
def edit_blog_post(blog_post_id):
    session['nav_page_id'] = 5
    with app.app_context():
        writeBlogPostForm = WriteBlogPostForm()
    blog_post = Blog_post.query.filter_by(id=blog_post_id).first()
    writeBlogPostForm.title.data = blog_post.title
    blog_post_has_blog_tags = Blog_post_has_blog_tag.query.filter_by(blog_post_id=blog_post_id).all()
    writeBlogPostForm.tags.data = ''
    for blog_post_has_blog_tag in blog_post_has_blog_tags:
        tag = Blog_tag.query.filter_by(id=blog_post_has_blog_tag.blog_tag_id).first()
        writeBlogPostForm.tags.data += tag.tag_name
        if blog_post_has_blog_tag != blog_post_has_blog_tags[-1]:
            writeBlogPostForm.tags.data += ', '
    ret = {
            'writeBlogPostForm': writeBlogPostForm,
            'blog_post': blog_post
            }
    return render_template('edit_blog_post.html',ret=ret)

@app.route('/save_edit_blog_post/<int:blog_post_id>',methods=['POST'])
def save_edit_blog_post(blog_post_id):
    with app.app_context():
        writeBlogPostForm = WriteBlogPostForm()
    blog_post = Blog_post.query.filter_by(id=blog_post_id).first()
    blog_post_has_blog_tags = Blog_post_has_blog_tag.query.filter_by(blog_post_id=blog_post_id).all()
    ret = {
            'writeBlogPostForm': writeBlogPostForm,
            'blog_post': blog_post
            }
    if request.method == 'POST':
        if not writeBlogPostForm.validate_on_submit():
            return render_template('edit_blog_post.html',ret=ret)
        else:
            blog_post.title       = writeBlogPostForm.title.data
            blog_post.body        = request.form['board_body']
            db.session.commit()
            tags        = writeBlogPostForm.tags.data
            blog_post_has_blog_tags = Blog_post_has_blog_tag.query.filter_by(blog_post_id=blog_post.id).all()
            for blog_post_has_blog_tag in blog_post_has_blog_tags:
                db.session.delete(blog_post_has_blog_tag)
                db.session.commit()
            if tags:
                tags = tags.split(',')
                for tag in tags:
                    blog_tag = Blog_tag.query.filter_by(tag_name=tag.strip()).first()
                    if not blog_tag:
                        blog_tag = Blog_tag(tag.strip())
                        db.session.add(blog_tag)
                        db.session.commit()
                    blog_post_has_blog_tag = Blog_post_has_blog_tag(blog_post.id,blog_tag.id)
                    db.session.add(blog_post_has_blog_tag)
                    db.session.commit()
            return redirect(url_for('blog_post',blog_post_id=blog_post.id))


@app.route('/save_blog_post',methods=['POST'])
def save_blog_post():
    with app.app_context():
        writeBlogPostForm = WriteBlogPostForm()
    ret = {
            'writeBlogPostForm': writeBlogPostForm
            }
    if request.method == 'POST':
        if not writeBlogPostForm.validate_on_submit():
            return render_template('write_blog_post.html',ret=ret)
        else:
            title       = writeBlogPostForm.title.data
            user_id     = session['user_id']
            body        = request.form['board_body']
            new_blog_post = Blog_post(title, body, user_id)
            db.session.add(new_blog_post)
            db.session.commit()
            tags        = writeBlogPostForm.tags.data
            if tags:
                tags = tags.split(',')
                for tag in tags:
                    blog_tag = Blog_tag.query.filter_by(tag_name=tag.strip()).first()
                    if not blog_tag:
                        blog_tag = Blog_tag(tag.strip())
                        db.session.add(blog_tag)
                        db.session.commit()
                    blog_post_has_blog_tag = Blog_post_has_blog_tag(new_blog_post.id,blog_tag.id)
                    db.session.add(blog_post_has_blog_tag)
                    db.session.commit()
            return redirect(url_for('blog_post',blog_post_id=new_blog_post.id))

@app.route('/write_blog_post',methods=['GET'])
@login_required
def write_blog_post():
    session['nav_page_id'] = 5
    with app.app_context():
        writeBlogPostForm = WriteBlogPostForm()
    ret = {
            'writeBlogPostForm': writeBlogPostForm
            }
    return render_template('write_blog_post.html',ret=ret)

@app.route('/post_image_save',methods=['POST'])
def post_image_save():
    file = request.files['file']
    filename = secure_filename(file.filename)
    if utils.allowedFile(filename):
        directory_name = utils.convert_email_to_directory_name(session['email'])
        directory_url = os.path.join(app.config['UPLOAD_FOLDER'],directory_name)
        utils.createDirectory(directory_url)
#        file_path = os.path.join(directory_url,filename)
        file_path = os.path.join(directory_url,filename.split('.')[0]+'-'+str(datetime.now()).replace(' ','-')+'.'+filename.split('.')[-1])
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

@app.route('/save_blog_comment',methods=['POST'])
def save_blog_comment():
    with app.app_context():
        commentForm = CommentForm()
    blog_post_id = int(request.args.get('blog_post_id'))
    if request.method =='POST':
        if not commentForm.validate():
            blog_post   = Blog_post.query.filter_by(id=blog_post_id).first()
            user        = User.query.filter_by(id=blog_post.user_id).first()
            comments = get_comment_by_blog_post_id(blog_post_id)
            comments = get_comment_information(comments)

            ret = {
                    'commentForm': commentForm,
                    'blog_post': blog_post,
                    'user' : user,
                    'comments': comments
                    }
            return render_template('blog_post.html',ret=ret)
        else :
            body = commentForm.body.data
            user_id = session['user_id']
            comment = Blog_comment(body, user_id, blog_post_id)
            db.session.add(comment)
            db.session.commit()
            return redirect(url_for('blog_post',blog_post_id=blog_post_id))


@app.route('/activity')
def activity():
    session['nav_page_id'] = 2
    return render_template('activity.html')

@app.route('/write_activity')
def write_activity():
    session['nav_page_id'] = 2
    with app.app_context():
        eventForm = EventForm()

    ret = {
            'eventForm': eventForm
            }
    return render_template('write_activity.html',ret=ret)

@app.route('/save_activity',methods=['POST'])
@login_required
def save_activity():
    session['nav_page_id'] = 2
    with app.app_context():
        eventForm = EventForm()
    ret = {
            'eventForm': eventForm
            }
    if request.method == 'POST':
        if not eventForm.validate():
            return render_template('write_activity.html',ret=ret)
        else:
            if eventForm.validate_on_submit():
                filename = secure_filename(eventForm.filename.data.filename)
                if utils.allowedFile(filename):
                    directory_name = utils.convert_email_to_directory_name(session['email'])
                    directory_url = os.path.join(app.config['UPLOAD_FOLDER'],directory_name)
                    utils.createDirectory(directory_url)
                    file_path = os.path.join(directory_url,filename.split('.')[0]+'-'+str(datetime.now()).replace(' ','-')+'.'+filename.split('.')[-1])
                    eventForm.filename.data.save(file_path)
                    image = Image(file_path, session['user_id'])
                    db.session.add(image)
                    db.session.commit()

                    title = eventForm.title.data
                    body = request.form['board_body']
                    user_id = session['user_id']
                    image_id = image.id

                    new_event = Event(title,body,user_id,image_id)
                    db.session.add(new_event)
                    db.session.commit()
                    return redirect(url_for('activity'))
                else:
                    return json.dumps({'status':'error','message':'extention error'})

@app.route('/databook')
def databook():
    session['nav_page_id'] = 3
    return render_template('databook.html')

@app.route('/test')
def test():
    return render_template('test.html')

if __name__ == '__main__':
    app.run(host='58.227.42.161',debug=True)
