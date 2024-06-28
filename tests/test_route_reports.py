import pytest
from flask import Flask
from app.routes.reports import bp
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
def mock_get_connection():
    with patch('app.routes.reports.get_connection') as mock:
        yield mock

@pytest.fixture
def mock_report_generator():
    with patch('app.routes.reports.ReportGenerator') as mock:
        yield mock

@pytest.fixture
def mock_render_template():
    with patch('app.routes.reports.render_template') as mock:
        yield mock

def test_generate_report_success(client, mock_get_connection, mock_report_generator, mock_render_template):
    mock_conn = Mock()
    mock_get_connection.return_value = mock_conn
    
    mock_report = {
        'income': 5000,
        'expenses': 3000,
        'savings': 2000,
        'categories': {
            'Food': 1000,
            'Rent': 1500,
            'Utilities': 500
        }
    }
    mock_report_generator.return_value.generate_report.return_value = mock_report
    mock_render_template.return_value = "Mocked HTML Response"

    response = client.get('/generate_report?user_id=1&start_date=2023-01-01&end_date=2023-12-31')

    assert response.status_code == 200
    assert response.data == b"Mocked HTML Response"

    mock_get_connection.assert_called_once()
    mock_report_generator.assert_called_once_with(mock_conn)
    mock_report_generator.return_value.generate_report.assert_called_once_with(1, '2023-01-01', '2023-12-31')
    mock_render_template.assert_called_once_with('report.html', report=mock_report)

def test_generate_report_missing_user_id(client):
    response = client.get('/generate_report?start_date=2023-01-01&end_date=2023-12-31')

    assert response.status_code == 400
    assert b'user_id is required' in response.data

def test_generate_report_missing_dates(client):
    response = client.get('/generate_report?user_id=1')

    assert response.status_code == 400
    assert b'start_date and end_date are required' in response.data

def test_generate_report_invalid_user_id(client):
    response = client.get('/generate_report?user_id=invalid&start_date=2023-01-01&end_date=2023-12-31')

    assert response.status_code == 400
    assert b'user_id must be an integer' in response.data

def test_generate_report_error(client, mock_get_connection, mock_report_generator):
    mock_conn = Mock()
    mock_get_connection.return_value = mock_conn
    
    mock_report_generator.return_value.generate_report.side_effect = Exception("Database error")

    response = client.get('/generate_report?user_id=1&start_date=2023-01-01&end_date=2023-12-31')

    assert response.status_code == 500
    assert b'Database error' in response.data

    mock_get_connection.assert_called_once()
    mock_report_generator.assert_called_once_with(mock_conn)
    mock_report_generator.return_value.generate_report.assert_called_once_with(1, '2023-01-01', '2023-12-31')