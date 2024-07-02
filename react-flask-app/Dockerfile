# Stage 1: Build React app
FROM node:16 as build

# Set the working directory
WORKDIR /app

# Copy package.json and yarn.lock and install dependencies
COPY package.json yarn.lock ./
RUN yarn install

# Copy the rest of the React application and build the React app
COPY . ./
RUN yarn build

# Stage 2: Setup Flask app and run both Flask and React
FROM python:3.9

# Install yarn globally and clean up
RUN apt-get update && apt-get install -y curl && \
    curl -sS https://dl.yarnpkg.com/debian/pubkey.gpg | apt-key add - && \
    echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && apt-get install -y yarn && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy the Flask app requirements and install them
COPY server/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install concurrently to run multiple commands
RUN yarn global add concurrently

# Copy the Flask app
COPY server /app/server

# Copy the React build from the first stage
COPY --from=build /app/build /app/static

# Copy the rest of the application
COPY . /app

# Expose the ports for Flask and React
EXPOSE 3000
EXPOSE 5000

# Start both the React and Flask app using concurrently
CMD ["concurrently", "\"react-scripts start\"", "\"yarn start-api\""]
