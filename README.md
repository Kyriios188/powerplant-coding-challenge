# PowerPlant challenge implementation

## About

An implementation of the powerplant coding challenge from https://github.com/gem-spaas/powerplant-coding-challenge.
The challenge took me 3h30 to complete and does not cover all edge cases, but that's the most I can do in under 4 hours.

## Install & Run

### Without Docker

Run``pip install -r requirements.txt``preferably in a virtual environment.
Then run the main script with ``python main.py`` and interact with the API running on port 8888 at the `/productionplan` url.


### With Docker

Run ``docker build -t pp_challenge_robinsimon .`` to build the container and then ``docker run -it -p 8888:8888 pp_challenge_robinsimon`` to run it.

## Using the API

* The port 8888 must be available.
* The app listens to all interfaces.
* The request's Content-Type header must be set to ``application/json`` or the request will be rejected.


