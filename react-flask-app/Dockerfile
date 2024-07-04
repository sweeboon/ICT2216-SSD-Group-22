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
RUN python -m venv venv
RUN /bin/bash -c ". venv/bin/activate && pip install --upgrade pip && pip install -r /usr/src/app/server/requirements.txt"

# Expose the ports
EXPOSE 5000
EXPOSE 3000

# Start the Flask and React app
CMD ["/bin/bash", "-c", "cd /usr/src/app && . venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & npm start --prefix /usr/src/app"]
