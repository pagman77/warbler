"""Test message model."""
import os
# from typing_extensions import TypeVarTuple
from unittest import TestCase
from sqlalchemy.exc import IntegrityError
from models import db, User, Message, Follows, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        u = User.signup(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD",
            image_url=""
        )

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD2",
            image_url=""
        )


        db.session.add_all([u,u2])
        db.session.commit()

        u.messages.append(
            Message(text="This is test msg one.")
        )

        u2.messages.append(
            Message(text="This is test msg two.")
        )

        db.session.commit()

        self.test_msg1 = u.messages[0]
        self.test_msg2 = u2.messages[0]

        self.u_id = u.id
        self.u2_id = u2.id

    def tearDown(self):
        """Remove all session commits."""
        db.session.rollback()

    def test_msg_repr(self):
        """Does repr return expected message."""

        u = User.query.get(self.u_id)
        msg = u.messages[0]

        self.assertEqual(f"<Message #{msg.id}: {msg.text} Written by: {msg.user.username}>",
                        f"<Message #{msg.id}: This is test msg one. Written by: testuser>")

    def test_msg_like(self):
        """Test that user added to message's likes list after liking"""

        u = User.query.get(self.u_id)
        u2 = User.query.get(self.u2_id)

        u.liked_messages.append(self.test_msg2)
        db.session.commit()
        #test msg in/not in user's liked_messages
        self.assertIn(self.test_msg2, u.liked_messages)
        self.assertNotIn(self.test_msg2, u2.liked_messages)
        #test user is in/not in message's users_liked
        self.assertIn(u, self.test_msg2.users_liked)
        self.assertNotIn(u2, self.test_msg2.users_liked)

    def test_msg_delete(self):
        """tests only one message is removed on deletion"""

        u = User.query.get(self.u_id)
        u2 = User.query.get(self.u2_id)

        u.messages.append(
            Message(text="This is test msg three.")
        )

        db.session.delete(self.test_msg1)
        db.session.commit()

        self.assertTrue(len(u.messages), 1)
        #tests u2 not affected by u msg delete
        self.assertTrue(len(u2.messages), 1)




