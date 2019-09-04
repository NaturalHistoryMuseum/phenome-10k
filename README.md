# Phenome 10K

## Development

How to get it working:

First, make sure you have the following binaries available:
 - Python 3
 - Node 10
 - NPM 5.6
 - openctm-tools

To create a new virtual environment:

```bash
python3 -m venv venv
```

To activate the virtual environment:

```bash
source venv/bin/activate
```

To install and run:

```bash
# Install dependencies
pip install -r requirements.txt
npm i
# Run database migrations
flask db upgrade
# Create the admin account
flask set-admin-pw pass
# Build the front end
node build
# Start
flask run
```

If you want to run in developer/debug mode:

```bash
node build/watch &
FLASK_DEBUG=1 flask run
```

The default user for a new site has the email address `admin` and the username `pass`.
Make sure to change this!

To run tests, use the `pytest` command. For coverage use the --cov arg with the `app` directory:

```bash
pytest --cov=app
```

## Local staging

Before running ansible you'll need to do a few things:

0. Make sure you're connected to the NHM internal network
1. Generate a Vault token:
   ```bash
   source vault-token
   ```
2. ```bash
   pip install hvac
   ```

You can run a local staging environment by spining up Vagrant:

```
vagrant up
```

Edit your `/etc/hosts` file to direct `phenome10k.localhost` to `192.168.10.21`.
The site will be available at phenome10k.localhost, and should reflect the production configuration
of the service.

## Production

The site's infrastructure is an HA architecture is composed of:
 - 2+ load balancers in active-passive HA configuration
 - 2+ application servers
 - 1 data server (db and nfs), to be replaced in future with cloud-based storage

The system can be deployed to production via ansible.