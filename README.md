# dystwitic

`dystwitic` is a near real-time sentiment analyzer and geospatial 
visualizer of tweets.

## Requirements

`dystwitic` depends on [MongoDB](http://mongodb.com), 
[Redis](http://redis.io), and [supervisord](http://supervisord.org).
Python dependencies can be found in 
[requirements.txt](/njmattes/dystwitic/blob/master/requirements.txt).
You'll also need to set up an app at 
[apps.twitter.com](https://apps.twitter.com/).
 
## Installation

Your package manager should have `redis-server` and `supervisor` available.
If it also has `mongod` that's great. But if
you're on Debian, you'll need to install MongoDB using the instructions
[here](https://docs.mongodb.com/manual/tutorial/install-mongodb-on-debian/).

Then install the python dependencies with 
`pip install -r {PATH_TO_PROJECT}/requirements.txt`.

Copy `supervisor.example.ini` to `supervisor.ini` and replace 
`{PATH_TO_VIRTUAL_ENV}` with the path to your virtual environment 
and `{PATH_TO_PROJECT}` with the path to wherever placed the project 
files.

This file can be included in your supervisord configuration, likely
at `/etc/supervisor/supervisord.conf`, in an `[include]` section
at the end of this file. 

Copy `dystwitic/config.example.py` to `dystwitic/config.py` and replace 
the keys and secrets in the `TwitterConfig` object with the relevant 
authorization information from your twitter app. You can replace (or not)
the `<REPLACE_ME>` values in the `FlaskConfig` object.

`nginx.example.conf` should provide a useful basis for testing. Replace 
`server_name`'s value with your domain and `{PATH_TO_PROJECT}` with the path to 
your project.

## How it works

The core of what's happening is this:

1. We're creating a stream of tweets that contain specified tags, which
   can be specified in the `TAGS` variable in `constants.py`. This 
   stream is monitored by supervisor so that if it goes down, there's
   some hope of restarting it on the fly.
2. Tweets that contain geospatial location information are ingested into
   a MongoDB collection. As they're ingested, a 
   [VADER](http://comp.social.gatech.edu/papers/icwsm14.vader.hutto.pdf) 
   sentiment analysis is computed for each tweet and ingested as well. 
   These tasks are queued with celery and also 
   monitored with supervisor.
3. A celery task also removes sufficiently old tweets from MongoDB
   to free up space and keep the application snappy.
4. Another process called `make_map()` in the `dystwitic.work.tasks` module
   runs with celery's beat scheduler. This process maps sentiment values between
   -1 and 1 to a color scale---the color scale can be defined with lists of
   RGB values in the `COLOR` dictionary in `constants.py`. Sentiment values 
   are interpolated against these colors, and those values are passed through 
   a  [radial basis function](https://en.wikipedia.org/wiki/Radial_basis_function)
   to create a 2-dimensional interpolated 'senitment map' around the globe. 
5. To save some amount of overhead this data is cached with Redis so that
   every visitor isn't duplicating the Rbf().
6. Optionally you can set `OBSFUCATE_COLORS` to `True`. This will create a 
   ridiculous and arbitray mapping of sentiment to color based on a VADER
   analysis of tweets containing color terms. It vastly increases overhead and
   decreases clarity. Double win!  
  
## Demo

You can see this code running at [http://dystwitic.earth](http://dystwitic.earth)