import logging
import uuid
from fastapi import FastAPI, Request, BackgroundTasks, HTTPException, status
from fastapi.responses import JSONResponse
from app import models, worker, storage
from app.auth import verify_api_key, verify_signature, InvalidSignatureError
from app.config import settings
from app.utils import setup_logging

setup_logging()
logger = logging.getLogger(__name__)
app = FastAPI()

@app.middleware("http")
async def add_correlation_id(request: Request, call_next):
    corr_id = request.headers.get("X-Correlation-Id", str(uuid.uuid4()))
    logging.info(f"Request started", path=request.url.path, correlation_id=corr_id)
    
    response = await call_next(request)
    
    response.headers["X-Correlation-Id"] = corr_id
    logging.info(f"Request completed", status_code=response.status_code, correlation_id=corr_id)
    return response

@app.post("/webhook", response_model=models.WebhookResponse)
async def webhook_endpoint(
    request: Request,
    background_tasks: BackgroundTasks,
    data: models.WebhookRequest
):
    # Authentication
    verify_api_key(request)
    
    # Signature verification
    body = await request.body()
    try:
        verify_signature(request, body)
    except InvalidSignatureError as e:
        logging.warning("Invalid signature", detail=str(e.detail))
        raise e
    
    # Idempotency check
    idempotency_key = request.headers.get("X-Idempotency-Key")
    if idempotency_key:
        if await storage.check_idempotency(idempotency_key):
            logging.info("Duplicate request", idempotency_key=idempotency_key)
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={"status": "duplicate", "job_id": "", "message": "Request already processed"}
            )
        await storage.set_idempotency(idempotency_key)
    
    # Create job
    job_id = str(uuid.uuid4())
    background_tasks.add_task(
        worker.process_webhook_task,
        data.model_dump(),
        job_id,
        data.callback_url
    )
    
    logging.info("Request accepted", job_id=job_id)
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "job_id": job_id,
            "message": "Processing in background"
        }
    )

@app.post("/run-task", response_model=models.WebhookResponse)
async def run_task_directly(
    request: Request,
    background_tasks: BackgroundTasks,
    data: models.WebhookRequest
):
    verify_api_key(request)
    job_id = str(uuid.uuid4())
    background_tasks.add_task(
        worker.process_webhook_task,
        data.model_dump(),
        job_id,
        data.callback_url
    )
    logging.info("Direct task started", job_id=job_id)
    return JSONResponse(
        status_code=status.HTTP_202_ACCEPTED,
        content={
            "status": "accepted",
            "job_id": job_id,
            "message": "Processing in background"
        }
    )

@app.get("/health", response_model=models.HealthResponse)
async def health_check():
    return {"status": "OK"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.error("HTTP Exception", status_code=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logging.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )