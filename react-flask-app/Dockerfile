# Use the official base image
FROM node:16

# Set the working directory
WORKDIR /var/jenkins_home/workspace

# Copy package.json and yarn.lock first to leverage Docker cache
COPY package*.json yarn.lock ./

# Install Node.js dependencies
RUN yarn install

# Copy the rest of the application code
COPY . .

# Verify the files are in the expected locations
RUN ls -l /var/jenkins_home/workspace/react-flask-app/server/

# Setup Python environment
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip

# Create and activate a virtual environment
RUN python3 -m venv /var/jenkins_home/workspace/react-flask-app/server/venv
RUN /var/jenkins_home/workspace/react-flask-app/server/venv/bin/pip install -r /var/jenkins_home/workspace/react-flask-app/server/requirements.txt

# Expose ports
EXPOSE 3000 5000

# Start the application using concurrently
CMD ["npx", "concurrently", "\"yarn start\"", "\"cd server && ../venv/bin/flask run --host=0.0.0.0 --port=5000\""]
