FROM nginx:latest

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg python3 python3-venv python3-pip wget && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs npm && \
    curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && \
    apt-get install -y yarn && \
    apt-get clean

# Copy your application code
COPY . /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Debug: List contents of /usr/src/app before creating the virtual environment
RUN ls -al /usr/src/app
RUN ls -al /usr/src/app/server

# Install Python dependencies within a virtual environment
RUN python3 -m venv /usr/src/app/server/venv && \
    ls -al /usr/src/app/server/venv && \
    /usr/src/app/server/venv/bin/pip install --upgrade pip && \
    /usr/src/app/server/venv/bin/pip install -r /usr/src/app/server/requirements.txt --break-system-packages

# Debug: Verify the virtual environment directory
RUN ls -al /usr/src/app/server/venv
RUN ls -al /usr/src/app/server/venv/bin

# Install Node.js dependencies
RUN cd /usr/src/app/src && yarn install

# Build the React app with legacy OpenSSL provider
RUN cd /usr/src/app/src && NODE_OPTIONS=--openssl-legacy-provider yarn build

# Expose the ports
EXPOSE 80 443 5000 3000

# Start the application
CMD /bin/bash -c "nginx && \
    cd /usr/src/app/server && . venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & \
    cd /usr/src/app/src && yarn start --port 3000"
