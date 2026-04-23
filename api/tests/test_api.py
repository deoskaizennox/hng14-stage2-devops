import pytest
from unittest.mock import patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app


@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_health_endpoint(client):
    """Test the health endpoint returns 200 and healthy status"""
    response = client.get('/health')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'healthy'


@patch('main.r')
def test_create_job(mock_redis, client):
    """Test job creation with mocked Redis"""
    mock_redis.lpush.return_value = 1
    mock_redis.hset.return_value = 1

    response = client.post('/jobs')
    assert response.status_code == 200
    json_data = response.get_json()
    assert 'job_id' in json_data
    assert len(json_data['job_id']) > 0


@patch('main.r')
def test_get_job_exists(mock_redis, client):
    """Test getting a job that exists"""
    mock_redis.hget.return_value = b'queued'

    response = client.get('/jobs/test-job-123')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['job_id'] == 'test-job-123'
    assert json_data['status'] == 'queued'


@patch('main.r')
def test_get_job_not_found(mock_redis, client):
    """Test 404 for non-existent job"""
    mock_redis.hget.return_value = None

    response = client.get('/jobs/nonexistent-id')
    assert response.status_code == 404
