FROM python:3.13-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python

USER python
RUN /usr/local/bin/python -m venv /home/python/venv

COPY --chown=python:python requirements.txt /home/python/hoth/requirements.txt
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/hoth/requirements.txt
