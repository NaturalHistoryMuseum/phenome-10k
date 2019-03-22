import tempfile
import subprocess
import os
import uuid
from functools import wraps
from zipfile import ZipFile
from flask import request, render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.routing import ValidationError, BaseConverter
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from stl.mesh import Mesh
from app import app, db, models
from app.forms import LoginForm, RegistrationForm, ScanUploadForm
from app.models import User, Scan

class ScanConverter(BaseConverter):
  regex = r'[^/]+'

  def to_python(self, slug):
    scan = Scan.query.filter_by(url_slug=slug).first()
    if scan == None:
      raise ValidationError
    return scan

  def to_url(self, value):
    return BaseConverter.to_url(self, value.url_slug)

app.url_map.converters['scan'] = ScanConverter

def requiresAdmin(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.isAdmin():
            return render_template('403.html', message='You must be an administrator to access this page.') ,403
        return f(*args, **kwargs)
    return decorated_function

def requiresContributor(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.isContributor():
            return render_template('403.html', message='You must be a contributor to access this page.') ,403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('index.html')

@app.route('/about', methods=['GET', 'POST'])
def about():
  return render_template('about.html', title='About')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(next=request.args.get('next'))
    error = None
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.checkAndMigratePassword(form.password.data):
          db.session.commit()
          login_user(user, remember=form.remember_me.data)
          next_page = form.next.data
          if not next_page or url_parse(next_page).netloc != '':
              next_page = url_for('index')
          return redirect(next_page)
        else:
          error = 'Invalid email and/or password'
    return render_template('login.html', title='Sign In', form=form, error=error)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
      return redirect(url_for('index'))
    form = RegistrationForm()
    error = None

    if form.validate_on_submit():
      user = User(name = form.name.data, email=form.email.data, country_code=form.country.data, user_type=form.organisation.data)
      user.setPassword(form.password.data)
      db.session.add(user)
      db.session.commit()
      flash('You are now registered and may log in')
      return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, error=error)

@app.route('/library/', methods=['GET'])
def library():
  scans = Scan.query.filter_by(published=True).order_by(db.func.random()).limit(50).all()

  return render_template('library.html', title="Library", scans=scans)

@app.route('/library/create/', methods=['GET', 'POST'])
@requiresContributor
def library_create():
    form = ScanUploadForm()
    if form.validate_on_submit():
      # TODO: Restrict list of uploadable file types
      # Save upload to temporary file
      filename, fileExt = os.path.splitext(form.file.data.filename)
      with tempfile.NamedTemporaryFile(suffix=fileExt) as uploadFile:
        form.file.data.save(uploadFile.name)

        # Convert to bin if ascii
        form.file.data.seek(0)
        if form.file.data.read(5) == b'solid':
          # TODO: Don't override original file
          Mesh.from_file(uploadFile.name).save(uploadFile.name)

        # Convert to ctm in uploads storage
        # TODO: Check errors, secure_filename, no duplicates
        ctmConvert = subprocess.run(["ctmconv", uploadFile.name, 'uploads/' + filename + '.ctm'], stderr=subprocess.PIPE)
        if ctmConvert.returncode > 0:
          # TODO: Deal with this error properly
          app.logger.warn(ctmConvert.stderr)

        # Zip source file & save to large file storage
        # TODO: (secure_filename)(no duplicates)
        # TODO: Configure large file storage
        with ZipFile('uploads/' + form.file.data.filename + '.zip', 'w') as zipFile:
          zipFile.write(uploadFile.name)

      # TODO: Use a different function that's more similar to what wordpress does
      # (maybe just replace `_` with `-`?)
      url_slug = secure_filename(form.scientific_name.data).lower()

      try:
        if app.url_map.bind('').match('/' + url_slug) != None:
          # TODO: Instead of appending uuid, move this into the form validator and let the user pick a new url in case of clash
          url_slug += '-' + uuid.uuid4()
      except: # TODO: What's the specific RouteNotFound error here?
        pass

      scan = Scan(
        author_id = current_user.id,
        scientific_name = form.scientific_name.data,
        alt_name = form.alt_name.data,
        specimen_location = form.specimen_location.data,
        specimen_id = form.specimen_id.data,
        description = form.description.data,
        url_slug = url_slug
      )

      db.session.add(scan)
      db.session.commit()

      return redirect(url_for('edit_scan', scan=scan))

    return render_template('upload.html', title='Upload New', form=form)

@app.route('/<scan:scan>/')
def scan(scan):
  # TODO: Hide if unpublished
  return render_template('scan.html', title=scan.scientific_name, scan=scan)

@app.route('/<scan:scan>/edit/', methods=['GET', 'POST'])
def edit_scan(scan):
  # TODO: Check user can edit
  form = ScanUploadForm(obj=scan)
  if form.validate_on_submit():
    scan.scientific_name = form.scientific_name.data
    scan.alt_name = form.alt_name.data
    scan.specimen_location = form.specimen_location.data
    scan.specimen_id = form.specimen_id.data
    scan.description = form.description.data
    db.session.commit()
    return redirect(url_for('edit_scan', scan=scan))
  return render_template('upload.html', title=scan.scientific_name, form=form, edit=True)
