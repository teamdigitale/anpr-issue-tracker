""" This is the main flask routing module """
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from .modules import run
from flask_basicauth import BasicAuth
from os import path
import yaml

# app initialization
app = Flask(__name__, static_url_path='/app/app/static')

# Monkey patch for user:pwd
my_path = path.abspath(path.dirname(__file__))
with open(path.join(my_path, "private/conf.yaml"), 'r') as f_in:
        yamlContent = yaml.load(f_in, Loader=yaml.FullLoader)
        app.config['BASIC_AUTH_USERNAME'] = yamlContent['BASIC_AUTH_USERNAME']
        app.config['BASIC_AUTH_PASSWORD'] = yamlContent['BASIC_AUTH_PASSWORD']

app.config['BASIC_AUTH_FORCE'] = True

basic_auth = BasicAuth(app)

# Scheduler initialization
# Calling 'run.main' every 7 days
sched = BackgroundScheduler(daemon=True, timezone='Europe/Rome')
# Does not start automatically
sched.add_job(run.main, 'interval', days=7)
sched.start()

@app.route("/")
@basic_auth.required
def hello():
    """ Serve static page """
    return app.send_static_file('index.html')

@app.route("/run")
def force_run():
    """ Run job now """
    for job in sched.get_jobs():
        # job.modify(next_run_time=datetime.now(), kwargs={"force":True})
        # WARNING: This is a synchronous call
        job.func(force=True)
    return "Job scheduled to run in a minute. Go back <a href='/'>HOME</a>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
