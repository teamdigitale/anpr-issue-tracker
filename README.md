# Github Issue Tracker

This web app aims at tracking the issues on a certain repository and display
some statistics on a webpage.

# Deployment
At the moment, the app is Dockerized.
Use this 

``` bash
 docker run -p 8001:80 -v $(pwd)/private/:/app/app/private:rw -e TZ=Europe/Rome
 ghanpr
```

# Known issues
* For some reasons (still unknown), if the `apscheduler` is immediately started
  inside the dockerized instance with this command:

  ```python
  sched.add_job(run.main, 'interval', days=7, next_run_time=datetime.now())
  ```
  the job is started in a synchronous way and nginx does not accept any
  requests. Same thing happens when using `job.func()` inside the `force_run()`
  function. 
  Probably this is due to the thread handling system, since running the flask
  app locally works as expected.
  NOTE: it may also be related to a timezone issue.
 

# License
GNU Affero GPL v3.0 or later
