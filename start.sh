#!/bin/sh
gunicorn app.main:app --bind 0.0.0.0:10000
