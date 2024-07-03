# Use the official Nginx image as a base
FROM nginx:latest

# Install necessary dependencies
RUN apt-get update && \
    apt-get install -y curl gnupg python3 python3-venv python3-pip wget && \
    curl -sL https://deb.nodesource.com/setup_14.x | bash - && \
    apt-get install -y nodejs npm && \
    curl -sL https://dl.yarnpkg.com/debian/pubkey.gpg | gpg --dearmor | tee /usr/share/keyrings/yarnkey.gpg >/dev/null && \
    echo "deb [signed-by=/usr/share/keyrings/yarnkey.gpg] https://dl.yarnpkg.com/debian stable main" | tee /etc/apt/sources.list.d/yarn.list && \
    apt-get update && \
    apt-get install -y yarn

# Copy your application code
COPY . /usr/src/app

# Set the working directory
WORKDIR /usr/src/app

# Install Python dependencies within a virtual environment
RUN python3 -m venv /usr/src/app/server/venv && \
    /usr/src/app/server/venv/bin/python -m ensurepip --upgrade && \
    /usr/src/app/server/venv/bin/pip install --upgrade pip && \
    /usr/src/app/server/venv/bin/pip install -r /usr/src/app/server/requirements.txt --break-system-packages

# Install Node.js dependencies
RUN cd /usr/src/app/src && yarn install

# Expose the ports
EXPOSE 80 443

# Start the application
CMD /bin/bash -c "nginx && \
    cd /usr/src/app/server && . venv/bin/activate && flask run --host=0.0.0.0 --port=5000 & \
    cd /usr/src/app/src && yarn start --port 3000"
