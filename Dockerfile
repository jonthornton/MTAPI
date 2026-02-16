FROM python:3.11-slim

WORKDIR /app

ARG CONFIGFILE=settings.cfg.sample

COPY . .

RUN cp ${CONFIGFILE} settings.cfg

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]