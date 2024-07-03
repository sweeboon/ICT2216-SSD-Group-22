# Use an official Node.js runtime as a parent image
FROM node:16

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and yarn.lock files
COPY react-flask-app/src/package*.json ./react-flask-app/src/
COPY react-flask-app/server/requirements.txt ./react-flask-app/server/

# Install Node.js dependencies
RUN cd react-flask-app/src && yarn install

# Install Python dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip && \
    python3 -m venv react-flask-app/server/venv && \
    bash -c "source react-flask-app/server/venv/bin/activate && pip install -r react-flask-app/server/requirements.txt"

# Copy the rest of the application code
COPY . .

# Expose ports
EXPOSE 3000 5000

# Default command
CMD ["bash"]
