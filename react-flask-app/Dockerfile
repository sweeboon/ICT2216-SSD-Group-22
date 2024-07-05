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

RUN chmod -R 755 /usr/src/app



# Combine the commands to activate the virtual environment and start the React app
ENTRYPOINT ["sh", "-c", "cd /usr/src/app/server && . venv/bin/activate && cd /usr/src/app"]

# Use CMD to start the React app
CMD ["yarn", "start"]