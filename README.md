# Phenome 10K

## Development

How to get it working:

First, make sure you have the following binaries available:
 - Python 3.8
 - Node 14.5
 - NPM 6.14

To create and/or activate the virtual environment:
```bash
source activate
```

This basically just runs the venv scripts:

```bash
# Create env
python3.8 -m venv venv
# Activate env
source venv/bin/activate
```

To install requirments and run:

```bash
# Install dependencies
pip install -r requirements.txt
npm i
# Run database migrations
flask db upgrade
# Create the admin account
flask set-admin-pw pass
# build the front end
npm build
# Start the front end
npm start &
# Start the task queue
scripts/tasks.sh &
# Start
flask run
```

If you want to run in developer/debug mode (with hot reload for both servers):

```bash
npm watch &
FLASK_DEBUG=1 flask run
```

`npm start` has to be restarted every time the frontend is rebuilt. If you are making frequent changes, `npm watch` is much easier as it handles both the bundling _and_ the server restarts.

The default user for a new site has the email address `admin` and the username `pass`.
Make sure to change this!

To run tests with coverage, use the `tests` script, or use `pytest` with custom arguments.

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

The system can be deployed to production via ansible:

```bash
ansible-playbook -iansible/inventories/production.ini ansible/playbook.yml -e@ansible/group_vars/production/main.yml -k -K  -ua-paulk6
```


## Adding database migrations

Add or modify models in models.py then run `flask db revision`
