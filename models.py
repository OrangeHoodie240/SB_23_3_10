"""Models for Blogly."""

from flask_sqlalchemy import SQLAlchemy
import datetime as dt

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
    posts = db.relationship('Post')

    @classmethod
    def get_users(cls):
        return cls.query.all()

    @classmethod
    def get_user_by_id(cls, id):
        return cls.query.get(id)

    @classmethod
    def delete_user(cls, id):
        Post.delete_for(id)
        cls.query.filter(cls.id == id).delete()
        db.session.commit()

    @classmethod
    def add_user(cls, first_name, last_name, image_url):
        user = User(first_name=first_name,
                    last_name=last_name, image_url=image_url)
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


class Post(db.Model):
    __tablename__ = 'posts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    user = db.relationship('User')

    @classmethod
    def add_post(cls, title, content, user_id, created_at=dt.datetime.now()):
        post = Post(title=title, content=content,
                    user_id=user_id, created_at=created_at)
        db.session.add(post)
        db.session.commit()
        return post

    @classmethod
    def get_post_by_id(cls, id):
        return Post.query.get(id)

    @classmethod
    def delete_by_id(cls, id):
        PostTag.delete_for_post(id)
        Post.query.filter(Post.id == id).delete()
        db.session.commit()

    # not commiting since this is more of an accessory method
    @classmethod
    def delete_for(cls, id):
        posts = Post.query.filter(Post.user_id == id).all()
        for post in posts:
            PostTag.delete_for_post(post.id)
            Post.delete_by_id(post.id)

    # does not commit since I am currently using it as an accessory method
    @classmethod
    def update_tags(cls, id, tag_ids):
        post = Post.get_post_by_id(id)
        tags = PostTag.query.filter(PostTag.post_id == id).all()
        tags = {tag.tag_id for tag in tags}

        # remove all tags it already had that arent in the new list of selected tags
        ids_to_del = tags.difference(tag_ids)
        for tag_id in ids_to_del:
            PostTag.delete(id, tag_id)

        # add any new tags
        ids_to_add = tag_ids.difference(tags)
        for tag_id in ids_to_add:
            PostTag.add(id, tag_id)

        return post

    @classmethod
    def update_post(cls, id, title, content, tag_ids):
        post = Post.get_post_by_id(id)
        post.title = title
        post.content = content
        post = Post.update_tags(post.id, tag_ids)
        db.session.commit()


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    posts = db.relationship('Post', secondary='posts_tags', backref='tags')

    @classmethod
    def get_by_id(cls, id):
        return Tag.query.get(id)

    @classmethod
    def add(cls, name):
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
        return tag

    @classmethod
    def update(cls, id, name):
        tag = Tag.get_by_id(id)
        tag.name = name
        db.session.commit()
        return tag

    @classmethod
    def delete(cls, id):
        PostTag.delete_for_tag(id)
        Tag.query.filter(Tag.id == id).delete()
        db.session.commit()
        return id

    @classmethod
    def get_tags(cls):
        return Tag.query.all()


class PostTag(db.Model):
    __tablename__ = 'posts_tags'
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey(
        'posts.id'), nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)

    __table_args__ = (db.UniqueConstraint('post_id', 'tag_id'),)

    @classmethod
    def get_all(cls):
        return PostTag.query.all()

    @classmethod
    def add(cls, post_id, tag_id):
        post_tag = PostTag(post_id=post_id, tag_id=tag_id)
        db.session.add(post_tag)
        db.session.commit()
        return post_tag

    @classmethod
    def delete(cls, post_id, tag_id):
        PostTag.query.filter((PostTag.post_id == post_id)
                             & (PostTag.tag_id == tag_id)).delete()
        db.session.commit()
        return (post_id, tag_id)

    # not commiting since its more of an accessory
    @classmethod
    def delete_for_post(cls, post_id):
        PostTag.query.filter(PostTag.post_id == post_id).delete()
        return post_id

    # not commiting since it is more of an accessory
    @classmethod
    def delete_for_tag(cls, tag_id):
        PostTag.query.filter(PostTag.tag_id == tag_id).delete()
        return tag_id
