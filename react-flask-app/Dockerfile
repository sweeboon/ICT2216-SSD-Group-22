# Use the official base image with Node.js 16
FROM node:16

# Set the working directory
WORKDIR /usr/src/app

# Copy the package.json and yarn.lock files
COPY react-flask-app/package*.json react-flask-app/yarn.lock ./

# Install Node.js dependencies
RUN yarn install

# Copy the rest of the application code
COPY react-flask-app/ .

# Setup Python environment
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip

# Verify the files are in the expected locations
RUN ls -l /usr/src/app/react-flask-app/server/

# Create and activate a virtual environment
RUN python3 -m venv /usr/src/app/react-flask-app/server/venv
RUN /usr/src/app/react-flask-app/server/venv/bin/pip install -r /usr/src/app/react-flask-app/server/requirements.txt

# Expose ports
EXPOSE 3000 5000

# Start the application using concurrently
CMD ["npx", "concurrently", "\"yarn start\"", "\"cd server && ../venv/bin/flask run --host=0.0.0.0 --port=5000\""]
