To activate the virtual environment:

# Phenome 10K

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

To run tests, use the `pytest` command. For coverage use the --cov arg with the `app` directory:

```bash
pytest --cov=app
```
