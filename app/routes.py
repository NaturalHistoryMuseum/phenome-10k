import tempfile
import subprocess
import os
import uuid
from functools import wraps
from zipfile import ZipFile, ZIP_DEFLATED
from flask import request, render_template, redirect, url_for, flash, send_from_directory, jsonify, g, Response, send_file
from flask.helpers import safe_join
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.routing import ValidationError, BaseConverter
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound, BadRequest
from stl.mesh import Mesh
from app import app, db, models
from app.forms import LoginForm, RegistrationForm, ScanUploadForm, PublicationUploadForm
from app.models import User, Scan, File, Publication, Tag, Taxonomy, ScanAttachment
import mimetypes
import subprocess
import json
from PIL import Image
import io

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
    with ZipFile(zip.location, 'w', ZIP_DEFLATED) as zipFile:
      zipFile.write(uploadFile.name)

    return (zip, ctmFile)

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
  width = request.args.get('w')

  if width == None:
    return send_from_directory('../uploads', path)

  thumbnail_file = path + '-' + width + '.png'

  try:
    return send_from_directory('../thumbnails', thumbnail_file)
  except NotFound:
    thumbnail_file = safe_join('thumbnails/', thumbnail_file)

    try:
      width = int(width)
    except ValueError:
      raise BadRequest('Thumbnail width must be an integer number')

    if width < 1:
      raise BadRequest('Thumbnail width must be greater than zero')

    try:
      im = Image.open(safe_join('uploads', path))
    except FileNotFoundError:
      raise NotFound()
    except OSError:
      raise BadRequest()

    if(width >= im.width):
      return send_from_directory('../uploads', path)

    height = im.height * width / im.width
    im.thumbnail((width, height))
    byteIO = io.BytesIO()
    im.save(byteIO, format='PNG')
    im.save(thumbnail_file, format='PNG')
    return Response(byteIO.getvalue(), mimetype="image/png", direct_passthrough=True)

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

# This is just for development, please delete before going to production
@app.route('/tag', methods=['GET','POST'])
@requiresAdmin
def tag():
  import calendar
  import time
  t = "''"
  tax = "''"
  if request.method=='POST':
    t = request.form.get('type')
    tax = request.form.get('taxonomy')
    parent = '/'.join(tax.split('/')[0:-1])
    if (parent != ''):
      parent_id = Tag.query.filter_by(taxonomy = parent).first().id
    else:
      parent_id = None
    tag = Tag(id = int(calendar.timegm(time.gmtime())), name = request.form.get('name'), taxonomy = tax, category = t, parent_id = parent_id)
    db.session.add(tag)
    db.session.commit()
  return '<form method=post><input name=type value='+ t +' placeholder=category><input autofocus name=name placeholder=name><input placeholder=taxonomy name=taxonomy value='+tax+'><input type=submit></form>'

@app.route('/library/', methods=['GET'])
def library():
  # scans = Scan.query.filter_by(published=True).order_by(db.func.random()).limit(50).all()
  sort = request.args.get("sort")
  ontogenic_age = request.args.getlist("ontogenic_age")
  geologic_age = request.args.getlist("geologic_age")
  elements = request.args.getlist("elements")
  taxonomy = request.args.getlist("taxonomy")
  mine = 'mine' in request.args.keys()

  scanConditions = db.and_(
    Scan.published,
    Scan.tags.any(db.or_(*[ Tag.taxonomy.startswith(term) for term in ontogenic_age ])),
    Scan.tags.any(db.or_(*[ Tag.taxonomy.startswith(term) for term in geologic_age ])),
    Scan.tags.any(db.or_(*[ Tag.taxonomy.startswith(term) for term in elements ])),
    Scan.taxonomy.any(Taxonomy.id.in_(taxonomy)) if len(taxonomy) > 0 else True,
    Scan.author_id == current_user.id if mine and current_user.is_authenticated else True
  )

  # This is annoying... if we're sorting by name it's just sort,
  # but if we're sorting by tag we need to group it all.
  # Put it under the `groups` key so the view knows it needs to render differently
  if(sort in ('geologic_age', 'ontogenic_age')):
    data ={
      'groups': [ { 'group': tag.name, 'items': [s.serialize() for s in tag.scans if s.published ] } for tag in Tag.query.filter(Tag.scans.any(scanConditions)).filter_by(category=sort).all() ]
    }
  else:
    query = Scan.scientific_name

    data = {
      'scans': [ s.serialize() for s in Scan.query.filter(scanConditions).order_by(query).limit(50).all() ]
    }

  data['tags'] = Tag.tree()
  data['tags']['taxonomy'] = Taxonomy.tree()

  return render_vue(data, title="Library", menu='library')

@app.route('/library/manage-uploads')
def manage_uploads():
  pass

@app.route('/<scan:scan>/')
def scan(scan):
  # TODO: Hide if unpublished
  return render_vue(scan.serialize(), title=scan.scientific_name, menu='library')

@app.route('/<scan:scan>/stills')
@login_required
def scan_stills(scan):
  """Return a zip file containing all of the stills attached to this scan"""
  zip_buffer = io.BytesIO()
  with ZipFile(zip_buffer, "w") as zip_file:
    for still in scan.attachments:
      zip_file.write(still.file.location, still.file.filename)

  zip_buffer.seek(0)
  filename = scan.url_slug + '_stills.zip'

  return send_file(zip_buffer, as_attachment=True, attachment_filename=filename)

@app.route('/<scan:scan>/edit', methods=['GET', 'POST'])
@app.route('/library/create/', methods=['GET', 'POST'])
@requiresContributor
def edit_scan(scan = None):
  # TODO: Check user can edit
  form = ScanUploadForm(obj=scan, pub_query=request.args.get("pub_query"))

  # Get the records for the currently selected publications
  pubsearch = form.publications_search.data or []
  scanpubs = [pub.id for pub in scan.publications] if scan else []
  pubselected = (form.publications.data or scanpubs) + pubsearch
  form.publications.data = pubselected
  pubs = Publication.query.filter(Publication.id.in_(pubselected)).all()
  form.publications.choices = [(pub.id, pub.title) for pub in pubs]
  form.publications_search.choices = form.publications.choices

  if request.method == 'POST':
    if scan == None:
      scan = Scan(
        author_id = current_user.id,
      )
      db.session.add(scan)

    # TODO: Restrict list of uploadable file types
    # Save upload to temporary file
    if form.file.data:
        (zipFile, ctmFile) = convert_file(form.file.data)
        scan.source = zipFile
        scan.ctm = ctmFile
        db.session.add(zipFile)
        db.session.add(ctmFile)

    if scan.url_slug == None:
      scan.url_slug = generate_slug(form.scientific_name.data)

    scan.scientific_name = form.scientific_name.data
    scan.alt_name = form.alt_name.data
    scan.specimen_location = form.specimen_location.data
    scan.specimen_id = form.specimen_id.data
    scan.description = form.description.data
    scan.publications = Publication.query.filter(Publication.id.in_(form.publications.data)).all()
    scan.tags = form.geologic_age.data + form.ontogenic_age.data + form.elements.data

    if form.gbif_id.data:
      scan.gbif_id = form.gbif_id.data

      import urllib.request, json
      with urllib.request.urlopen("http://api.gbif.org/v1/species/" + str(scan.gbif_id) + "/parents") as url:
        tags = json.loads(url.read().decode())
      with urllib.request.urlopen("http://api.gbif.org/v1/species/" + str(scan.gbif_id)) as url:
        tags.append(json.loads(url.read().decode()))

      tagIds = [ tag['key'] for tag in tags ]
      existingTags = Taxonomy.query.filter(Taxonomy.id.in_(tagIds)).all()
      existingTagIds = [ tag.id for tag in existingTags ]
      scan.taxonomy = existingTags

      for tag in tags:
        if tag['key'] in existingTagIds:
          continue

        newTag = Taxonomy(
          id = tag['key'],
          name = tag['vernacularName'] if 'vernacularName' in tag else tag['canonicalName'],
          parent_id = tag['parentKey'] if 'parentKey' in tag else None
        )
        db.session.add(newTag)
        scan.taxonomy.append(newTag)

    for file in form.attachments.data:
        import string
        import random
        filename = secure_filename(file.filename)
        location = safe_join('uploads', ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)) + filename)
        file.save(location)
        attachment = ScanAttachment(
          name = filename,
          file = File(
            # Todo: This should be a user-supplied string
            title = filename,
            filename = filename,
            location = location,
            owner_id = current_user.id,
            size = os.stat(location).st_size,
            # Todo: Get this properly - use python-magic?
            mime_type = 'image/png'
          )
        )
        db.session.add(attachment)
        scan.attachments.append(attachment)

    if form.published.data:
      form_valid = form.validate()
      if not scan.source:
        form_valid = False
        form.file.errors.append('A scan file is required')

      if not scan.attachments:
        form_valid = False
        form.stills.errors.append('A still is required')

      if form_valid:
        scan.published = True
        db.session.commit()
        return redirect(url_for('edit_scan', scan=scan))

    scan.published = False

    db.session.commit()

  if form.pub_query.data:
    pubs = Publication.query.filter(Publication.title.contains(form.pub_query.data))
    form.publications_search.choices = set([(pub.id, pub.title) for pub in pubs]) - set(form.publications.choices)

  data = {
      'form': form.serialize(),
      'scan': scan.serialize() if scan else None,
      'csrf_token': g.csrf_token
  }

  return render_vue(data, title='Edit' if scan else 'Upload New', menu='library')

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

@app.route('/publications/manage-publications/')
def manage_publications():
  pass

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

@app.route('/contribute')
def contribute():
  pass

def render_vue(data, title, menu):
  if request.accept_mimetypes.accept_html:
    return render_template('base.html', content=vue(data), title=title, menu=menu)
  return jsonify(data)


# This is for server-side rendering a view in vue
# pass the url path and an object to be provided as the defaultData property to the vue model
def vue(defaultData = None):
  path = request.full_path
  pipes = subprocess.Popen(['node', '--experimental-modules', 'app/vue/server.js', path, json.dumps(defaultData)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  std_out, std_err = pipes.communicate()

  if pipes.returncode != 0:
      # an error happened!
      err_msg = "%s. Code: %s" % (std_err.decode().strip(), pipes.returncode)
      raise Exception(err_msg)

  elif len(std_err):
    app.logger.error(std_err.decode())

  return std_out.decode()
