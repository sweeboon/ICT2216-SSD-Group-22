# Stage 1: Build React app
FROM node:16 as build-react
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Setup Flask app
FROM python:3.11-slim as build-flask
WORKDIR /usr/src/app

# Copy React build files and package.json from the first stage
COPY --from=build-react /usr/src/app/build ./frontend/build
COPY --from=build-react /usr/src/app/package*.json ./
COPY --from=build-react /usr/src/app/yarn.lock ./

# Install system dependencies and Python virtual environment
RUN apt-get update && apt-get install -y bash curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs npm && \
    npm install -g yarn && \
    apt-get clean

# Copy the Flask app code
COPY ./server ./server

# Create and activate virtual environment, install dependencies
RUN python -m venv venv && \
    /bin/bash -c "source /usr/src/app/server/venv/bin/activate && pip install --upgrade pip && pip install -r /usr/src/app/server/requirements.txt"

# Set environment variables
ENV FLASK_APP=server.api
ENV NODE_OPTIONS=--openssl-legacy-provider

# Expose the ports on which the apps will run
EXPOSE 5000
EXPOSE 3000

# Install Node.js dependencies for the React app
WORKDIR /usr/src/app
RUN yarn install

# Start both Flask and React apps
CMD ["/bin/bash", "-c", "cd /usr/src/app && source /usr/src/app/server/venv/bin/activate && yarn start"]
