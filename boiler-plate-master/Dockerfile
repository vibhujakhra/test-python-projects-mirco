# base image
FROM python:3.8

#maintainer
LABEL Author="Gagandeep"

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONBUFFERED 1

#directory to store app source code
RUN mkdir /code

#directory to store app related logs
RUN mkdir -p /var/log/renewbuy

#switch to /app directory so that everything runs from here
WORKDIR /code

#let pip install required packages
ADD requirements.txt .
RUN pip install -r requirements.txt

#copy the app code to image working directory
COPY . /code
