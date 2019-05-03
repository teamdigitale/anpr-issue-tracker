# Github Issue Tracker

This web app aims at tracking the issues on a certain repository and display
some statistics on a webpage.

# Structure 
The app is composed by a set of Docker containers organized as follows:

* Flask web app
* Redis 
* Celery Worker
* Celery Beat
* Celery Flower (optional)

# Deployment
At the moment, the orchestration is done using `docker-compose`.
As such, in order to have a working installation up and running you should:

``` bash
docker-compose up --build
```

This will build the images and run the containers in `interactive` mode. 
If you want you could just build the images with `docker-compose build` and
then run them later on with `docker-compose up`. 

# Author
Check the `AUTHORS.md` file in the repo root.

# License
GNU Affero GPL v3.0 or later
