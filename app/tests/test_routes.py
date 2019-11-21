import pytest
import re
import json
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app import app, db, models

def csrf_token(client):
  """Generate a csrf token"""
  from flask import g

  # If the front page has been loaded once, the token will be in `g`
  if csrf_token in g:
    return g.csrf_token

  # Otherwise, do a request for the login page and get it from regex
  # Don't think there's a more straight forward way of doing this sadly
  login_page = client.get('/login')
  m = re.search(r'<input id="csrf_token" name="csrf_token" type="hidden" value="([^"]+)">', login_page.data.decode('utf-8'))
  csrf = m[1]

  return csrf

def login(client, email, password):
  """Log in a user and set a cookie on the client"""
  csrf = csrf_token(client)

  response = client.post('/login', data=dict(
      email=email,
      password=password,
      csrf_token=csrf
  ), follow_redirects=True)

  # if(response.status_code != 302):
  #   raise Exception('Did not log in: {0}'.format(response.status))

def login_admin(client):
  """Log in the admin user created by the client fixture"""
  login(client, 'admin@example.com', 'pass')


def logout(client):
  """Log out the current user"""
  return client.get('/logout', follow_redirects=True)

# Fixtures are created with the pytest.fixture decorator
# They are called by adding an argument to the test method with
# the name of the fixture you want to apply.

@pytest.fixture
def client():
  """Create a client to test requests to the app"""
  app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
  app.testing = True

  # Set up the app context
  with app.app_context():
    # Create database and admin user
    db.create_all()

    # Create test client and run the tests
    yield app.test_client()

  # Empty database for next test
  db.drop_all()

@pytest.fixture
def admin(client):
  """Create an admin user"""
  user = models.User(
    name = 'Admin',
    email = 'admin@example.com',
    role = 'ADMIN'
  )
  user.setPassword('pass')
  db.session.add(user)
  db.session.commit()
  return user

def test_library(client):
  response = client.get('/library', headers = {
    'Accept-Type': 'application/json'
  })

  assert response.data == b'{"page":1,"q":null,"scans":[],"showMine":false,"tags":{"taxonomy":[]},"total_pages":0}\n'

def test_manage_uploads(client, admin):
  login_admin(client)

  response = client.get('/library/manage-uploads/', headers = {
    'Accept-Type': 'application/json'
  })

  data = json.loads(response.data)

  assert data['page'] == 1
  assert data['q'] == None
  assert data['scans'] == []
  assert data['total_pages'] == 0

def test_stl_upload(client, tmpdir, admin):
  """Test for uploading a file and making sure it gets zipped"""
  login_admin(client)

  app.config['UPLOAD_DIRECTORY'] = tmpdir
  app.config['MODEL_DIRECTORY'] = tmpdir

  import io, time
  upload_file = (io.BytesIO(b'random data'), 'test_file.stl')
  data = {'file': upload_file, 'csrf_token': csrf_token(client) }
  response = client.post(
      '/scans/create?noredirect=1',
      data=data,
      content_type='multipart/form-data',
      headers = {
        'Accept': 'application/json'
      }
  )

  zip_file = '/'.join((time.strftime("%Y/%m/%d"), upload_file[1] + '.zip'))
  expected_file = '/models/' + zip_file
  expected_location = tmpdir.join(zip_file)

  from os import path

  assert json.loads(response.data)['scan']['source'] == expected_file
  assert path.exists(expected_location)

def test_zip_upload(client, tmpdir, admin):
  """Test for uploading a zip file"""
  login_admin(client)

  app.config['UPLOAD_DIRECTORY'] = tmpdir
  app.config['MODEL_DIRECTORY'] = tmpdir

  import io, time
  from pathlib import Path

  horse = io.BytesIO(Path(__file__).parent.parent.parent.joinpath('fixtures/Horse.zip').read_bytes())
  upload_file = (horse, 'test_file.zip')
  data = {'file': upload_file, 'csrf_token': csrf_token(client) }
  response = client.post(
      '/scans/create?noredirect=1',
      data=data,
      content_type='multipart/form-data',
      headers = {
        'Accept': 'application/json'
      }
  )

  zip_file = '/'.join((time.strftime("%Y/%m/%d"), upload_file[1]))
  expected_file = '/models/' + zip_file
  expected_location = tmpdir.join(zip_file)

  from os import path

  assert json.loads(response.data)['scan']['source'] == expected_file
  assert path.exists(expected_location)

def test_upload_process(client, tmpdir, admin):
  """Test to make sure an uploaded file gets processed"""
  login_admin(client)

  modeldir = tmpdir.join('models')
  app.config['UPLOAD_DIRECTORY'] = tmpdir
  app.config['MODEL_DIRECTORY'] = modeldir

  from pathlib import Path
  from app.models import File, Scan
  import io

  horse = io.BytesIO(Path(__file__).parent.parent.parent.joinpath('fixtures/Horse.zip').read_bytes())
  horseFile = File.fromBinary('horse.zip', horse, storage_area = File.MODELS_DIR, owner_id = admin.id)
  with open(horseFile.getAbsolutePath(),'wb') as f:
    f.write(horse.read())
  horseScan = Scan()
  horseScan.source = horseFile
  horseScan.author = admin
  db.session.add(horseFile)
  db.session.add(horseScan)
  db.session.commit()

  response = client.post(
      '/{0}/process'.format(horseScan.id)
  )

  import time
  ctm_file = '/'.join((time.strftime("%Y/%m/%d"), 'Horse.ascii.ctm'))
  expected_file = '/uploads/' + ctm_file
  expected_location = tmpdir.join(ctm_file)

  from os import path

  assert path.exists(expected_location)
  assert response.location == 'http://localhost/1/'

  response = client.get(
      response.location,
      headers = {
        'Accept': 'application/json'
      }
  )

  assert json.loads(response.data)  ['ctm'] == expected_file