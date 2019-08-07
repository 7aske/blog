# Personal blog

## Description

This is more of a fun oppurtinity to learn more about Flask and templating engines rather than a proper project that I intend to use actively. But you never know I might end up ranting about JavaScript ecosystem from time to time or post my recent projects.

## Packages

Back-end is handled by python's `Flask` framework while the front-end is written using `Jinja2` and in my own fashion vanilla `JavaScript`. For `CSS` frameworks I've decided to use [Materialize.css](https://materializecss.com) which is a big step up from `Bootstrap` in terms how the design looks and feels. Blog posts and comments are saved in a `Mongodb` database running on the same sever as `Flask`. I've done a cleaver little hack to avoid ever having to configure the database. Python server itself starts the process and manages crating the root user and initial `posts` collection.

## Dependencies

* Server:
    * Flask
    * Flask-PyMongo
    * Flask-CORS
    * shortuuid 
    
* Client:
    * axios
    * materialize-css
    * showdown
    * simplemde

## Usage

Assuming you have a virtual environment setup:

`$ FLASK_ENV=development ./venv/bin/flask run --host="0.0.0.0"`