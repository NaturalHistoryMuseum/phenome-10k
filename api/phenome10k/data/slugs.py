from werkzeug.utils import secure_filename

from ..models import Scan, Publication


def slug_available(slug):
    """
    Returns true if the slug url is available.
    """
    return (Scan.query.filter_by(url_slug=slug).first() is None) and (
        Publication.query.filter_by(url_slug=slug).first() is None
    )


def generate_slug(name):
    """
    Generate a URL slug for a given name.
    """
    # Slugify the title and check
    slug = secure_filename(name).lower().replace('_', '-')
    slug_n = slug
    n = 1

    # Append an increasing number to the slug until we find an available url
    while not slug_available(slug_n):
        n += 1
        slug_n = slug + '-' + str(n)

    return slug_n
