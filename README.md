# n8n Webhook Microservice

A robust, asynchronous webhook microservice built with FastAPI to integrate with n8n workflows.

## Features

- **Webhook Endpoint**: Secure endpoint for receiving webhooks from n8n or any HTTP client
- **Authentication**: API key authentication via `Authorization` header
- **HMAC Verification**: Optional HMAC-SHA256 signature verification
- **Idempotency**: Prevent duplicate processing using `X-Idempotency-Key`
- **Background Processing**: Async task processing with retries
- **Callback Notifications**: Send results to callback URLs
- **Docker Support**: Ready-to-run containerized environment
- **Health Checks**: `/health` endpoint for monitoring
- **Comprehensive Tests**: 90%+ test coverage

## Getting Started

### Prerequisites

- Python 3.11+
- Docker (optional)
- Redis (optional)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/n8n-webhook-service.git
   cd n8n-webhook-service