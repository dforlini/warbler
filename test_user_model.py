"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_follows(self):
        u1 = User.signup("unfollowed", "test1@test.com", "password", None)
        u1.id = 1111
        u2 = User.signup("followed", "test2@test.com", "password", None)
        u2.id = 2222
        db.session.add_all([u1, u2])
        db.session.commit()

        u1.following.append(u2)
        db.session.commit()

        self.assertEqual(len(u2.followers), 1)
        self.assertEqual(len(u2.following), 0)
        self.assertEqual(len(u1.followers), 0)
        self.assertEqual(len(u1.following), 1)

        self.assertEqual(u2.followers[0].id, u1.id)

    def test_user_signup(self):
        u_test = User.signup("testsignup", "testsignup@test.com", "password", None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testsignup")
        self.assertEqual(u_test.email, "testsignup@test.com")
        self.assertNotEqual(u_test.password, "password")
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_authentication(self):
        u = User.authenticate(self.u.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid)

        wrong_username = User.authenticate("wrongusername", "password")
        self.assertFalse(wrong_username)

        wrong_password = User.authenticate(self.u.username, "wrongpassword")
        self.assertFalse(wrong_password)
        
    