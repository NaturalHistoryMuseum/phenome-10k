import click
from flask.cli import FlaskGroup
from phenome10k import create_app
from phenome10k.data.gbif import pull_tags
from phenome10k.extensions import db, security, cache
from phenome10k.models import User, Scan, Taxonomy
from datetime import datetime as dt
from sqlalchemy import select


def create_cli_app(info):
    app = create_app()

    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'User': User, 'Scan': Scan}

    return app


@click.group(cls=FlaskGroup, create_app=create_cli_app)
def cli():
    """
    CLI for phenome10k.
    """
    pass


@cli.command()
@click.argument('password')
def set_admin_pw(password):
    user = security.datastore.find_user(email='admin')
    if not user:
        user = security.datastore.create_user(name='Administrator', email='admin')
    security.datastore.add_role_to_user(user, 'ADMIN')

    user.set_password(password)

    # make sure admin user is active and confirmed
    user.active = True
    if user.confirmed_at is None:
        user.confirmed_at = dt.now()

    security.datastore.commit()

    click.echo('Admin password set.')


@cli.command()
def update_gbif_tags():
    """
    Updates taxonomy tags from gbif backbone and deletes unused ones.
    """
    click.echo('Updating tags:')
    species_ids = db.session.execute(
        select(Scan.gbif_species_id)
        .where(Scan.gbif_species_id.isnot(None))
        .group_by(Scan.gbif_species_id)
    )
    for sid in species_ids:
        tags = [db.session.merge(tag) for tag in pull_tags(sid[0])]
        db.session.commit()
        if len(tags) == 0:
            continue
        for scan in Scan.query.filter(Scan.gbif_species_id == sid[0]):
            scan.taxonomy = tags
        click.echo(' - ' + tags[-1].name)

    click.echo('Deleting tags:')
    for tax in Taxonomy.query.filter(db.not_(Taxonomy.scans.any())):
        click.echo(' - ' + tax.name)
        db.session.delete(tax)
    db.session.commit()

    click.echo('Clearing taxonomy tree cache:')
    is_deleted = cache.delete('taxonomy_tree')
    click.echo('Deleted.' if is_deleted else 'Did not exist or could not be deleted.')


if __name__ == '__main__':
    cli()
