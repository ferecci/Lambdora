import pytest
from main import load_std

@pytest.fixture(autouse=True, scope="session")
def load_stdlib_once():
    load_std()
