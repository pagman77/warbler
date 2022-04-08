"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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


class UserModelTestCase(TestCase):
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

        self.u_id = u.id
        self.u2_id = u2.id

    def tearDown(self):
        """Remove all session commits."""
        db.session.rollback()


    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.get(self.u_id)

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does repr return expected information?"""

        u = User.query.get(self.u_id)

        self.assertEqual(f"<User #{u.id}: {u.username}, {u.email}>",
            f"<User #{self.u_id}: testuser, test@test.com>")


    def test_is_following_user(self):
        """Does is_following successfully detect
        when user1 is following user2?"""

        u = User.query.get(self.u_id)
        u2 = User.query.get(self.u2_id)

        u.following.append(u2)
        u2.following.append(u)

        self.assertTrue(u.is_following(u2))
        self.assertTrue(u2.is_following(u))


    def test_is_not_following_user(self):
        """Does is_following successfully detect
        when user1 is not following user2?"""

        u = User.query.get(self.u_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u.is_following(u2))
        self.assertFalse(u2.is_following(u))

    def test_is_followed_by_user(self):
        """Does is_followed_by successfully detect
        when user1 is followed by user2?"""

        u = User.query.get(self.u_id)
        u2 = User.query.get(self.u2_id)

        u.following.append(u2)
        u2.following.append(u)

        self.assertTrue(u.is_followed_by(u2))
        self.assertTrue(u2.is_followed_by(u))


    def test_is_not_followed_by_user(self):
        """Does is_followed_by successfully detect
        when user1 is not followed by user2?"""

        u = User.query.get(self.u_id)
        u2 = User.query.get(self.u2_id)

        self.assertFalse(u.is_followed_by(u2))
        self.assertFalse(u2.is_followed_by(u))

    def test_user_signup_success(self):
        """Does User.signup successfully create
        a new user given valid credentials?"""
        #add test to check for pw hashing, itemize validating each piece of info
        #pswds begin w/ $2b$

        u = User.signup(
            username="test3",
            password="superHash",
            email="donthackmyhash@test.com",
            image_url="")

        users = User.query.all()

        self.assertIn(u, users)


    def test_user_signup_fail(self):
        """Does User.signup fail to create a new user if any of the
        validations (eg uniqueness, non-nullable fields) fail?"""

        ### TEST MISSING DATA###
        with self.assertRaises(TypeError):
            User.signup(password="superHash", email="donthackmyhash@test.com", image_url="")

        with self.assertRaises(TypeError):
            User.signup(username="test3", email="donthackmyhash@test.com", image_url="")

        with self.assertRaises(TypeError):
            User.signup(username="test3", password="superHash", image_url="")


        ### TEST DUPLICATE USER###
        u = User.signup(
            username="testuser",
            password="superHash",
            email="donthackmyhash@test.com",
            image_url="")

        with self.assertRaises(IntegrityError):
            db.session.commit()


    def test_user_authenticate_method_success(self):
        """Does User.authenticate successfully return
        a user when given a valid username and password?"""

        u = User.query.get(self.u_id)
        auth_u = User.authenticate("testuser", "HASHED_PASSWORD")

        self.assertEqual(u, auth_u)


    def test_user_authenticate_method_un_fail(self):
        """Does User.authenticate fail to return
        a user when the username is invalid?"""

        auth_u = User.authenticate("testuser33", "HASHED_PASSWORD")

        self.assertFalse(auth_u)


    def test_user_authenticate_method_pw_fail(self):
        """Does User.authenticate fail to return
        a user when the password is invalid?"""

        auth_u = User.authenticate("testuser", "HASHED_PASSWORD33")

        self.assertFalse(auth_u)


