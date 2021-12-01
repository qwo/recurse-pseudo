FROM python:alpine 

LABEL maintainer="Stanley Zheng"

# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.7-slim

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt
RUN pip install Flask gunicorn

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.

ENV PORT 8080

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
