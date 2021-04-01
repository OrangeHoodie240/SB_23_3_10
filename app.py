"""Blogly application."""

from flask import Flask, request, render_template, session, flash, redirect
from models import db, connect_db, User, Post
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Something is a secret to someone'


app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

debug = DebugToolbarExtension(app)


@app.route('/')
def index():
    return redirect('/users')


@app.route('/users')
def users():
    return render_template('index.html', users=User.get_users())


@app.route('/new')
def add_user_get():
    return render_template('add_user.html')


@app.route('/new', methods=["POST"])
def add_user():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url', None)
    User.add_user(first_name, last_name, image_url)

    return redirect('/')


@app.route('/users/<int:id>')
def details(id):
    user = User.get_user_by_id(id)
    return render_template('details.html', user=user)


@app.route('/users/<int:id>/edit')
def edit_details(id):
    user = User.get_user_by_id(id)
    return render_template('edit-details.html', user=user)


@app.route('/users/<int:id>/edit', methods=['POST'])
def update_details(id):
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url', None)
    User.update_user(id, first_name, last_name, image_url)

    return redirect('/')


@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    User.delete_user(id)
    return redirect('/')


@app.route('/users/<int:id>/posts/new')
def add_post_form(id):
    return render_template('post_form.html', id=id)


@app.route('/users/<int:id>/posts/new', methods=['POST'])
def commit_post(id):
    title = request.form.get('title')
    content = request.form.get('content')
    Post.add_post(title, content, id)

    return redirect(f'/users/{id}')


@app.route('/posts/<int:id>')
def show_post(id):
    post = Post.get_post_by_id(id)
    return render_template('view_post.html', post=post)


@app.route('/posts/<int:id>/edit')
def edit_post_form(id):
    post = Post.get_post_by_id(id)
    return render_template('edit_post.html', post=post)

@app.route('/posts/<int:id>/edit', methods=['POST'])
def commit_edit_post(id):
    title = request.form.get('title')
    content = request.form.get('content')
    Post.update_post(id, title, content)
    return redirect(f'/posts/{id}')


@app.route('/posts/<int:id>/delete', methods=['POST'])
def delete_post(id):
    post = Post.get_post_by_id(id)
    user_id = post.user_id
    Post.delete_by_id(post.id)
    return redirect(f'/users/{user_id}')
