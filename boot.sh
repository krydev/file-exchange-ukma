#!/bin/bash
gunicorn -b 0.0.0.0:$PORT --access-logfile - --error-logfile - manage:app --daemon
python worker.py
