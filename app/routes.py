import tempfile
import subprocess
import os
import uuid
import math
from functools import wraps
from zipfile import ZipFile, ZIP_DEFLATED
from flask import request, render_template, redirect, url_for, flash, send_from_directory, jsonify, g, Response, send_file, make_response
from flask.helpers import safe_join
from flask_login import current_user, login_user, login_required, logout_user
from werkzeug.routing import ValidationError, BaseConverter
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound, BadRequest, Forbidden
from stl.mesh import Mesh
from app import app, db, models
from app.forms import LoginForm, RegistrationForm, ScanUploadForm, PublicationUploadForm
from app.models import User, Scan, File, Publication, Tag, Taxonomy, Attachment, ScanAttachment, PublicationFile
import mimetypes
import subprocess
import json
from PIL import Image
import io
from flask_mail import Message
from app import mail

def hideScanFiles(data):
  if not current_user.is_authenticated:
    login = url_for('login')
    data['source'] = login
    for pub in data['publications']:
      for file in pub['files']:
        file['file'] = login
  return data

def ensureEditable(item):
  """ Throw Forbidden exception if the current user is not allowed to edit the given model """
  if not current_user.canEdit(item):
      raise Forbidden('You cannot edit this item as you are not the original author.')

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
    ctmFile = File.fromName(filename + '.ctm')
    ctmFile.mime_type = 'application/octet-stream'

    ctmConvert = subprocess.run(["ctmconv", uploadFile.name, ctmFile.location], stderr=subprocess.PIPE)
    if ctmConvert.returncode > 0:
      # TODO: Deal with this error properly
      app.logger.warn(ctmConvert.stderr)

    ctmFile.size = os.stat(ctmFile.location).st_size

    # Zip source file & save to large file storage
    # TODO: Configure large file storage
    zip = File.fromName(file.filename + '.zip')
    zip.mime_type = 'application/zip'

    with ZipFile(zip.location, 'w', ZIP_DEFLATED) as zipFile:
      zipFile.write(uploadFile.name)

    zip.size = os.stat(zip.location).st_size

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

class FileConverter(BaseConverter):
  def to_url(self, value):
    import re
    return BaseConverter.to_url(self, value if isinstance(value, str) else re.sub(r"^uploads/", "", value.location))

app.url_map.converters['scan'] = ScanConverter
app.url_map.converters['publication'] = PublicationConverter
app.url_map.converters['file'] = FileConverter

def slug_available(slug):
  """ Returns true if the slug url is availabe """
  app.logger.warn(slug)
  try:
    return not app.url_map.bind('').match('/' + slug)
  except NotFound:
    return True

def generate_slug(name):
  """ Generate a URL slug for a given name """
  if not name:
    return None

  # Slugify the title and check
  slug = secure_filename(name).lower().replace('_', '-')
  slug_n = slug
  n = 1

  # Append an increasing number to the slug until we find an available url
  while not slug_available(slug_n):
    n += 1
    slug_n = slug + '-' + str(n)

  return slug_n

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

@app.route('/uploads/<file:path>')
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

@app.route('/about/', methods=['GET', 'POST'])
def about():
  return render_template('about.html', title='About', menu='about')

@app.route('/login/', methods=['GET', 'POST'])
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

@app.route('/logout/')
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
@app.route('/tag/', methods=['GET','POST'])
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
    results = [ (tag, tag.scans.filter(scanConditions).all()) for tag in Tag.query.filter_by(category=sort).all() ]

    data = {
      'groups': [
        {
          'group': tag.name,
          'items': [
            s.serialize() for s in scans
          ]
        }
        for (tag, scans) in results if len(scans) > 0
      ]
    }
  else:
    query = Scan.scientific_name

    data = {
      'scans': [ s.serialize() for s in Scan.query.filter(scanConditions).order_by(query).all() ]
    }

  data['tags'] = Tag.tree()
  data['tags']['taxonomy'] = Taxonomy.tree()

  return render_vue(data, title="Library", menu='library')

@app.route('/library.rss')
def feed():
  """ Generate the RSS feed """
  scans = Scan.query.filter(Scan.published).order_by(Scan.date_created)
  resp = make_response(render_template('rss.xml', scans = scans))
  resp.headers['Content-type'] = 'application/rss+xml'
  return resp

@app.route('/library/manage-uploads/', methods=['GET', 'POST'])
@app.route('/library/manage-uploads/page/<int:page>/', methods=['GET', 'POST'])
@requiresContributor
def manage_uploads(page=1):
  """View a list of uploads with publish, edit, delete actions"""

  # Process delete request
  if request.method == 'POST':
    scan_id = request.form.get('delete')
    scan = Scan.query.get(scan_id)
    ensureEditable(scan)
    db.session.delete(scan)
    db.session.commit()
    return redirect(request.full_path)

  # To publish, we have to submit to the ScanUploadForm endpoint,
  # which requires a CSRF token. Construct the form to generate one.
  ScanUploadForm()

  per_page = 50
  offset = (page - 1) * per_page
  query = Scan.query
  startswith = request.args.get('char')
  if(startswith):
    query = query.filter(Scan.scientific_name.startswith(startswith))
  scans = query.paginate(page, per_page)
  data = {
    'scans': [ s.serialize() for s in scans.items if current_user.canEdit(s) ],
    'page': page,
    'total_pages': math.ceil(scans.total / per_page),
    'csrf_token': g.csrf_token
  }
  return render_vue(data, title="Manage Uploads", menu="library")

@app.route('/<scan:scan>/')
def scan(scan):
  if not scan.published and not (current_user.is_authenticated and current_user.canEdit(scan)):
    raise NotFound()
  data = hideScanFiles(scan.serialize())

  return render_vue(data, title=scan.scientific_name, menu='library')

@app.route('/stills/<int:id>/', methods=['DELETE'])
@login_required
def delete_still(id):
  """Url for deleting a still"""
  attachment = ScanAttachment.query.filter_by(attachment_id=id).first()
  return_to = url_for('library')

  if attachment:
    ensureEditable(attachment)
    return_to = url_for('edit_scan', scan=attachment.scan)
    db.session.delete(attachment)
    db.session.commit()

  # Use a 303 response to force browser to use GET for the next request
  return redirect(return_to, code=303)

@app.route('/<scan:scan>/stills/')
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

@app.route('/<scan:scan>/edit-scan', methods=['GET', 'POST'])
@app.route('/library/create/', methods=['GET', 'POST'])
@requiresContributor
def edit_scan(scan = None):
  form = ScanUploadForm(obj=scan)

  if scan:
    ensureEditable(scan)

    if not form.geologic_age.data:
      form.geologic_age.data = scan.geologic_age

    if not form.ontogenic_age.data:
      form.ontogenic_age.data = scan.ontogenic_age

    if not form.elements.data:
      form.elements.data = scan.elements

  # Get the records for the currently selected publications
  pubs = Publication.query.filter(Publication.author_id == current_user.id).all()
  form.publications.choices = [(pub, pub.title) for pub in pubs]

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
    scan.specimen_url = form.specimen_url.data
    scan.description = form.description.data
    scan.publications = form.publications.data

    scan.tags = form.geologic_age.data + form.ontogenic_age.data + form.elements.data

    gbif_id = form.gbif_id.data

    if gbif_id and gbif_id != scan.gbif_id:
      scan.gbif_id = gbif_id
      import urllib.request, json
      with urllib.request.urlopen("http://api.gbif.org/v1/species/" + str(gbif_id) + "/parents") as url:
        tags = json.loads(url.read().decode())
      with urllib.request.urlopen("http://api.gbif.org/v1/species/" + str(gbif_id)) as url:
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
      if isinstance(file, Attachment):
        continue
      import string
      import random
      import magic

      # Take the filename as the label and generate a new, safe filename
      label = file.filename
      filename = secure_filename(file.filename) + '.png'

      fileModel = File.fromBinary(filename, file.stream)

      if (fileModel.mime_type != 'image/png'):
        form.stills.errors.append('Stills must be png files')
      else:
        file.save(fileModel.location)
        attachment = Attachment(
          name = label,
          file = fileModel
        )
        db.session.add(attachment)
        scan.attachments.append(attachment)

    form_valid = True

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
    else:
      scan.published = False

    if form_valid:
      db.session.commit()
      return redirect(request.args.get('redirect') or url_for('edit_scan', scan=scan))

  data = {
      'form': form.serialize(),
      'scan': scan.serialize() if scan else None,
      'csrf_token': g.csrf_token
  }

  return render_vue(data, title='Edit' if scan else 'Upload New', menu='library')

@app.route('/publications/create/', methods=['GET', 'POST'])
@app.route('/<publication:publication>/edit-pub', methods=['GET', 'POST'])
def edit_publication(publication=None):
    form = PublicationUploadForm(obj=publication)

    if publication:
      ensureEditable(publication)

    if form.validate_on_submit():
      if not publication:
        publication = Publication(
          author_id = current_user.id,
          url_slug = generate_slug(form.title.data)
        )
        db.session.add(publication)
      publication.title = form.title.data
      publication.pub_year = form.pub_year.data
      publication.authors = form.authors.data
      publication.journal = form.journal.data
      publication.link = form.link.data
      publication.abstract = form.abstract.data
      publication.published = True

      for file in form.files.data:
        if file == '':
          continue
        f = File.fromUpload(file)
        db.session.add(f)
        publication.files.append(
          Attachment(
            file = f,
            name = file.filename
          )
        )

      db.session.commit()

      return redirect(url_for('edit_publication', publication=publication))

    data = {
      'publication': publication.serialize() if publication else None,
      'form': form.serialize(),
      'csrf_token': g.csrf_token
    }

    return render_vue(data, title='Edit' if publication else 'Create', menu='publications')

@app.route('/remove-pub-file/<int:id>', methods=['DELETE'])
@requiresContributor
def delete_pub_file(id):
  """Url for deleting a file"""
  attachment = PublicationFile.query.filter_by(attachment_id=id).first()
  return_to = url_for('publications')

  if attachment:
    ensureEditable(attachment)
    return_to = url_for('edit_publication', publication=attachment.publication)
    db.session.delete(attachment)
    db.session.commit()

  # Use a 303 response to force browser to use GET for the next request
  return redirect(return_to, code=303)

@app.route('/publications/')
@app.route('/publications/page/<int:page>/')
def publications(page = 1):
  per_page = 100

  title = request.args.get('title')
  mine = 'mine' in request.args.keys()

  if title:
    query = Publication.query.filter(Publication.title.ilike('%{0}%'.format(title)))
  else:
    query = Publication.query

  if mine and current_user.is_authenticated:
    query = query.filter(Publication.author_id == current_user.id)

  pubs = query.filter_by(published = True).paginate(page, per_page)

  data = {
    'publications': [ pub.serialize() for pub in pubs.items ],
    'page': page,
    'total_pages': math.ceil(pubs.total / per_page)
  }

  return render_vue(data, title='Publications', menu='publications')

@app.route('/publications/manage-publications/', methods=['GET', 'POST'])
@app.route('/publications/manage-publications/page/<int:page>/', methods=['GET', 'POST'])
@requiresContributor
def manage_publications(page=1):
  """View a list of publications with publish, edit, delete actions"""

  # Process delete request
  if request.method == 'POST':
    action = request.form.get('action')
    publication_id = request.form.get('id')
    if publication_id:
      publication = Publication.query.get(publication_id)
      ensureEditable(publication)

      if action == 'delete':
        db.session.delete(publication)
        db.session.commit()
      elif action == 'publish':
        publication.published = True
        db.session.commit()
      elif action == 'unpublish':
        publication.published = False
        db.session.commit()
    return redirect(request.full_path)

  per_page = 50
  offset = (page - 1) * per_page
  query = Publication.query
  pub_year = request.args.get('pub_year')
  if(pub_year):
    query = query.filter_by(pub_year = pub_year)
  publications = query.paginate(page, per_page)
  data = {
    'publications': [ pub.serialize() for pub in publications.items if current_user.canEdit(pub) ],
    'page': page,
    'total_pages': math.ceil(publications.total / per_page),
    'years': [ y[0] for y in db.session.query(Publication.pub_year).order_by(Publication.pub_year.desc()).distinct().all() ]
  }
  return render_vue(data, title="Manage Publications", menu="publications")

@app.route('/<publication:publication>/')
def publication(publication):
  if not publication.published and not (current_user.is_authenticated and current_user.canEdit(publication)):
    raise NotFound()
  return render_vue(publication.serialize(), title=publication.title, menu='publications')

@app.route('/contribute/', methods=['GET', 'POST'])
def contribute():
  if current_user.is_authenticated and request.method == 'POST':
    message = request.form.get('message')

    body = current_user.name + " would like to become a contributor to Phenome10k:\n\n"
    html = current_user.name + " would like to become a contributor to Phenome10k:<br><br>"

    if message:
      body += '"' + message + '"\n\n'
      html += '<blockquote>"' + message + '"</blockquote><br><br>'

    profileLink = url_for('users', id=current_user.id, _external=True)

    body += (
      "To approve their request, use the following link:\n" + profileLink
    )
    html += "<a href='" + profileLink + "'>Approve this request</a>"

    mail.send(Message(
      recipients = [app.config['ADMIN_EMAIL']],
      reply_to = (current_user.name, current_user.email),
      subject = current_user.name + " has requested to become a Phenome10k contributor",
      body = body,
      html = html
    ))
  return render_template('contribute.html', title='Contributing', menu='home')

@app.route('/users', methods=['GET', 'POST'])
@requiresAdmin
def users():
  error = ''

  if request.method == 'POST':
    id = request.form.get('id')
    user = User.query.get(id)

    if user:
      # Todo: Validation and errors
      user.role = request.form.get('role')
      db.session.commit()
      return redirect(url_for('users'))
    else:
      error = 'No user was found for id ' + id

  query = User.query
  id = request.args.get('id')

  if id:
    query = query.filter_by(id=id)

  users = [ user.serialize() for user in query.all() ]
  data = { 'users': users, 'error': error }

  return render_vue(data, title = 'Users')


def render_vue(data, title, menu = None):
  if request.accept_mimetypes.accept_html:
    return render_template('base.html', content=vue(data), title=title, menu=menu)
  return jsonify(data)

# This is for server-side rendering a view in vue
# pass the url path and an object to be provided as the defaultData property to the vue model
def vue(defaultData = None):
  path = request.full_path
  pipes = subprocess.Popen(['node', 'app/vue/server.js', path, json.dumps(defaultData)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  std_out, std_err = pipes.communicate()

  if pipes.returncode != 0:
      # an error happened!
      err_msg = "%s. Code: %s" % (std_err.decode().strip(), pipes.returncode)
      raise Exception(err_msg)

  elif len(std_err):
    app.logger.error(std_err.decode())

  return std_out.decode()
