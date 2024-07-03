# Use the official base image with Node.js 16
FROM node:16

# Set the working directory
WORKDIR /usr/src/app

# Copy the package.json and yarn.lock files
COPY package*.json yarn.lock ./

# Install Node.js dependencies
RUN yarn install

# Copy the rest of the application code
COPY . .

# Install dependencies and Python 3.8 on Debian Buster
RUN apt-get update && \
    apt-get install -y \
    python3.8 \
    python3.8-venv \
    python3.8-dev \
    python3-pip \
    build-essential \
    libssl-dev \
    libffi-dev

# Verify the files are in the expected locations
RUN ls -l /usr/src/app/server/

# Create and activate a virtual environment with Python 3.8
RUN python3.8 -m venv /usr/src/app/server/venv
RUN /usr/src/app/server/venv/bin/pip install --upgrade pip
RUN /usr/src/app/server/venv/bin/pip install --no-cache-dir -r /usr/src/app/server/requirements.txt

# Expose ports
EXPOSE 3000 5000

# Start the application using concurrently
CMD ["npx", "concurrently", "\"yarn start\"", "\"cd server && ../venv/bin/flask run --host=0.0.0.0 --port=5000\""]
