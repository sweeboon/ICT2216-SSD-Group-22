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

# Copy React build files from the first stage
COPY --from=build-react /usr/src/app/build ./frontend/build
COPY --from=build-react /usr/src/app/package*.json ./
COPY --from=build-react /usr/src/app/yarn.lock ./
COPY --from=build-react /usr/src/app/public ./public

# Install system dependencies and Python virtual environment
RUN apt-get update && apt-get install -y bash curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs npm && \
    npm install -g yarn && \
    apt-get clean

# Copy the Flask app code
COPY ./server ./server

# Create and activate virtual environment in the /usr/src/app/server directory, install dependencies
RUN cd /usr/src/app/server && \
    python -m venv venv && \
    /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Set environment variables
ENV FLASK_APP=server.api
ENV NODE_OPTIONS=--openssl-legacy-provider

# Expose the ports on which the apps will run
EXPOSE 5000
EXPOSE 3000

# Install Node.js dependencies for the React app
RUN yarn install

# Debug step: verify venv and directory contents
RUN ls -l /usr/src/app/
RUN ls -l /usr/src/app/server/venv/bin && \
    ls -l /usr/src/app/server
RUN ls -l /usr/src/app/src/
# Create a startup script
RUN echo '#!/bin/bash\ncd /usr/src/app/server\nsource venv/bin/activate\ncd /usr/src/app\nyarn start\n' > /usr/src/app/start.sh

# Verify the startup script
RUN ls -l /usr/src/app/start.sh && cat /usr/src/app/start.sh
RUN ls -l /usr/src/app/src/
RUN ls -l /usr/src/app/src/index.js
RUN chmod +x /usr/src/app/start.sh

# Start both Flask and React apps using the startup script
CMD ["/bin/bash", "-c", "/usr/src/app/start.sh"]
