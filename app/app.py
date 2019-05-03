""" This is the main flask routing module """
from os import path
from flask import Flask, url_for
from flask_basicauth import BasicAuth
from worker import celery
import celery.states as states
import yaml

# app initialization
app = Flask(__name__, static_url_path='/app/static')

# Read info for Basic Auth user:pwd
with open("/app/private/conf.yaml", 'r') as f_in:
        yamlContent = yaml.load(f_in, Loader=yaml.FullLoader)
        app.config['BASIC_AUTH_USERNAME'] = yamlContent['BASIC_AUTH_USERNAME']
        app.config['BASIC_AUTH_PASSWORD'] = yamlContent['BASIC_AUTH_PASSWORD']

# Basic Auth config
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

# App Routing.
@app.route("/")
@basic_auth.required
def index():
    """ Serve static page """
    return app.send_static_file('index.html')

# Force run outside schedule.
@basic_auth.required
@app.route('/run')
def force_run() -> str:
    force = True
    task = celery.send_task('tasks.run', args=[force], kwargs={})
    response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>Check the current status of {task.id} </a>"
    return response

# Check the status of the run.
# This may be outdated since we have Flower!
@basic_auth.required
@app.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)
