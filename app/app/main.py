""" This is the main flask routing module """
from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from .modules import run

# app initialization
app = Flask(__name__, static_url_path='/static')

# Scheduler initialization
# Calling 'run.main' every 7 days
sched = BackgroundScheduler(daemon=True)
sched.add_job(run.main, 'interval', days=7)
sched.start()

@app.route("/")
def hello():
    """ First function to be called """
    return app.send_static_file('index.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
