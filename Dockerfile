FROM python:3-alpine

WORKDIR /app
COPY requirements.txt /app
RUN --mount=type=cache,target=/root/.cache/pip pip3 install -r requirements.txt

# install gunicorn production server
RUN --mount=type=cache,target=/root/.cache/pipu pip3 install gunicorn

COPY . /app

# put your settings.cfg in here
RUN mkdir /config
RUN ln -s /config/settings.cfg /app/settings.cfg

EXPOSE 8000
CMD ["gunicorn", "-c", "gunicorn.py", "app:app"]
