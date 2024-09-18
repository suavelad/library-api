# Pull official base image 
FROM --platform=amd64 python:3.11-slim

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Create the working directory
RUN mkdir /app
RUN mkdir /app/staticfiles
# Set working directory
WORKDIR /app

# Install base dependencies
RUN apt-get update && apt update 
RUN apt  install -y  libpng-dev  

# Set up a venv
# This is needed to build on the production server, because if we attempt
# to build in the global docker image environment, pip will find injected Datadog
# APM python packages, attempt to uninstall them in the pip install process, and crash.
# ENV VIRTUAL_ENV=/app/venv
# RUN python3 -m venv $VIRTUAL_ENV
# ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# COPY pyproject.toml poetry.lock /app/


# RUN pip install poetry
#RUN poetry config virtualenvs.create false
# Install dependencies
# RUN poetry install
RUN pip install --upgrade pip
# RUN pip install croniter


ADD requirements.txt /app/
RUN pip install -r requirements.txt

# Copy entrypoint.sh
# COPY ./entrypoint.sh /entrypoint.sh

# RUN chmod +x /entrypoint.sh
COPY ./ /app

EXPOSE 8002

CMD ["python", "manage.py", "runserver", "0.0.0.0:8002"]

# ENTRYPOINT [ "/entrypoint.sh" ]