"""Blogly application."""

from flask import Flask, request, render_template, session, flash, redirect
from models import db, connect_db, User, Post, Tag, PostTag
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
    tags = Tag.get_tags()
    return render_template('post_form.html', id=id, tags=tags)


@app.route('/users/<int:id>/posts/new', methods=['POST'])
def commit_post(id):
    title = request.form.get('title')
    content = request.form.get('content')
    post = Post.add_post(title, content, id)

    tags = Tag.get_tags()
    for tag in tags:
        if(request.form.get(tag.name, None) is not None):
            PostTag.add(post.id, tag.id)

    return redirect(f'/users/{id}')


@app.route('/posts/<int:id>')
def show_post(id):
    post = Post.get_post_by_id(id)
    return render_template('view_post.html', post=post)


@app.route('/posts/<int:id>/edit')
def edit_post_form(id):
    post = Post.get_post_by_id(id)
    tag_names = [ tag.name for tag in post.tags]
    tags = Tag.get_tags()
    return render_template('edit_post.html', post=post, tag_names=tag_names, tags=tags)


@app.route('/posts/<int:id>/edit', methods=['POST'])
def commit_edit_post(id):
    title = request.form.get('title')
    content = request.form.get('content')

    tags = set()
    for tag in Tag.get_tags():
        if(request.form.get(tag.name, None) is not None):
            tags.add(tag.id)

    Post.update_post(id, title, content, tags)
    return redirect(f'/posts/{id}')


@app.route('/posts/<int:id>/delete', methods=['POST'])
def delete_post(id):
    post = Post.get_post_by_id(id)
    user_id = post.user_id
    Post.delete_by_id(post.id)
    return redirect(f'/users/{user_id}')


@app.route('/tags')
def get_tags():
    tags = Tag.get_tags()
    return render_template('tags.html', tags=tags)


@app.route('/tags/<int:id>')
def tag_details(id):
    tag = Tag.get_by_id(id)
    return render_template('tag_details.html', tag=tag)


@app.route('/tags/new')
def add_tag():
    return render_template('new_tag_form.html')


@app.route('/tags/new', methods=["POST"])
def add_tag_commit():
    name = request.form.get('name')
    Tag.add(name)
    return redirect('/tags')


@app.route('/tags/<int:id>/edit')
def edit_tag(id):
    tag = Tag.get_by_id(id)
    return render_template('tag_edit_form.html', tag=tag)


@app.route('/tags/<int:id>/edit', methods=['POST'])
def edit_tag_commit(id):
    name = request.form.get('name')
    Tag.update(id, name)
    return redirect('/tags')


@app.route('/tags/<int:id>/delete', methods=['POST'])
def delete_tag(id):
    Tag.delete(id)
    return redirect('/tags')
