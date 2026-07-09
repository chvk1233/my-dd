import os
import tempfile

import pytest

os.environ.setdefault("KAFKA_ENABLED", "false")
os.environ.setdefault("LLM_PROVIDER", "mock")

from app import create_app
from services import db


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db.init_db(path)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def client(temp_db):
    app = create_app(db_path=temp_db)
    app.config["TESTING"] = True
    return app.test_client()
