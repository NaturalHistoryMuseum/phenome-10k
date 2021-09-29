import click
from flask.cli import FlaskGroup
from phenome10k.models import User, Scan, Taxonomy
from phenome10k.extensions import db
from phenome10k.data.gbif import pull_tags
from phenome10k import create_app


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
    user = User(
        id=1,
        name='Administrator',
        email='admin',
        role='ADMIN'
    )

    user = db.session.merge(user)

    if user.check_password(password):
        db.session.commit()
        click.echo('Password not changed', err=True)
        return

    user.set_password(password)
    db.session.commit()

    click.echo('Password changed')


@cli.command()
def update_gbif_tags():
    """ Updates taxonomy tags from gbif backbone and deletes unused ones."""
    click.echo('Updating tags:')
    for scan in Scan.query.filter(Scan.gbif_id).all():
        tags = [
            db.session.merge(tag) for tag in pull_tags(scan.gbif_id)
        ]
        scan.taxonomy = tags
        click.echo(' - ' + scan.scientific_name)

    click.echo('Deleting tags:')
    for tax in Taxonomy.query.filter(db.not_(Taxonomy.scans.any())):
        click.echo(' - ' + tax.name)
        db.session.delete(tax)
    db.session.commit()


if __name__ == '__main__':
    cli()
