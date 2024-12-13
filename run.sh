#!/bin/bash
export FLASK_ENV=production
gunicorn --workers 4 --bind 0.0.0.0:8000 app:app 