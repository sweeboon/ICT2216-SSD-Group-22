# Use the official Nginx image as a base
FROM nginx:latest

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg python3 python3-venv python3-pip && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    npm install --global yarn

# Copy your application code
COPY . /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Install Python dependencies
RUN python3 -m venv server/venv && \
    . server/venv/bin/activate && \
    pip install -r server/requirements.txt

# Install Node.js dependencies
RUN cd src && yarn install

# Expose the ports
EXPOSE 80 443

# Start the application
CMD /bin/bash -c "nginx && \
    cd /usr/src/app/server && . venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & \
    cd /usr/src/app/src && yarn start"
