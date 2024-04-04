import os
from datetime import datetime
from unittest import TestCase
from models import db, User, Message

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"
from app import app

db.create_all()

class MessageModelTestCase(TestCase):
    """Test model for Message-df"""

    def setUp(self):
        """Clean up existing users and messages-df"""
        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction-df"""
        db.session.rollback()

    def test_message_model(self):
        """Does basic model work?"""
        
        m = Message(
            text="This is a test message",
            user_id=self.testuser.id,
        )

        db.session.add(m)
        db.session.commit()

        #User should have one message-df
        self.assertEqual(len(self.testuser.messages), 1)
        self.assertEqual(self.testuser.messages[0].text, "This is a test message")

        #Test the message's attributes-df
        self.assertEqual(m.text, "This is a test message")
        self.assertIsNotNone(m.timestamp)
        self.assertTrue(isinstance(m.timestamp, datetime))
        self.assertEqual(m.user_id, self.testuser.id)

    def test_message_likes(self):
        """Test liking a message-df"""
        m1 = Message(
            text="a warble",
            user_id=self.testuser.id
        )
        m2 = Message(
            text="another warble",
            user_id=self.testuser.id
        )

        user2 = User.signup("unliketestuser", "test2@test.com", "password", None)
        db.session.add_all([m1, m2, user2])
        db.session.commit()

        user2.likes.append(m1)

        db.session.commit()

        l = Message.query.filter(Message.text=="a warble").one()
        self.assertEqual(l.likes[0].id, user2.id)