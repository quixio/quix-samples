"""
Shared pytest fixtures for QuixStreams integration tests
"""
import pytest
import os
import time


@pytest.fixture
def kafka_broker():
    """Get Kafka broker address from environment"""
    return os.getenv("Quix__Broker__Address", "kafka:9092")


@pytest.fixture
def unique_suffix():
    """Generate unique suffix for test resources"""
    return int(time.time())


@pytest.fixture
def test_timeout():
    """Get test timeout from environment"""
    return int(os.getenv("TEST_TIMEOUT", "30"))
