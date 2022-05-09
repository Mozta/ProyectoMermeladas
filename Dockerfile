FROM python:3.10-slim

RUN apt-get update -y

COPY . /app
WORKDIR /app

ENV PORT 8080
ENV HOST 0.0.0.0

RUN pip install --no-cache-dir -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]