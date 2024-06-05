#Change the below  line with the official docker image of your organisation.
# It should look like - 'FROM artifactory.<myCompany>.com:8443/<company-python-image>:<version>'
FROM python:3.10


USER root

WORKDIR /app

COPY . .
COPY  install-pythondependencies requirements.txt /usr/local/sbin/
RUN python3 -m venv /venv
RUN install-pythondependencies
ENV PATH="/venv/bin:$PATH"
VOLUME /genaidata
EXPOSE 5000/tcp

CMD ["gunicorn","--config", "src/config/gunicorn_config.py", "app:app"]

