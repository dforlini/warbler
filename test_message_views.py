"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_message_show(self):
        """Can user see message detail-df"""

        #First, add a sample message-df
        m = Message(id=1234, text="a test message", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.get(f"/messages/{m.id}")

            self.assertEqual(resp.status_code, 200)
            self.assertIn(m.text, str(resp.data))

    def test_delete_message(self):
        """Can user delete a message-df"""

        #First, add a sample message-df
        m = Message(id=5678, text="another test message", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        #Make sure the message exists-df
        self.assertIsNotNone(Message.query.get(5678))

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post("/messages/5678/delete")

            #Make sure it redirects-df
            self.assertEqual(resp.status_code, 302)

            #Make sure the message was deleted-df
            self.assertIsNone(Message.query.get(5678))

    def test_unauthorized_message_add(self):
        """When you're not logged in, you can't add messages and are redirected to home page-df"""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "You shouldn't see me"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("You shouldn't see me", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthorized_message_delete(self):
        """When you're not logged in, you can't delete messages and are redirected to home page-df"""

        m = Message(id=1010, text="I'm going to disappear", user_id=self.testuser.id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            resp = c.post("/messages/1010/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
            #Message should still be there after unauthorized attempt to delete-df
            self.assertIsNotNone(Message.query.get(1010))

    def tearDown(self):
        """Clean up any fouled transaction-df"""
        db.session.rollback()