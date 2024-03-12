import click
from flask.cli import FlaskGroup
from phenome10k import create_app
from phenome10k.data.gbif import pull_tags
from phenome10k.extensions import db, security
from phenome10k.models import User, Scan, Taxonomy


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
    security.datastore.commit()

    click.echo('Admin password set.')


@cli.command()
def update_gbif_tags():
    """
    Updates taxonomy tags from gbif backbone and deletes unused ones.
    """
    click.echo('Updating tags:')
    for scan in Scan.query.filter(Scan.gbif_species_id).all():
        tags = [db.session.merge(tag) for tag in pull_tags(scan.gbif_species_id)]
        scan.taxonomy = tags
        click.echo(' - ' + scan.scientific_name)

    click.echo('Deleting tags:')
    for tax in Taxonomy.query.filter(db.not_(Taxonomy.scans.any())):
        click.echo(' - ' + tax.name)
        db.session.delete(tax)
    db.session.commit()


if __name__ == '__main__':
    cli()
