# Use an official Node.js runtime as a parent image for building the app
FROM node:14 as build

# Set the working directory
WORKDIR /app

# Copy package.json and yarn.lock and install frontend dependencies
COPY react-flask-app/src/package.json react-flask-app/src/yarn.lock ./
RUN yarn install

# Copy the rest of the application and build the app
COPY . .
RUN yarn build --cwd react-flask-app/src

# Use the existing Nginx image to serve the built application
FROM nginx:alpine

# Copy the build output to the Nginx html directory
COPY --from=build /app/react-flask-app/src/build /usr/share/nginx/html

# Copy Nginx configuration file
COPY react-flask-app/src/nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
