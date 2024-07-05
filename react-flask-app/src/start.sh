#!/bin/bash
# Start the Flask app
cd /usr/src/app/server
source venv/bin/activate

# Start the React app
cd /usr/src/app
yarn start
