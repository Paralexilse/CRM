FROM python:3.13-alpine
RUN pip install --upgrade pip
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev
ENV PYTHONBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app/www/crm
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . . 