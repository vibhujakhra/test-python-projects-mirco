# python base image + all requirements
FROM registry.gitlab.renewbuy.in/sleep/go-pybentobox:latest

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONBUFFERED 1

#directory to store app source code
RUN mkdir /code

#directory to store app related logs
RUN mkdir -p /var/log/sleep/

#switch to /app directory so that everything runs from here
WORKDIR /code

#copy the app code to image working directory
COPY . /code
