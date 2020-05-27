import os
import pytest
from main import app, db, User


@pytest.fixture
def client():
    app.config['TESTING'] = True
    os.environ["DATABASE_URL"] = "sqlite:///:memory:"
    client = app.test_client()

    cleanup()  # clean up before every test

    db.create_all()

    yield client


def cleanup():
    db.drop_all()  # clean up/delete the DB (drop all tables in the database)


def test_index_not_logged_in(client):
    response = client.get('/')
    assert b'Enter your name' in response.data


def test_index_logged_in(client):
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    response = client.get('/')
    assert b'Write your Number' in response.data


def test_profile(client):
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    response = client.get('/profile')
    assert b'Test User' in response.data


def test_prof_edit(client):
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    response = client.get('/profile/edit')
    assert b'Edit your profile' in response.data

    response = client.post('/profile/edit', data={"profile-name": "Test User 2",
                                                  "profile-email": "test2@user.com"}, follow_redirects=True)

    assert b'Test User 2' in response.data
    assert b'test2@user.com' in response.data


def test_prof_del(client):
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    response = client.get('/profile/delete')
    assert b'Delete your Profile' in response.data

    response = client.post('/profile/delete', follow_redirects=True)
    assert b'Enter your name' in response.data


def test_users(client):
    response = client.get('/users')
    assert b'<h3>Users</h3>' in response.data
    assert b'Test User' not in response.data

    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    response = client.get('/users')
    assert b'<h3>Users</h3>' in response.data
    assert b'Test User' in response.data


def test_user_details(client):
    client.post('/login', data={"user-name": "Test User", "user-email": "test@user.com",
                                "user-password": "password123"}, follow_redirects=True)

    user = db.query(User).first()

    response = client.get('/user/{}'.format(user.id))
    assert b'test@user.com' in response.data
    assert b'Test User' in response.data