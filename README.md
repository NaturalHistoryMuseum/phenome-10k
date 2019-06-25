To activate the virtual environment:

# Phenome 10K



## Development

How to get it working:

First, make sure you have the following binaries available:
 - Python 3
 - Node 10
 - NPM 5.6
 - openctm-tools


```bash
# Install dependencies
pip install -r requirements.txt
npm i
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

You can run a local staging environment by spining up Vagrant:

```
vagrant up
```

The site will be available at phenome10k.localhost, and should reflect the production configuration
of the service.

## Production

The site's infrastructure is an HA architecture is composed of:
 - 2+ load balancers in active-passive HA configuration
 - 2+ application servers
 - Connected to external DB cluster and file server

The system can be deployed to production via ansible.
