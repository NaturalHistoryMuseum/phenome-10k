import pytest

from app import app, db, models


@pytest.fixture
def db_models():
    """Create a client to test requests to the app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.testing = True

    # Set up the app context
    with app.app_context():
        # Create database and admin user
        db.create_all()

        # Create test client and run the tests
        yield models

    # Empty database for next test
    db.drop_all()


def test_queue(db_models):
    Queue = db_models.Queue

    Queue.add('method_name', 'arg1', 2)
    Queue.add('method_name2', 'another arg')

    iterator = Queue.read()

    assert iterator.__next__() == ('method_name', ['arg1', 2])
    assert iterator.__next__() == ('method_name2', ['another arg', ])
