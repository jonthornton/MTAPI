FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN test -f settings.cfg || (echo "Error: settings.cfg not found" && exit 1)

RUN pip install -r requirements.txt

EXPOSE 5000

CMD ["python", "app.py"]