import os
from unittest import TestCase
from models import db, User
from app import app

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class UserViewTestCase(TestCase):
    """Test views for users-df"""

    def setUp(self):
        """Create test client and sample data-df"""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="password",
                                    image_url=None)
        db.session.commit()

    def tearDown(self):
        """Clean up fouled transactions-df"""

        db.session.rollback()

    def test_signup(self):
        """Can user sign up-df"""

        with self.client as client:
            resp = client.post('/signup', data={"username": "testuser2", "email": "test2@test.com",
                                                "password": "password2", "image_url": ""}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            #Make sure it redirects to the home page-df
            self.assertEqual(resp.status_code, 200)
            self.assertIn('You are successfully signed up', html)

            #Make sure user is actually inserted into the database-df
            user = User.query.filter_by(username="testuser2").first()
            self.assertIsNotNone(user)

    def test_login(self):
        """Can user log in-df"""

        with self.client as client:
            resp = client.post('/login', data={"username": "testuser", "password": "password"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Hello, testuser!', html)

    def test_logout(self):
        """Can user log out-df"""

        with self.client as client:
            #Log in first-df
            client.post('/login', data={"username": "testuser", "password": "password"})

            resp = client.get('/logout', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('You have successfully logged out', html)

    def test_user_profile_update(self):
        """Can user update their profile-df"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess['curr_user'] = self.testuser.id

            resp = client.post('/users/profile', data={"username": "testuserupdated",
                                                       "email": "testupdated@test.com",
                                                       "image_url": "",
                                                       "password": "password"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Profile updated!', html)

            user = User.query.get(self.testuser.id)
            self.assertEqual(user.username, "testuserupdated")
            self.assertEqual(user.email, "testupdated@test.com")