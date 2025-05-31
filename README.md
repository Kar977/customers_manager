# customers_manager

`customers_manager` is a microservice responsible for handling customer-related operations in the **BarberShop API** platform. It manages customer profiles, appointment bookings, and emits asynchronous events for notifications.

This service is part of a distributed microservices system and communicates exclusively through the [`gateway_barbershop`](https://github.com/Kar977/gateway_barbershop).

## Features

- Customer profile creation and retrieval  
- Appointment booking and history  
- Emits booking confirmation events to `notification_manager` via RabbitMQ  
- Uses isolated PostgreSQL database  
- Protected by JWT authentication (validated by the API Gateway)

## Technologies

- Python 3.11  
- FastAPI 0.111.0
- PostgreSQL 15  
- Docker Docker 24.0.7
- Pydantic 2.7  
- Httpx 0.27  
- Pytest  8.3.5 / Pytest-asyncio 0.26.0  
- Pika (RabbitMQ client)  
- Uvicorn 0.30.1

## Environment Variables / Secrets

The following secrets are required (via GitHub Secrets or a local `.env` file):
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_ACCOUNT_ID`
- `POSTGRES_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST`, `POSTGRES_PORT`

## ⚙️ Local Development
1. **Clone the repository**
   ```
   git clone https://github.com/Kar977/customers_manager.git
   cd customers_manager
   ```
2. **Build and run using Docker**
   ```
   docker build -t customers_manager .
   docker run --env-file .env -p 8001:8001 customers_manager

   ```
   The service will be available at:
   `http://localhost:8001`

>In production, the service is accessible only through the API Gateway.
