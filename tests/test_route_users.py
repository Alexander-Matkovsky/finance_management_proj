import pytest
from flask import Flask
from app.routes.users import bp
from unittest.mock import Mock, patch
from app.models.database import UserOperations

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_get_db():
    with patch('app.routes.users.get_db') as mock:
        yield mock

def test_add_user_success(client, mock_get_db):
    mock_db = Mock(spec=UserOperations)
    mock_get_db.return_value = mock_db

    response = client.post('/add_user', data={'name': 'John Doe'})

    assert response.status_code == 201
    assert b"User John Doe added successfully!" in response.data
    mock_db.add_user.assert_called_once_with('John Doe')

def test_add_user_missing_name(client):
    response = client.post('/add_user', data={})

    assert response.status_code == 400
    assert b"Name is required" in response.data

def test_delete_user_success(client, mock_get_db):
    mock_db = Mock(spec=UserOperations)
    mock_get_db.return_value = mock_db

    response = client.delete('/delete_user?user_id=1')

    assert response.status_code == 200
    assert b"User 1 deleted successfully!" in response.data
    mock_db.delete_user.assert_called_once_with(1)

def test_delete_user_missing_id(client):
    response = client.delete('/delete_user')

    assert response.status_code == 400
    assert b"user_id is required" in response.data

def test_delete_user_invalid_id(client):
    response = client.delete('/delete_user?user_id=invalid')

    assert response.status_code == 400
    assert b"user_id must be an integer" in response.data

def test_get_user_success(client, mock_get_db):
    mock_db = Mock(spec=UserOperations)
    mock_get_db.return_value = mock_db
    mock_user = Mock()
    mock_user.user_id = 1
    mock_user.name = 'John Doe'
    mock_db.get_user.return_value = mock_user

    response = client.get('/get_user?user_id=1')

    assert response.status_code == 200
    assert response.json == {"user_id": 1, "name": "John Doe"}
    mock_db.get_user.assert_called_once_with(1)

def test_get_user_not_found(client, mock_get_db):
    mock_db = Mock(spec=UserOperations)
    mock_get_db.return_value = mock_db
    mock_db.get_user.return_value = None

    response = client.get('/get_user?user_id=999')

    assert response.status_code == 404
    assert b"User 999 not found" in response.data

def test_get_user_missing_id(client):
    response = client.get('/get_user')

    assert response.status_code == 400
    assert b"user_id is required" in response.data

def test_get_user_invalid_id(client):
    response = client.get('/get_user?user_id=invalid')

    assert response.status_code == 400
    assert b"user_id must be an integer" in response.data

def test_update_user_success(client, mock_get_db):
    mock_db = Mock(spec=UserOperations)
    mock_get_db.return_value = mock_db

    response = client.put('/update_user', data={
        'user_id': '1',
        'name': 'Jane Doe'
    })

    assert response.status_code == 200
    assert b"User 1 updated successfully!" in response.data
    mock_db.update_user.assert_called_once_with(1, 'Jane Doe')

def test_update_user_missing_data(client):
    response = client.put('/update_user', data={
        'user_id': '1'
    })

    assert response.status_code == 400
    assert b"user_id and name are required" in response.data

def test_update_user_invalid_id(client):
    response = client.put('/update_user', data={
        'user_id': 'invalid',
        'name': 'Jane Doe'
    })

    assert response.status_code == 400
    assert b"user_id must be an integer" in response.data