# Stage 1: Build React app
FROM node:14 as build-react

WORKDIR /usr/src/app

COPY ./src/package*.json ./
RUN yarn install

COPY ./src .
RUN NODE_OPTIONS=--openssl-legacy-provider yarn build

# Stage 2: Build Flask app
FROM python:3.11-slim as build-flask

WORKDIR /usr/src/app

COPY ./server /usr/src/app/server

RUN python -m venv /usr/src/app/venv && \
    . /usr/src/app/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r /usr/src/app/server/requirements.txt --break-system-packages

# Stage 3: Runtime environment
FROM python:3.11-slim

WORKDIR /usr/src/app

# Copy built React app from Stage 1
COPY --from=build-react /usr/src/app/build /usr/src/app/build

# Copy Flask app from Stage 2
COPY --from=build-flask /usr/src/app/venv /usr/src/app/venv
COPY --from=build-flask /usr/src/app/server /usr/src/app/server

# Install serve globally
RUN npm install -g serve

# Expose the ports
EXPOSE 5000 3000

# Start the Flask and React applications
CMD /bin/bash -c "\
    cd /usr/src/app/server && . /usr/src/app/venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & \
    serve -s /usr/src/app/build -l 3000"
