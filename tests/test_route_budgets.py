import pytest
from flask import Flask, json
from app.routes.budgets import bp
from app.models.database import BudgetOperations
from unittest.mock import Mock, patch

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
    with patch('app.routes.budgets.get_db') as mock:
        yield mock

def test_add_budget(client, mock_db):
    mock_budget_ops = Mock(spec=BudgetOperations)
    mock_db.return_value = mock_budget_ops

    response = client.post('/add_budget', data={
        'user_id': '1',
        'budget_name': 'Groceries',
        'initial_amount': '500.00'
    })

    assert response.status_code == 201
    assert b"Budget Groceries added successfully!" in response.data
    mock_budget_ops.set_budget.assert_called_once_with(1, 'Groceries', 500.00)

def test_get_budget(client, mock_db):
    mock_budget_ops = Mock(spec=BudgetOperations)
    mock_db.return_value = mock_budget_ops
    mock_budget_ops.get_budget.return_value = (500.00, 250.00)

    response = client.get('/get_budget?user_id=1&category_name=Groceries')

    assert response.status_code == 200
    assert response.json == {"budget": {"amount": 500.00, "amount_used": 250.00}}
    mock_budget_ops.get_budget.assert_called_once_with(1, 'Groceries')

def test_get_budgets(client, mock_db):
    mock_budget_ops = Mock(spec=BudgetOperations)
    mock_db.return_value = mock_budget_ops

    class MockBudget:
        def __init__(self, data):
            self.__dict__.update(data)
        
        def to_dict(self):
            return self.__dict__

        def __repr__(self):
            return str(self.to_dict())

    # Use MockBudget objects to represent budgets
    mock_budgets = [
        MockBudget({
            "id": 1,
            "user_id": 1,
            "category_name": 'Groceries',
            "amount": 500.00,
            "amount_used": 250.00
        }),
        MockBudget({
            "id": 2,
            "user_id": 1,
            "category_name": 'Entertainment',
            "amount": 200.00,
            "amount_used": 100.00
        })
    ]
    mock_budget_ops.get_budgets.return_value = mock_budgets

    response = client.get('/get_budgets?user_id=1')
    print(response.data)  # Print raw response data
    assert response.status_code == 200
    response_data = json.loads(response.data)
    assert len(response_data['budgets']) == 2
    assert response_data['budgets'][0]['category_name'] == 'Groceries'
    assert response_data['budgets'][1]['category_name'] == 'Entertainment'
    mock_budget_ops.get_budgets.assert_called_once_with(1)

def test_update_budget(client, mock_db):
    mock_budget_ops = Mock(spec=BudgetOperations)
    mock_db.return_value = mock_budget_ops

    response = client.put('/update_budget', data={
        'user_id': '1',
        'category_name': 'Groceries',
        'new_amount': '600.00'
    })

    assert response.status_code == 200
    assert b"Budget for user 1 and category Groceries updated successfully!" in response.data
    mock_budget_ops.update_budget.assert_called_once_with(1, 'Groceries', 600.00)

def test_delete_budget(client, mock_db):
    mock_budget_ops = Mock(spec=BudgetOperations)
    mock_db.return_value = mock_budget_ops

    response = client.delete('/delete_budget?user_id=1&category_name=Groceries')

    assert response.status_code == 200
    assert b"Budget for user 1 and category Groceries deleted successfully!" in response.data
    mock_budget_ops.delete_budget.assert_called_once_with(1, 'Groceries')

def test_add_budget_missing_data(client):
    response = client.post('/add_budget', data={
        'user_id': '1',
        'budget_name': 'Groceries'
    })

    assert response.status_code == 400
    assert b"user_id, budget_name, and initial_amount are required" in response.data

def test_get_budget_not_found(client, mock_db):
    mock_budget_ops = Mock(spec=BudgetOperations)
    mock_db.return_value = mock_budget_ops
    mock_budget_ops.get_budget.return_value = (None, None)

    response = client.get('/get_budget?user_id=1&category_name=NonExistent')

    assert response.status_code == 404
    assert b"Budget for user 1 and category NonExistent not found" in response.data