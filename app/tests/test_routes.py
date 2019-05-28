import pytest
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db

@pytest.fixture
def client():
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
  app.testing = True

  with app.app_context():
    db.create_all()

  client = app.test_client()

  return client


def test_library(client):
    response = client.get('/library', headers = {
      'Accept-Type': 'application/json'
    })

    assert response.data == b'{"q":null,"scans":[],"tags":{"taxonomy":[]}}\n'


# - Construct app instance with in-memory database
# - Run db migration
# -
