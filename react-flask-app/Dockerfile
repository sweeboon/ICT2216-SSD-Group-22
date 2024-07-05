# Stage 1: Build React app
FROM node:14 as build-react
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Setup Flask app
FROM python:3.11-slim as build-flask
WORKDIR /usr/src/app
COPY --from=build-react /usr/src/app /usr/src/app
RUN apt-get update && apt-get install -y curl gnupg && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs npm && \
    npm install -g yarn && \
    apt-get clean
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate && pip install --upgrade pip && pip install -r /usr/src/app/server/requirements.txt"

# Set environment variables
ENV FLASK_APP=server.api
ENV NODE_OPTIONS=--openssl-legacy-provider

# Expose the ports
EXPOSE 5000
EXPOSE 3000

# Copy start.sh script from the src directory and make it executable
COPY src/start.sh /usr/src/app/start.sh
RUN chmod +x /usr/src/app/start.sh

# Debug step to list directory contents
RUN ls -l /usr/src/app/
RUN ls -l /usr/src/
RUN cat /usr/src/app/start.sh

# Start the Flask and React app
CMD ["/bin/bash", "/usr/src/app/start.sh"]
