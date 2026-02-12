"""
Pytest fixtures for FMU Runner tests
"""
import pytest
import os

@pytest.fixture
def fixtures_dir():
    """Path to test fixtures directory."""
    return os.path.join(os.path.dirname(__file__), "fixtures")

@pytest.fixture
def bouncing_ball_fmu(fixtures_dir):
    """Path to BouncingBall.fmu test file."""
    return os.path.join(fixtures_dir, "BouncingBall.fmu")

@pytest.fixture
def sample_input_data():
    """Sample input data in CSV-like format (list of dicts)."""
    return [
        {"time": 0.0, "x": 1.0, "y": 2.0},
        {"time": 1.0, "x": 1.5, "y": 2.5},
        {"time": 2.0, "x": 2.0, "y": 3.0},
    ]

@pytest.fixture
def sample_config():
    """Sample simulation configuration."""
    return {
        "start_time": 0.0,
        "stop_time": 3.0,
        "parameters": {}
    }
