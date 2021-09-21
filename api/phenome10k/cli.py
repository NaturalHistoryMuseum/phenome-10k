import click
from flask.cli import FlaskGroup
from phenome10k.models import User, Scan
from phenome10k.extensions import db
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
        print('Password not changed')
        return

    user.set_password(password)
    db.session.commit()

    print('Password changed')


if __name__ == '__main__':
    cli()
