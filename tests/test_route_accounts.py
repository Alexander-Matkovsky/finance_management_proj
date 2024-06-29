import pytest
from flask import Flask
from app.routes.accounts import bp
from app.models.database import AccountOperations
from unittest.mock import Mock, patch

from finance.account import Account

@pytest.fixture
def app():
    app = Flask(__name__)
    app.register_blueprint(bp)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def mock_db():
    with patch('app.routes.accounts.get_db') as mock:
        yield mock

def test_add_account(client, mock_db):
    mock_account_ops = Mock(spec=AccountOperations)
    mock_db.return_value = mock_account_ops

    response = client.post('/add_account', data={
        'user_id': '1',
        'account_name': 'Test Account',
        'initial_balance': '100.50'
    })

    assert response.status_code == 201
    assert b"Account Test Account added successfully!" in response.data
    mock_account_ops.add_account.assert_called_once_with(1, 'Test Account', 100.50)

def test_add_account_missing_data(client):
    response = client.post('/add_account', data={
        'user_id': '1',
        'account_name': 'Test Account'
    })

    assert response.status_code == 400
    assert b"user_id, account_name, and initial_balance are required" in response.data

def test_get_account(client, mock_db):
    mock_account_ops = Mock(spec=AccountOperations)
    mock_db.return_value = mock_account_ops
    
    # Create a mock Account object
    mock_account = Mock(spec=Account)
    mock_account.id = 1
    mock_account.user_id = 100
    mock_account.name = 'Test Account'
    mock_account.balance = 100.50
    
    mock_account_ops.get_account.return_value = mock_account

    response = client.get('/get_account?id=1')

    assert response.status_code == 200
    assert response.json == {
        "account": {
            "id": 1,
            "user_id": 100,
            "name": 'Test Account',
            "balance": 100.50
        }
    }
    mock_account_ops.get_account.assert_called_once_with(1)

def test_get_account_not_found(client, mock_db):
    mock_account_ops = Mock(spec=AccountOperations)
    mock_db.return_value = mock_account_ops
    mock_account_ops.get_account.return_value = None

    response = client.get('/get_account?id=999')

    assert response.status_code == 404
    assert b"Account 999 not found" in response.data

def test_update_account(client, mock_db):
    mock_account_ops = Mock(spec=AccountOperations)
    mock_db.return_value = mock_account_ops

    response = client.put('/update_account', data={
        'id': '1',
        'account_name': 'Updated Account',
        'new_balance': '200.75'
    })

    assert response.status_code == 200
    assert b"Account 1 updated successfully!" in response.data
    mock_account_ops.update_account.assert_called_once_with(1, 'Updated Account', 200.75)

def test_delete_account(client, mock_db):
    mock_account_ops = Mock(spec=AccountOperations)
    mock_db.return_value = mock_account_ops

    response = client.delete('/delete_account?id=1')

    assert response.status_code == 200
    assert b"Account 1 deleted successfully!" in response.data
    mock_account_ops.delete_account.assert_called_once_with(1)

def test_delete_account_invalid_id(client):
    response = client.delete('/delete_account?id=invalid')

    assert response.status_code == 400
    assert b"id must be an integer" in response.data