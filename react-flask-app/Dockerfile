# Use an official Python and Node.js runtime as a parent image
FROM node:16

# Install Python and other dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip nginx

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and yarn.lock files for React
COPY react-flask-app/server/package*.json ./react-flask-app/server/

# Install Node.js dependencies
RUN cd react-flask-app/server && yarn install

# Copy Python requirements file
COPY react-flask-app/server/requirements.txt ./react-flask-app/server/

# Create and activate virtual environment, and install Python dependencies
RUN python3 -m venv react-flask-app/server/venv && \
    bash -c "source react-flask-app/server/venv/bin/activate && pip install -r react-flask-app/server/requirements.txt"

# Copy Nginx configuration file
COPY react-flask-app/nginx/nginx.conf /etc/nginx/nginx.conf

# Copy the rest of the application code
COPY . .

# Expose ports
EXPOSE 80
EXPOSE 443
EXPOSE 3000
EXPOSE 5000

# Command to start Nginx and the application
CMD ["bash", "-c", "source /usr/src/app/react-flask-app/server/venv/bin/activate && \
    cd /usr/src/app/react-flask-app/server && flask db migrate && yarn start & \
    nginx -g 'daemon off;'"]
