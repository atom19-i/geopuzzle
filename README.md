[![CircleCI](https://circleci.com/gh/TyVik/geopuzzle.svg?style=svg)](https://circleci.com/gh/TyVik/geopuzzle)
[![BrowserStack Status](https://www.browserstack.com/automate/badge.svg?badge_key=Fbm86tXoBBqACUnFaJqP)](https://www.browserstack.com/automate/public-build/Fbm86tXoBBqACUnFaJqP)
[![codecov](https://codecov.io/gh/TyVik/geopuzzle/branch/develop/graph/badge.svg)](https://codecov.io/gh/TyVik/geopuzzle)

[![Total alerts](https://img.shields.io/lgtm/alerts/g/TyVik/geopuzzle.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/TyVik/geopuzzle/alerts/)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/TyVik/geopuzzle.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/TyVik/geopuzzle/context:python)
[![Language grade: JavaScript](https://img.shields.io/lgtm/grade/javascript/g/TyVik/geopuzzle.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/TyVik/geopuzzle/context:javascript)

[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=TyVik_geopuzzle&metric=sqale_rating)](https://sonarcloud.io/dashboard?id=TyVik_geopuzzle)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=TyVik_geopuzzle&metric=alert_status)](https://sonarcloud.io/dashboard?id=TyVik_geopuzzle)
[![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=TyVik_geopuzzle&metric=reliability_rating)](https://sonarcloud.io/dashboard?id=TyVik_geopuzzle)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=TyVik_geopuzzle&metric=security_rating)](https://sonarcloud.io/dashboard?id=TyVik_geopuzzle)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=TyVik_geopuzzle&metric=sqale_index)](https://sonarcloud.io/dashboard?id=TyVik_geopuzzle)

# Intro

![geopuzzle](https://github.com/TyVik/geopuzzle/raw/1e8c970da66e35d8e11f9805355c7d041c7ebc95/static/images/puzzle.gif) 
Arrange the pieces of the world! You need to drag the shape of the territory to the right place. 
Just like in childhood we collected pictures piece by piece, so here you can collect a country 
from regions or whole continents from countries! 

Furthermore second variation is the Quiz. In the Quiz you need find the country by flag, emblem 
or the capital. 

# Installation

This is just web application, so you need:

1. nginx 
2. uwsgi
3. supervisor
4. python >= 3.8
5. redis
6. postgres >= 12
7. nodejs >= 12.13

## System applications

Install nginx, uwsgi, supervisor and other packages:
```bash
$ sudo apt install nginx uwsgi uwsgi-plugin-python3 supervisor redis-server
$ sudo apt install gdal-bin gettext build-essential python3-dev libpq-dev
```

Template config files for nginx, uwsgi and supervisor are placed in `deploy` directory.
I hope python 3 with pipenv already installed :)

## Create virtual environment

```bash
$ pipenv install
```

## Create database

1. Install Postgres with PostGIS:
    ```
    $ sudo apt install postgresql postgresql-contrib postgis
    ```

2. Install postgis extension:
    ```
    $ sudo su postgres -c psql
    postgres=# create user geopuzzle with password 'geopuzzle';
    postgres=# create database geopuzzle owner geopuzzle;
    ``` 
3. Create user and database:
    ```
    $ sudo su postgres -c psql
    postgres=# \c geopuzzle
    geopuzzle=# create extension postgis;
    geopuzzle=# create extension postgis_topology;
    geopuzzle=# create extension postgis_sfcgal;
    geopuzzle=# create extension fuzzystrmatch;
    geopuzzle=# create extension address_standardizer;
    geopuzzle=# create extension postgis_tiger_geocoder;
    ```
4. Create `.env` file (based on `.env_template`) in project root with environment settings. 
Required parameters were already initialed default values in template file;
5. Create tables:
    ```
    (venv)$ ./manage.py migrate
    ```

## Set up env variables

All environment variables are collected in .env file (.env_template is template for that). 
Some variables such as REDIS_HOST or DJANGO_SETTINGS_MODULE do not require explanation. 
But some are specific to the project:

* OSM_KEY need only for load polygons into database
* GOOGLE_KEY is production key for Google Maps API (preferred, but not required)
* RAVEN_DSN for collect errors to Sentry (optional)
* AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY need only for AWS settings usage. Can left them blank.


## Build static files

Install nodejs:
```
$ sudo apt install nodejs npm
$ npm init
$ npm run build
(geopuzzle) $ ./manage.py collectstatic
```

# Load data

I find excellent service for load geojson files with polygons - https://osm-boundaries.com/.
Just select the country (or many or with regions) and click 'Export'. URL must be like:
```
https://osm-boundaries.com/Download/Submit?apiKey=74ba654a378b8daf80f&db=osm20210531&osmIds=-5682946,-5682950&format=GeoJSON&srid=4326
```
And download content by that link. You've got zip archive with GeoJson files, unpack them into `geojson` folder.
After that you can run management command `(venv)$ ./manage.py update_regions` for load polygons into database.
Take into account - data from OSM is not perfect and some regions can have bad or recursive links to each other.
In most cases, restarting can help :) 

# Management commands

Management command usually run via manage.py script, for example: `./manage.py import_region`.

* `cache` - import/export and recalculate cache (from postgres)
* `import_region` - load one .geojson into database
* `update_infobox` - update infobox from WikiData
* `update_regions` - load all .geojson into database from `geojson` folder
* `validate_infoboxes` - check that all required data in all infoboxes is filled and correct

# Docker images

Project has 2 Dockerfiles:

* /Dockerfile.backend - for server side (django tests and deploy)
* /Dockerfile.frontend - for client side (webpack build bundles and jest tests for future)

All images should be up to date with all installed dependencies. This allows you to significantly reduce the time to perform tasks CI.
Command for update image (frontend, by example):

```bash
$ docker build -t tyvik/geopuzzle:frontend -f Dockerfile.frontend .
$ docker push tyvik/geopuzzle:frontend
```

# Run in dev mode with Docker Compose

Build and run:

```bash
$ docker-compose build
$ docker-compose up -d
```

Stop:

```bash
$ docker-compose stop
```

You can download [sample database](https://drive.google.com/open?id=1H_JUXr39Q-W2_153qHgbQD80FOUSU-JM).
Unpack archive into `pgdata` directory.

Or download dump as [sql file](https://drive.google.com/open?id=1OGXl7P9dkevD_v7QgBoW8CbsQxDjW7EI).

Go to [http://localhost:8000](http://localhost:8000)

# Useful links

* https://osm-boundaries.com/
* http://global.mapit.mysociety.org/areas/O03 - http://mapit.poplus.org/docs/self-hosted/how-data-is-stored/
* http://geo.koltyrin.ru/
* http://www.marineregions.org/gazetteer.php?p=browser&id=1900&expand=true#ct

# Useful services

[<img src="https://cloud.githubusercontent.com/assets/7864462/12837037/452a17c6-cb73-11e5-9f39-fc96893bc9bf.png" alt="Browser Stack Logo" width="400">](https://www.browserstack.com/)