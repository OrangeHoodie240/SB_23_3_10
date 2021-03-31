from unittest import TestCase
from models import db, connect_db, User
from app import app

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///test_blogly'
app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
connect_db(app)

db.drop_all()
db.create_all()


class TestApp(TestCase):
    def setUp(self):
        User.query.delete()
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
            client.post('/new', data={"first_name": "Chuck", "last_name": "Norris", "image_url": None})
            user = User.query.filter(User.first_name == "Chuck").one()

            self.assertIsNotNone(user)
            self.assertEquals(user.last_name, "Norris")

    def tearDown(self):
        db.session.rollback()
