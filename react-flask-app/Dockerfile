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
RUN . venv/bin/activate && pip install --upgrade pip && pip install -r /usr/src/app/server/requirements.txt

# Stage 3: Final setup with nginx
FROM nginx:alpine
COPY --from=build-react /usr/src/app/build /usr/share/nginx/html
COPY --from=build-flask /usr/src/app /usr/src/app
COPY nginx.conf /etc/nginx/nginx.conf

# Run Flask app
CMD /bin/bash -c "nginx && \
    cd /usr/src/app/server && . /usr/src/app/venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & \
    cd /usr/src/app && yarn start --port 3000"

EXPOSE 80
EXPOSE 443
EXPOSE 5000
