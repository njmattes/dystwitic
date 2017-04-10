# dystwitic

`dystwitic` is a near real-time sentiment analyzer of a filtered stream of tweets.

## Requirements

Aside from the contents of 
[requirements.txt](/njmattes/dystwitic/blob/master/requirements.txt),
`dystwitic` also depends on [MongoDB](http://mongodb.com), 
[Redis](http://redis.io), and [supervisord](http://supervisord.org). 
You'll also need to set up an app at 
[apps.twitter.com](https://apps.twitter.com/).
 
## Installation
 
After setting up a virtual environment, 
`pip install -r PATH/TO/requirements.txt`.

Then copy `supervisor.example.ini` to `supervisor.ini` and replace 
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

## Demo

You can see this code running at [http://dystwitic.earth](http://dystwitic.earth)