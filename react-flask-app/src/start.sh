#!/bin/bash
# Start the Flask app
cd /usr/src/app/server
source venv/bin/activate
flask run --host=0.0.0.0 --port=5000 &
# Start the React app
cd /usr/src/app
yarn start
