import tempfile
import subprocess
import os
import uuid
from functools import wraps
from zipfile import ZipFile
from flask import request, render_template, redirect, url_for, flash, send_from_directory, jsonify, g
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.routing import ValidationError, BaseConverter
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from stl.mesh import Mesh
from app import app, db, models
from app.forms import LoginForm, RegistrationForm, ScanUploadForm, PublicationUploadForm
from app.models import User, Scan, File, Publication
import mimetypes
import subprocess
import json

mimetypes.add_type('application/javascript', '.mjs')

def convert_file(file):
  if not file:
    return (None, None)
  filename, fileExt = os.path.splitext(file.filename)
  with tempfile.NamedTemporaryFile(suffix=fileExt) as uploadFile:
    file.save(uploadFile.name)

    # Convert to bin if ascii
    file.seek(0)
    if file.read(5) == b'solid':
      # TODO: Don't override original file
      Mesh.from_file(uploadFile.name).save(uploadFile.name)

    # Convert to ctm in uploads storage
    # TODO: Check errors, secure_filename, no duplicates
    ctmFile = models.File()
    ctmFile.filename = filename + '.ctm'
    ctmFile.location = 'uploads/' + ctmFile.filename
    ctmFile.owner = current_user
    ctmFile.mime_type = 'application/zip'
    ctmConvert = subprocess.run(["ctmconv", uploadFile.name, ctmFile.location], stderr=subprocess.PIPE)
    if ctmConvert.returncode > 0:
      # TODO: Deal with this error properly
      app.logger.warn(ctmConvert.stderr)

    # Zip source file & save to large file storage
    # TODO: (secure_filename)(no duplicates)
    # TODO: Configure large file storage
    zip = models.File()
    zip.filename = file.filename + '.zip'
    zip.location = 'uploads/' + zip.filename
    zip.owner = current_user
    zip.mime_type = 'application/zip'
    with ZipFile(zip.location, 'w') as zipFile:
      zipFile.write(uploadFile.name)

    return (zip, ctmFile)



@app.context_processor
def bem_processor():
  def bem_class(el, part, modify):
    base = el + '__' + part
    classes = [ base + '--' + mod for mod, val in modify.items() if val]
    return ' '.join([ base ] + classes)
  return dict(bem = bem_class)

class SlugConverter(BaseConverter):
  regex = r'[^/]+'
  model = None

  def to_python(self, slug):
    model = self.model.findBySlug(slug)
    if model == None:
      raise ValidationError
    return model

  def to_url(self, value):
    return BaseConverter.to_url(self, value.url_slug or value.id)

class ScanConverter(SlugConverter):
  model = Scan

class PublicationConverter(SlugConverter):
  model = Publication

app.url_map.converters['scan'] = ScanConverter
app.url_map.converters['publication'] = PublicationConverter

def generate_slug(name):
  if not name:
    return None
  # TODO: Use a different function that's more similar to what wordpress does
  # (maybe just replace `_` with `-`?)
  url_slug = secure_filename(name).lower()

  try:
    if app.url_map.bind('').match('/' + url_slug) != None:
      # TODO: Instead of appending uuid, move this into the form validator and let the user pick a new url in case of clash
      url_slug += '-' + uuid.uuid4()
  except: # TODO: What's the specific RouteNotFound error here?
    pass

  return url_slug

def requiresAdmin(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.isAdmin():
            return render_template('403.html', message='You must be an administrator to access this page.', menu='home') ,403
        return f(*args, **kwargs)
    return decorated_function

def requiresContributor(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.isContributor():
            return render_template('403.html', message='You must be a contributor to access this page.', menu='home') ,403
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET', 'POST'])
def index():
  return render_template('index.html', menu='home')

@app.route('/uploads/<path:path>')
def send_uploads(path):
    return send_from_directory('../uploads', path)

@app.route('/about', methods=['GET', 'POST'])
def about():
  return render_template('about.html', title='About', menu='about')

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
    return render_template('login.html', title='Sign In', form=form, error=error, menu='home')

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
    return render_template('register.html', title='Register', form=form, error=error, menu='home')

@app.route('/library/', methods=['GET'])
def library():
  # scans = Scan.query.filter_by(published=True).order_by(db.func.random()).limit(50).all()
  sort = Scan.scientific_name if request.args.get("sort") else db.func.random()
  scans = Scan.query.order_by(sort).limit(50).all()

  return render_vue('library', [s.serialize() for s in scans], title="Library", menu='library')

@app.route('/library/create/', methods=['GET', 'POST'])
@requiresContributor
def library_create():
    form = ScanUploadForm()

    # Get the records for the currently selected publications
    pubsearch = form.publications_search.data or []
    pubselected = (form.publications.data or []) + pubsearch
    form.publications.data = pubselected
    pubs = Publication.query.filter(Publication.id.in_(pubselected)).all()
    form.publications.choices = [(pub.id, pub.title) for pub in pubs]

    if form.validate_on_submit():
      # TODO: Restrict list of uploadable file types
      # Save upload to temporary file
      (zipFile, ctmFile) = convert_file(form.file.data)

      url_slug = generate_slug(form.scientific_name.data)

      scan = Scan(
        author_id = current_user.id,
        scientific_name = form.scientific_name.data,
        alt_name = form.alt_name.data,
        specimen_location = form.specimen_location.data,
        specimen_id = form.specimen_id.data,
        description = form.description.data,
        url_slug = url_slug,
        publications = pubs,
        source = zipFile,
        ctm = ctmFile
      )

      db.session.add(scan)
      db.session.commit()


      if request.accept_mimetypes.accept_json:
        return jsonify({
          'id': scan.id,
          'ctm': scan.ctm.location
         })

      return redirect(url_for('edit_scan', scan=scan))

    if form.pub_query.data:
      pubs = Publication.query.filter(Publication.title.contains(form.pub_query.data))
      form.publications_search.choices = set([(pub.id, pub.title) for pub in pubs]) - set(form.publications.choices)

    if request.accept_mimetypes.accept_html:
      return render_template('base.html', content=vue('library/create', g.csrf_token), title='Upload New', menu='library')

    return jsonify({ 'errors': form.errors, 'data': { k: v for k, v in form.data.items() if k != 'file'  } })

@app.route('/<scan:scan>/')
def scan(scan):
  # TODO: Hide if unpublished
  return render_template('scan.html', title=scan.scientific_name, scan=scan, menu='library')

@app.route('/<scan:scan>/edit', methods=['GET', 'POST'])
def edit_scan(scan):
  # TODO: Check user can edit
  form = ScanUploadForm(obj=scan, pub_query=request.args.get("pub_query"))
  # pubIds = [(pubId,) for pubId in form.publications.data] if form.publications.data else []
  # form.publications.choices = [(pub.id, pub.title) for pub in scan.publications] + pubIds

  pubsearch = form.publications_search.data or []
  pubselected = (form.publications.data or [pub.id for pub in scan.publications]) + pubsearch
  form.publications.data = pubselected
  pubs = Publication.query.filter(Publication.id.in_(pubselected)).all()
  form.publications.choices = [(pub.id, pub.title) for pub in pubs]
  form.publications_search.choices = form.publications.choices

  if form.validate_on_submit():
    scan.scientific_name = form.scientific_name.data
    scan.alt_name = form.alt_name.data
    scan.specimen_location = form.specimen_location.data
    scan.specimen_id = form.specimen_id.data
    scan.description = form.description.data
    scan.publications = Publication.query.filter(Publication.id.in_(form.publications.data)).all()
    for file in form.attachments.data:
        # TODO: Don't overwrite
        file.save('uploads/' + file.filename)
        scan.attachments.append(File(
          filename = file.filename,
          location = 'uploads/' + file.filename,
          owner_id = current_user.id
        ))
    db.session.commit()
    return redirect(url_for('edit_scan', scan=scan) + '?pub_query=' + form.pub_query.data)

  if form.pub_query.data:
    pubs = Publication.query.filter(Publication.title.contains(form.pub_query.data))
    form.publications_search.choices = set([(pub.id, pub.title) for pub in pubs]) - set(form.publications.choices)

  if request.accept_mimetypes.accept_html:
    return render_template('base.html', content=vue('library/create', g.csrf_token), title='Edit', menu='library')

  return jsonify({ 'errors': form.errors, 'data': form.json_data(), 'scan': scan.serialize() })

@app.route('/publications/create/', methods=['GET', 'POST'])
@requiresContributor
def create_publication():
    form = PublicationUploadForm()
    if form.validate_on_submit():
      publication = Publication(
        author_id = current_user.id,
        title = form.title.data,
        url_slug = generate_slug(form.title.data),
        pub_year = form.pub_year.data,
        authors = form.authors.data,
        journal = form.journal.data,
        link = form.link.data,
        abstract = form.abstract.data
      )

      for file in form.files.data:
        # TODO: Don't overwrite
        file.save('uploads/' + file.filename)
        publication.files.append(File(
          filename = file.filename,
          location = 'uploads/' + file.filename,
          owner_id = current_user.id,
          mime_type = 'application/pdf',
        ))

      db.session.add(publication)
      db.session.commit()

      return redirect(url_for('edit_publication', publication=publication))

    return render_template('create-publication.html', title='Create', form=form, menu='publications')

@app.route('/publications')
def publications():
  title = request.args.get('title')
  pubs = Publication.query.filter(Publication.title.ilike('%{0}%'.format(title)))
  return jsonify([pub.serialize() for pub in pubs])

@app.route('/<publication:publication>/')
def publication(publication):
  # TODO: Hide if unpublished
  return render_template('publication.html', title=publication.title, publication=publication, menu='publications')

@app.route('/<publication:publication>/edit/', methods=['GET', 'POST'])
@requiresContributor
def edit_publication(publication):
    form = PublicationUploadForm(obj=publication)
    if form.validate_on_submit():
      publication.title = form.title.data
      publication.pub_year = form.pub_year.data
      publication.authors = form.authors.data
      publication.journal = form.journal.data
      publication.link = form.link.data
      publication.abstract = form.abstract.data

      app.logger.warn(form.files.data)

      for file in form.files.data:
        # TODO: Don't overwrite
        if file == None:
          continue
        file.save('uploads/' + file.filename)
        f = File(
          filename = file.filename,
          location = 'uploads/' + file.filename,
          owner_id = current_user.id,
          mime_type = 'application/pdf',
        )
        db.session.add(f)
        publication.files.append(f)

      db.session.commit()

      return redirect(url_for('edit_publication', publication=publication))

    return render_template('create-publication.html', title='Create', form=form, menu='publications')

@app.route('/upload', methods=['POST'])
@requiresContributor
def upload():
  files = request.files.getlist('file')
  result = []
  for file in files:
    (zipFile, ctmFile) = convert_file(file)
    db.session.add(zipFile)
    db.session.add(ctmFile)
    db.session.commit()
    result.append({
      'zip': zipFile.id,
      'ctm': {
        'id': ctmFile.id,
        'url': ctmFile.location
      }
    })

  return jsonify(result)

def render_vue(path, data, title, menu):
  if request.accept_mimetypes.accept_html:
    return render_template('base.html', content=vue(path, data), title=title, menu=menu)
  return jsonify(data)

def vue(path, defaultData = None):
  pipes = subprocess.Popen(['node', '--experimental-modules', 'node/route.mjs', path, json.dumps(defaultData)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  std_out, std_err = pipes.communicate()

  if pipes.returncode != 0:
      # an error happened!
      err_msg = "%s. Code: %s" % (std_err.decode().strip(), pipes.returncode)
      raise Exception(err_msg)

  elif len(std_err):
    app.logger.error(std_err.decode())

  return std_out.decode()
