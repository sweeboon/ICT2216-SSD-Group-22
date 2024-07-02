# Stage 1: Build React app
FROM node:14 AS build

WORKDIR /app
COPY package.json yarn.lock ./
RUN yarn install
COPY . .
RUN yarn build

# Stage 2: Set up backend with virtual environment and copy built frontend
FROM python:3.8-slim

WORKDIR /app

# Install Node.js for yarn build
RUN apt-get update && \
    apt-get install -y curl && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs && \
    npm install -g yarn

# Create virtual environment
RUN python -m venv venv
ENV PATH="/app/venv/bin:$PATH"

# Install backend dependencies
COPY server/requirements.txt ./
RUN /bin/bash -c "source venv/bin/activate && pip install -r requirements.txt"

# Copy backend code
COPY server/ ./

# Run Flask migrations
RUN /bin/bash -c "source venv/bin/activate && flask db migrate"

# Copy built frontend from the previous stage
COPY --from=build /app/build ./frontend/build

# Expose the port the backend runs on
EXPOSE 5000

# Command to run the application
CMD ["/bin/bash", "-c", "source venv/bin/activate && yarn start"]
