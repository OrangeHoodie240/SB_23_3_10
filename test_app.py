from unittest import TestCase
from models import db, connect_db, User, Post
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
connect_db(app)

db.drop_all()


class TestApp(TestCase):
    def setUp(self):
        db.create_all()
        User.add_user("Flash", "Gordon", None)
        User.add_user('Vultan', 'Hawkman', None)
        User.add_user('Lichking', 'Arthas', None)
        User.add_user('Anduin', 'Lothar', None)

    def test_root_redirects_to_users(self):
        with app.test_client() as client:
            resp = client.get('/')
            print(resp.location)
            self.assertEquals(resp.location, 'http://localhost/users')

    def test_users_displays_users(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            user_names = ['Flash', 'Vultan', 'Lichking', 'Anduin']
            for name in user_names:
                self.assertIn(name, html)

    def test_deletes_user(self):
        id = User.query.filter(User.first_name == "Anduin").one().id
        with app.test_client() as client:
            client.post(f'/users/{id}/delete')

            user = User.get_user_by_id(id)
            self.assertIsNone(user)

    def test_adds_user(self):
        with app.test_client() as client:
            client.post(
                '/new', data={"first_name": "Chuck", "last_name": "Norris", "image_url": None})
            user = User.query.filter(User.first_name == "Chuck").one()

            self.assertIsNotNone(user)
            self.assertEquals(user.last_name, "Norris")

    def test_post_created(self):
        with app.test_client() as client:
            id = User.query.filter(User.first_name == 'Flash').one().id
            title = 'A Funny Story'
            content = 'Not so funny'
            client.post(f'/users/{id}/posts/new',
                        data={"title": title, "content": content})
            post = Post.query.filter(
                (Post.user_id == id) & (Post.title == title)).one()
            self.assertEquals(post.content, content)

    def test_post_deleted(self):
        with app.test_client() as client:
            id = User.query.filter(User.first_name == 'Flash').one().id
            post_id = Post.add_post('test post title', 'test content', id).id
            
            client.post(f'/posts/{post_id}/delete')
            
            post = Post.get_post_by_id(post_id)
            self.assertIsNone(post)

    def tearDown(self):
        db.drop_all()
