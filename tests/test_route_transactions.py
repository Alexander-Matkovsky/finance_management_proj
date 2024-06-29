import pytest
from flask import Flask
from app.routes.transactions import bp
from unittest.mock import Mock, patch
from app.models.database import TransactionOperations

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
    with patch('app.routes.transactions.get_db') as mock:
        yield mock

def test_add_transaction_success(client, mock_get_db):
    mock_db = Mock(spec=TransactionOperations)
    mock_get_db.return_value = mock_db

    response = client.post('/add_transaction', data={
        'account_id': '1',
        'amount': '100.50',
        'description': 'Test transaction',
        'category_name': 'Food',
        'date': '2023-06-01',
        'type': 'Expense'
    })

    assert response.status_code == 201
    assert b"Transaction added successfully!" in response.data
    mock_db.add_transaction.assert_called_once_with(1, '2023-06-01', 100.50, 'Expense', 'Test transaction', 'Food')

def test_add_transaction_missing_data(client):
    response = client.post('/add_transaction', data={
        'account_id': '1',
        'amount': '100.50'
    })
    assert response.status_code == 400
    assert b"account_id, amount, description, category_name, date, and type are required" in response.data

def test_add_transaction_invalid_type(client):
    response = client.post('/add_transaction', data={
        'account_id': '1',
        'amount': '100.50',
        'description': 'Test transaction',
        'category_name': 'Food',
        'date': '2023-06-01',
        'type': 'Invalid'
    })

    assert response.status_code == 400
    assert b"type must be either 'Income' or 'Expense'" in response.data

def test_delete_transaction_success(client, mock_get_db):
    mock_db = Mock(spec=TransactionOperations)
    mock_get_db.return_value = mock_db

    response = client.delete('/delete_transaction?transaction_id=1')

    assert response.status_code == 200
    assert b"Transaction 1 deleted successfully!" in response.data
    mock_db.delete_transaction.assert_called_once_with(1)

def test_delete_transaction_missing_id(client):
    response = client.delete('/delete_transaction')

    assert response.status_code == 400
    assert b"transaction_id is required" in response.data

def test_get_transaction_success(client, mock_get_db):
    mock_db = Mock(spec=TransactionOperations)
    mock_get_db.return_value = mock_db
    mock_transaction = {'id': 1, 'amount': 100.50, 'description': 'Test transaction'}
    mock_db.get_transaction.return_value = mock_transaction

    response = client.get('/get_transaction?transaction_id=1')

    assert response.status_code == 200
    assert response.json == mock_transaction
    mock_db.get_transaction.assert_called_once_with(1)

def test_get_transaction_not_found(client, mock_get_db):
    mock_db = Mock(spec=TransactionOperations)
    mock_get_db.return_value = mock_db
    mock_db.get_transaction.return_value = None

    response = client.get('/get_transaction?transaction_id=999')

    assert response.status_code == 404
    assert b"Transaction 999 not found" in response.data

def test_update_transaction_success(client, mock_get_db):
    mock_db = Mock(spec=TransactionOperations)
    mock_get_db.return_value = mock_db

    response = client.put('/update_transaction', data={
        'transaction_id': '1',
        'amount': '200.75',
        'description': 'Updated transaction',
        'category_name': 'Groceries',
        'date': '2023-06-02',
        'type': 'Expense'
    })

    assert response.status_code == 200
    assert b"Transaction 1 updated successfully!" in response.data
    mock_db.update_transaction.assert_called_once_with(1, '2023-06-02', 200.75, 'Expense', 'Updated transaction', 'Groceries')

def test_get_transactions_success(client, mock_get_db):
    mock_db = Mock(spec=TransactionOperations)
    mock_get_db.return_value = mock_db
    mock_transactions = [
        {'id': 1, 'amount': 100.50, 'description': 'Transaction 1'},
        {'id': 2, 'amount': 200.75, 'description': 'Transaction 2'}
    ]
    mock_db.get_transactions.return_value = mock_transactions

    response = client.get('/get_transactions?account_id=1')

    assert response.status_code == 200
    assert response.json == mock_transactions
    mock_db.get_transactions.assert_called_once_with(1)

def test_get_transactions_missing_account_id(client):
    response = client.get('/get_transactions')

    assert response.status_code == 400
    assert b"account_id is required" in response.data