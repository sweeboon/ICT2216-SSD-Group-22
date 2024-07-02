# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Set environment variables
ENV VIRTUAL_ENV=/app/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r react-flask-app/server/requirements.txt

# Install Node.js and Yarn
RUN apt-get update && apt-get install -y curl gnupg
RUN curl -sL https://deb.nodesource.com/setup_14.x | bash -
RUN apt-get install -y nodejs
RUN npm install --global yarn

# Install frontend dependencies
RUN cd react-flask-app/src && yarn install

# Expose port
EXPOSE 5000

# Run the application
CMD ["bash", "-c", ". venv/bin/activate && flask db upgrade && yarn start"]
