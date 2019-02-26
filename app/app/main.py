from flask import Flask, request
from apscheduler.schedulers.background import BackgroundScheduler
from .modules import run
app = Flask(__name__, static_url_path='/static')
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Europe/Rome'})
scheduler.start()

@app.route("/")
def hello():
    return app.send_static_file('index.html')

@app.route("/scheduler")
def run_task():
    scheduler.add_job(func=run.main, trigger='cron', day_of_week='0') 
    return 'Schedulato. Torna a <a href="/">Home</a>', 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
