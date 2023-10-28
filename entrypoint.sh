#!/bin/bash

pipenv run gunicorn -w 4 --bind 0.0.0.0:3000 --timeout 1800 run:app