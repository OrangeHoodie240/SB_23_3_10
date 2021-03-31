"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text)

    @classmethod
    def get_users(cls):
        return cls.query.all()

    @classmethod
    def get_user_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def delete_user(cls, id):
        cls.query.filter(cls.id == id).delete()
        db.session.commit()

    @classmethod
    def add_user(cls, first_name, last_name, image_url):
        user = User(first_name=first_name, last_name=last_name, image_url=image_url)
        db.session.add(user)
        db.session.commit()

    @classmethod
    def update_user(cls, id, first_name, last_name, image_url):
        user = cls.get_user_by_id(id)
        user.first_name = first_name
        user.last_name = last_name
        user.image_url = image_url
        db.session.commit() 

    def __repr__(self):
        return f'User(id={self.id}, first_name="{self.first_name}", last_name="{self.last_name}", image_url="{self.image_url}")'
