# Stage 1: Build the application
FROM node:18 as build

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies
RUN npm install && npm install -g concurrently

# Copy the rest of the application code
COPY . .

# Build the application
RUN npm run build

# Stage 2: Setup the final image
FROM python:3.9-slim

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y nginx curl gnupg wget && \
    curl -sL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs yarn && \
    rm -rf /var/lib/apt/lists/*

# Copy built files from the previous stage
COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Copy your application code
COPY . /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Install Python dependencies within a virtual environment
RUN python3 -m venv /usr/src/app/server/venv && \
    /usr/src/app/server/venv/bin/pip install --upgrade pip && \
    /usr/src/app/server/venv/bin/pip install -r /usr/src/app/server/requirements.txt

# Install Node.js dependencies
RUN cd /usr/src/app/src && yarn install

# Expose the ports
EXPOSE 80 443 5000 3000

# Start the application
CMD /bin/bash -c "nginx && \
    cd /usr/src/app/server && source venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & \
    cd /usr/src/app/src && yarn start --port 3000"
