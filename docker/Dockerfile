FROM python:3.11-alpine

WORKDIR /app

COPY ./docker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY customers_manager/ .

EXPOSE 8001

CMD ["uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]