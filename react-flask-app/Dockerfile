# Stage 1: Build React app
FROM node:16 as build-react
WORKDIR /usr/src/app
COPY package*.json ./
# Copy everything from the context
COPY . .
# Install dependencies and build the React app
RUN npm install
RUN npm run build
RUN ls -l /usr/src/app/
# Stage 2: Setup Flask app
FROM python:3.13.0rc1-slim as build-flask
WORKDIR /usr/src/app

# Copy the entire app directory from the build stage
COPY --from=build-react /usr/src/app /usr/src/app

# Install system dependencies and Python virtual environment
RUN apt-get update && apt-get install -y bash curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs npm && \
    npm install -g yarn && \
    apt-get clean
# Copy the Flask app code
COPY ./server ./server

# Ensure .env file is included
COPY ./server/.env /usr/src/app/server/.env


# Create and activate virtual environment, install dependencies
RUN cd /usr/src/app/server && \
    python -m venv venv && \
    /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Set environment variables
ENV FLASK_APP=wsgi.py
ENV NODE_OPTIONS=--openssl-legacy-provider

# Expose the ports on which the apps will run
EXPOSE 5000
EXPOSE 3000

# Install Node.js dependencies for the React app
RUN yarn install


# Create a startup script
RUN echo '#!/bin/bash\n' \
    'cd /usr/src/app/server\n' \
    '. venv/bin/activate\n' \
    'flask db upgrade\n' \
    'cd /usr/src/app\n' \
    'yarn start\n' > /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Verify the directory contents
RUN ls -l /usr/src/app/
RUN ls -l /usr/src/app/server/
RUN ls -l /usr/src/app/server/venv/bin

# Start both Flask and React apps using the startup script
CMD ["/bin/bash", "/usr/src/app/start.sh"]
