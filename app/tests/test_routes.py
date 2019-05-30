import pytest
import re
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models

def login(client, email, password):
  login_page = client.get('/login')
  m = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="([^"]+)">', login_page.data.decode('utf-8'))
  csrf = m.group(1)
  return client.post('/login', data=dict(
      email=email,
      password=password,
      csrf_token=csrf
  ), follow_redirects=True)


def logout(client):
    return client.get('/logout', follow_redirects=True)

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

def test_manage_uploads(client):
  user = models.User(
    name = 'Admin',
    email = 'admin@example.com',
    role = 'ADMIN'
  )
  user.setPassword('pass')
  db.session.add(user)
  db.session.commit()

  login(client, 'admin@example.com', 'pass')

  response = client.get('/library/manage-uploads/', headers = {
    'Accept-Type': 'application/json'
  })

  data = json.loads(response.data)

  assert data['page'] == 1
  assert data['q'] == None
  assert data['scans'] == []
  assert data['total_pages'] == 0
