""" This is the main flask routing module """
from flask import Flask, url_for
from flask_basicauth import BasicAuth
from os import path
import yaml

from worker import celery
import celery.states as states

# app initialization
app = Flask(__name__, static_url_path='/app/app/static')

# Monkey patch for user:pwd
my_path = path.abspath(path.dirname(__file__))
with open(path.join(my_path, "private/conf.yaml"), 'r') as f_in:
        yamlContent = yaml.load(f_in, Loader=yaml.FullLoader)
        app.config['BASIC_AUTH_USERNAME'] = yamlContent['BASIC_AUTH_USERNAME']
        app.config['BASIC_AUTH_PASSWORD'] = yamlContent['BASIC_AUTH_PASSWORD']

# Basic Auth config
app.config['BASIC_AUTH_FORCE'] = True
basic_auth = BasicAuth(app)

# TODO: add scheduling

# App Routing.
@app.route("/")
@basic_auth.required
def index():
    """ Serve static page """
    return app.send_static_file('index.html')

# Force run outside schedule.
@app.route('/run')
def force_run() -> str:
    force = True
    task = celery.send_task('tasks.run', args=[force], kwargs={})
    response = f"<a href='{url_for('check_task', task_id=task.id, external=True)}'>Check the current status of {task.id} </a>"
    return response


# Check the status of the run.
# QUESTION: should we insert flower?
@app.route('/check/<string:task_id>')
def check_task(task_id: str) -> str:
    res = celery.AsyncResult(task_id)
    if res.state == states.PENDING:
        return res.state
    else:
        return str(res.result)
