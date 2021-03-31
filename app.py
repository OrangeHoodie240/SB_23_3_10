"""Blogly application."""

from flask import Flask, request, render_template, session, flash, redirect
from models import db, connect_db, User
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
def updete_details(id):
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    image_url = request.form.get('image_url', None)
    User.update_user(id, first_name, last_name, image_url)

    return redirect('/')


@app.route('/users/<int:id>/delete', methods=['POST'])
def delete_user(id):
    User.delete_user(id)
    return redirect('/')
