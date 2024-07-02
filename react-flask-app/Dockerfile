# Stage 1: Build React app
FROM node:16 AS build

WORKDIR /app

# Copy package.json and yarn.lock and install dependencies
COPY package.json yarn.lock ./
RUN yarn install

# Copy the rest of the React application and build the React app
COPY . ./
RUN yarn build

# Stage 2: Setup Flask app and run both Flask and React
FROM python:3.9-slim

# Install Node.js and Yarn
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && curl -fsSL https://deb.nodesource.com/setup_16.x | bash - \
    && apt-get install -y nodejs \
    && curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - \
    && echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list \
    && apt-get update && apt-get install -y --no-install-recommends yarn \
    && apt-get install -y bash \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the Flask app requirements and install them
COPY server/requirements.txt ./
RUN python -m venv /app/venv && \
    /app/venv/bin/pip install --no-cache-dir -r requirements.txt && \
    rm -rf /root/.cache/pip

# Install concurrently to run multiple commands
RUN yarn global add concurrently

# Copy the Flask app
COPY server /app/server

# Copy the React build from the first stage
COPY --from=build /app/build /app/static

# Copy the rest of the application
COPY . /app

# Copy the .env file from home directory to the container
COPY /home/student24/.env /app/.env

# Expose the ports for Flask and React
EXPOSE 3000
EXPOSE 5000

# Use bash to source the virtual environment, export env variables, and start the app
CMD ["bash", "-c", "source /app/venv/bin/activate && export $(cat /app/.env | xargs) && cd /app && concurrently \"yarn start\" \"yarn start-api\""]
