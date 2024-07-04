# Stage 1: Build React app
FROM node:14 as build-react
WORKDIR /usr/src/app
COPY react-flask-app/package*.json ./
RUN npm install
COPY react-flask-app ./
RUN npm run build

# Stage 2: Setup Flask app
FROM python:3.11-slim as build-flask
WORKDIR /usr/src/app
COPY react-flask-app/server ./
RUN python -m venv venv
RUN . venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt

# Stage 3: Final setup with nginx
FROM nginx:alpine
COPY --from=build-react /usr/src/app/build /usr/share/nginx/html
COPY --from=build-flask /usr/src/app /usr/src/app
COPY react-flask-app/nginx.conf /etc/nginx/nginx.conf

# Run Flask app
CMD ["sh", "-c", ". /usr/src/app/venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & nginx -g 'daemon off;'"]

EXPOSE 80
EXPOSE 443
EXPOSE 5000
